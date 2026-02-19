from fastapi import FastAPI

from app.cart.router import cart_router
from app.category.router import category_router
from app.product.router import product_router
from app.health import health_router

app = FastAPI()

app.include_router(health_router)
app.include_router(product_router)
app.include_router(category_router)
app.include_router(cart_router)
