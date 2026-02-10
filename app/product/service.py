from app.product.models import Product
from app.core.crud import CRUDBase
from app.product.schemas import ProductCreateSchema, ProductUpdateSchema


class ProductService(CRUDBase[Product, ProductCreateSchema, ProductUpdateSchema]):
    pass


product_service = ProductService(Product)
