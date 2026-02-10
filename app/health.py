from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.session import get_db

health_router = APIRouter()


@health_router.get("/health_db")
async def test_endpoint(db: Session = Depends(get_db)):
    return {"message": "API is working"}


@health_router.get("/health")
async def health():
    return {"status": "ok"}
