from fastapi import FastAPI

from app.product.router import product_router
from app.health import health_router

app = FastAPI()

app.include_router(health_router)
app.include_router(product_router)
