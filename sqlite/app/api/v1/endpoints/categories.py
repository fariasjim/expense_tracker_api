import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from app.db import get_db, redis_client
from app.models.schemas import Category, UserRole
from app.api.deps import RoleChecker

router = APIRouter(prefix="/categories", tags=["Catalog Hierarchy"])
require_admin = RoleChecker([UserRole.ADMIN])


class CategoryCreate(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True


async def get_all_descendant_ids(parent_id: int, db: AsyncSession) -> List[int]:
    descendant_ids = []

    async def dfs(current_id: int):
        statement = select(Category.id).where(Category.parent_id == current_id)
        result = await db.execute(statement)
        child_ids = result.scalars().all()
        for child_id in child_ids:
            descendant_ids.append(child_id)
            await dfs(child_id)

    await dfs(parent_id)
    return descendant_ids


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    slug_statement = select(Category).where(Category.slug == payload.slug)
    slug_check = await db.execute(slug_statement)
    if slug_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parent category not found"
        )
    new_category = Category(
        name=payload.name, slug=payload.slug, parent_id=payload.parent_id
    )
    try:
        await redis_client.delete(f"category_tree:{payload.parent_id}")
    except Exception:
        pass
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category


@router.get("", response_model=List[CategoryResponse])
async def list_all_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    return result.scalars().all()


@router.get("/{category_id}/subcategories", response_model=List[int])
async def get_subcategory_tree(category_id: int, db: AsyncSession = Depends(get_db)):
    base_cat = await db.get(Category, category_id)
    if not base_cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target category not found"
        )
    cache_key = f"category_tree:{category_id}"
    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
    except Exception:
        pass
    descendants = await get_all_descendant_ids(category_id, db)
    try:
        await redis_client.setex(cache_key, 3600, json.dumps(descendants))
    except Exception:
        pass
    return descendants
