from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.product.schemas import ProductCreateSchema, ProductUpdateSchema
from app.product.service import product_service
from app.core.session import get_db

product_router = APIRouter(prefix="/products", tags=["products"])


@product_router.get("/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    return await product_service.get_one(product_id, db)


@product_router.get("/")
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return await product_service.get_many(db, skip, limit)


@product_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreateSchema, db: Session = Depends(get_db)):
    return await product_service.create(product, db)


@product_router.put("/{product_id}")
async def update_product(product: ProductUpdateSchema, product_id: int, db: Session = Depends(get_db)):
    return await product_service.update(db, product_id, product)


@product_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    return await product_service.delete(db, product_id)
