from pydantic import BaseModel

from app.category.schemas import CategoryCreateSchema
from app.core.schemas import IdMixin, CreatedUpdatedMixin


class ProductCreateSchema(BaseModel):
    name: str
    price: float
    category: CategoryCreateSchema | None = None


class ProductUpdateSchema(ProductCreateSchema, IdMixin, CreatedUpdatedMixin):
    category_id: int | None = None
