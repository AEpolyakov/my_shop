from pydantic import BaseModel

from app.core.schemas import IdMixin, CreatedUpdatedMixin


class ProductCreateSchema(BaseModel):
    name: str
    price: float


class ProductUpdateSchema(ProductCreateSchema, IdMixin, CreatedUpdatedMixin):
    pass
