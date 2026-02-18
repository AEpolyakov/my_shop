from typing import Generic, Type

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, delete, func, Select, asc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from typing_extensions import TypeVar

from app.core.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_one(self, item_id: int, db: AsyncSession) -> ModelType | None:

        obj = (await db.execute(self.base_select.where(self.model.id == item_id))).scalar()
        if obj is None:
            raise HTTPException(status_code=404, detail=f"item id={item_id} from {self.model.__tablename__} not found")

        return obj

    async def get_many(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> dict:

        results = (await db.scalars(self.base_select.offset(skip).limit(limit).order_by(asc(self.model.id)))).all()
        total = (await db.execute(select(func.count()).select_from(self.model))).scalar_one()

        return {
            "results": results,
            "total": total,
        }

    async def create(self, obj: CreateSchemaType, db: AsyncSession) -> ModelType:

        new_obj = self.model(**jsonable_encoder(obj))
        db.add(new_obj)
        await db.commit()

        return new_obj

    async def delete(self, db: AsyncSession, item_id: int) -> None:

        obj = (await db.execute(delete(self.model).where(self.model.id == item_id).returning(self.model))).scalar()

        if not obj:
            raise HTTPException(status_code=404, detail=f"item id={item_id} not found")

        await db.commit()

        return obj

    async def update(self, db: AsyncSession, item_id: int, new_obj_schema: UpdateSchemaType) -> ModelType:

        old_obj = await self.get_one(item_id, db)
        update_data = jsonable_encoder(new_obj_schema)

        for field in update_data:
            setattr(old_obj, field, update_data[field])

        db.add(old_obj)
        await db.commit()

        return old_obj

    @property
    def base_select(self) -> Select:
        return select(self.model)
