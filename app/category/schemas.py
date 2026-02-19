from pydantic import BaseModel

from app.core.schemas import ResponseModel


class CategoryCreateSchema(BaseModel):
    name: str


class CategoryUpdateSchema(CategoryCreateSchema):
    pass


class CategoryResponseSchema(CategoryUpdateSchema, ResponseModel):
    pass


class CategoryListResponseSchema(BaseModel):
    results: list[CategoryResponseSchema]
    total: int
