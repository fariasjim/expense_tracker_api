from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import col, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field
from app.db import get_db
from app.models.schemas import Product, Category, UserRole
from app.api.deps import RoleChecker
from app.api.v1.endpoints.categories import get_all_descendant_ids


router = APIRouter(prefix="/products", tags=["Product Catalog and Inventory"])
require_admin = RoleChecker([UserRole.ADMIN])


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0, description="Price must be greater than zero")
    stock: int = Field(gt=0, description="Stock must be greater than zero")
    category_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category_id: int

    class Config:
        from_attributes = True


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    category = await db.get(Category, payload.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target cateogory not found."
        )
    new_product = Product(**payload.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


@router.get("", response_model=List[ProductResponse])
async def list_products(
    category_id: Optional[int] = None, db: AsyncSession = Depends(get_db)
):
    if category_id:
        base_category = await db.get(Category, category_id)
        if not base_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found"
            )
        descendant_ids = await get_all_descendant_ids(category_id, db)
        target_category_ids = [category_id] + descendant_ids
        statement = select(Product).where(
            col(Product.category_id).in_(target_category_ids)
        )
    else:
        statement = select(Product)
    result = await db.execute(statement)
    return result.scalars().all()


async def reduce_product_stock_safe(
    product_id: int, quantity: int, db: AsyncSession
) -> Product:
    statement = select(Product).where(Product.id == product_id).with_for_update()
    result = await db.execute(statement)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with product id {product_id} not foynd",
        )
    if product.stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock for '{product_id}'. Requested: {quantity}, Available: {product.stock}.",
        )
    product.stock -= quantity
    return product
