from sqlalchemy import Select, select
from sqlalchemy.orm import joinedload

from app.core.crud import CRUDBase
from app.product.models import Product
from app.product.schemas import ProductCreateSchema, ProductUpdateSchema


class ProductService(CRUDBase[Product, ProductCreateSchema, ProductUpdateSchema]):

    @property
    def base_select(self) -> Select:
        return select(Product).options(joinedload(Product.category))


product_service = ProductService(Product)
