from app.core.router import create_crud_router, CrudRouterTypes
from app.product.schemas import ProductsResponseSchema, ProductResponseSchema, ProductCreateSchema, ProductUpdateSchema
from app.product.service import product_service

product_router = create_crud_router(
    prefix="/products",
    tags=["products"],
    service=product_service,
    types=CrudRouterTypes(ProductCreateSchema, ProductUpdateSchema, ProductResponseSchema, ProductsResponseSchema),
)
