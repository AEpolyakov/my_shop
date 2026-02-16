from pydantic import BaseModel

from app.core.schemas import IdMixin, CreatedUpdatedMixin


class CategoryCreateSchema(BaseModel):
    name: str


class CategoryUpdateSchema(CategoryCreateSchema, IdMixin, CreatedUpdatedMixin):
    pass
