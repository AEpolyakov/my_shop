from dataclasses import dataclass
from typing import Type

from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.crud import CRUDBase
from app.core.session import get_db


@dataclass
class CrudRouterTypes:
    create: Type[BaseModel]
    update: Type[BaseModel]
    response: Type[BaseModel]
    response_list: Type[BaseModel]


def create_crud_router(prefix: str, tags: list[str], service: CRUDBase, types: CrudRouterTypes) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("/{item_id}", response_model=types.response)
    async def get_one(item_id: int, db: AsyncSession = Depends(get_db)):
        return await service.get_one(item_id, db)

    @router.get("/", response_model=types.response_list)
    async def get_many(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
        return await service.get_many(db, skip, limit)

    @router.post("/", status_code=status.HTTP_201_CREATED, response_model=types.response)
    async def create(item: types.create = Body(), db: AsyncSession = Depends(get_db)):
        return await service.create(item, db)

    @router.put("/{item_id}", response_model=types.response)
    async def update(item_id: int, item: types.update = Body(), db: AsyncSession = Depends(get_db)):
        return await service.update(db, item_id, item)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete(item_id: int, db: AsyncSession = Depends(get_db)):
        return await service.delete(db, item_id)

    return router
