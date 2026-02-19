from app.category.schemas import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
    CategoryListResponseSchema,
    CategoryResponseSchema,
)
from app.category.service import category_service
from app.core.router import create_crud_router, CrudRouterTypes

category_router = create_crud_router(
    "/category",
    ["category"],
    category_service,
    CrudRouterTypes(
        CategoryCreateSchema,
        CategoryUpdateSchema,
        CategoryResponseSchema,
        CategoryListResponseSchema,
    ),
)
