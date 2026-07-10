import os
import sys
import asyncio

# Force local path configuration matching your working directory
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./shop.db"

from sqlmodel import select, SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import engine
from app.models.schemas import User, UserRole, Category, Product
from app.core.security import hash_password


async def seed_database():
    print("🌱 Initializing database schema and tables...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("📁 Database tables verified and created successfully.")

    print("🌱 Commencing data population...")
    async with AsyncSession(engine) as session:
        # 1. Seed Default Admin Account
        admin_email = "admin@shop.local"
        statement = select(User).where(User.email == admin_email)
        result = await session.execute(statement)
        existing_admin = result.scalar_one_or_none()

        if not existing_admin:
            admin_user = User(
                email=admin_email,
                hashed_password=hash_password("AdminSecurePass123!"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(admin_user)
            print("   ✅ Default Admin Profile Staged.")
        else:
            print("   ℹ️ Admin profile already exists. Skipping...")

        # 2. Seed Nested Catalog Structure
        tech_cat = Category(name="Electronics", slug="electronics", parent_id=None)
        session.add(tech_cat)
        await session.flush()

        phones_cat = Category(
            name="Smartphones", slug="smartphones", parent_id=tech_cat.id
        )
        session.add(phones_cat)
        await session.flush()

        # 3. Seed Compliant Products
        sample_products = [
            Product(
                sku="APPL-IPH15-PRO",
                name="iPhone 15 Pro",
                description="Flagship Apple smartphone with Titanium design.",
                price=999.99,
                stock=50,
                status="active",
                category_id=phones_cat.id,
            ),
            Product(
                sku="SAMS-GALX-S24",
                name="Samsung Galaxy S24",
                description="Premium Android device featuring advanced AI tools.",
                price=849.50,
                stock=35,
                status="active",
                category_id=phones_cat.id,
            ),
        ]

        for prod in sample_products:
            prod_statement = select(Product).where(Product.sku == prod.sku)
            prod_result = await session.execute(prod_statement)
            existing_prod = prod_result.scalar_one_or_none()
            if not existing_prod:
                session.add(prod)
                print(f"   📦 Product Staged: {prod.name} [{prod.sku}]")

        await session.commit()
        print("🚀 Seeding routine finalized successfully with zero errors!")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_database())

