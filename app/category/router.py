from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.category.schemas import CategoryCreateSchema
from app.category.service import category_service
from app.core.session import get_db

category_router = APIRouter(prefix="/category", tags=["category"])


@category_router.get("/")
async def get_categories(db: Session = Depends(get_db)):
    return await category_service.get_many(db)


@category_router.post("/")
async def create_category(category: CategoryCreateSchema, db: Session = Depends(get_db)):
    return await category_service.create(category, db)
