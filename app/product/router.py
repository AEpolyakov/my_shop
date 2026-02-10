from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.product.schemas import ProductCreateSchema
from app.product.service import product_service
from app.core.session import get_db

product_router = APIRouter(prefix="/products", tags=["products"])


@product_router.get("/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_service.get_one(product_id, db)


@product_router.get("/")
async def get_products(db: Session = Depends(get_db)):
    return product_service.get_many(db)


@product_router.post("/")
async def create_product(product: ProductCreateSchema, db: Session = Depends(get_db)):
    return product_service.create(product, db)
