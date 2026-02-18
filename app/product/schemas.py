from pydantic import BaseModel

from app.category.schemas import CategoryCreateSchema


class ProductCreateSchema(BaseModel):
    name: str
    price: float
    category_id: int | None = None
    category: CategoryCreateSchema | None = None


class ProductUpdateSchema(ProductCreateSchema):
    pass
