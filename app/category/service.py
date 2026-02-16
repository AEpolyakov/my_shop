from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.category.models import Category
from app.category.schemas import CategoryCreateSchema, CategoryUpdateSchema
from app.core.crud import CRUDBase


class CategoryService(CRUDBase[Category, CategoryCreateSchema, CategoryUpdateSchema]):
    pass

    async def get_or_create_by_name(self, category_name: str, db: AsyncSession) -> Category:
        category = await db.scalar(select(Category).where(Category.name == category_name))

        if not category:
            category = await self.create(CategoryCreateSchema(name=category_name), db)

        return category


category_service = CategoryService(Category)
