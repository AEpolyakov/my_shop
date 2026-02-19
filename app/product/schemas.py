from pydantic import BaseModel

from app.category.schemas import CategoryCreateSchema
from app.core.schemas import ResponseModel


class ProductCreateSchema(BaseModel):
    name: str
    price: float
    category_id: int | None = None
    category: CategoryCreateSchema | None = None


class ProductUpdateSchema(ProductCreateSchema):
    pass


class ProductResponseSchema(ProductUpdateSchema, ResponseModel):
    pass


class ProductsResponseSchema(BaseModel):
    results: list[ProductResponseSchema]
    total: int
