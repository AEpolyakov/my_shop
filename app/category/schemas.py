from pydantic import BaseModel


class CategoryCreateSchema(BaseModel):
    name: str


class CategoryUpdateSchema(CategoryCreateSchema):
    pass
