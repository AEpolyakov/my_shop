from typing import Generic, Type, NoReturn

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, func, Select, asc
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

        obj = (await db.execute(self._base_select.where(self.model.id == item_id))).scalar()
        if obj is None:
            self.raise404(item_id, self.model.__tablename__)

        return obj

    @staticmethod
    def raise404(item_id: int, table_name: str) -> NoReturn:
        raise HTTPException(status_code=404, detail=f"item id={item_id} from {table_name} not found")

    async def get_many(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> dict:

        results = (await db.scalars(self._base_select.offset(skip).limit(limit).order_by(asc(self.model.id)))).all()
        total = (
            await db.execute(select(func.count()).where(self.model.deleted == False).select_from(self.model))
        ).scalar_one()

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

        obj = await self.get_one(item_id, db)
        obj.deleted = True

        db.add(obj)

        await db.commit()

        return obj

    async def update(self, db: AsyncSession, item_id: int, new_obj_schema: UpdateSchemaType) -> ModelType:

        old_obj = await self.get_one(item_id, db)
        update_data = jsonable_encoder(new_obj_schema)

        for field in update_data:
            setattr(old_obj, field, update_data[field])

        db.add(old_obj)
        await db.commit()
        await db.refresh(old_obj)

        return old_obj

    @property
    def base_select(self) -> Select:
        return select(self.model)

    @property
    def _base_select(self) -> Select:
        return self.base_select.where(self.model.deleted == False)
