from typing import Generic, Type

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException
from typing_extensions import TypeVar

from app.core.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_one(self, item_id: int, db: Session) -> ModelType | None:

        obj = db.execute(select(self.model).where(self.model.id == item_id)).scalar()
        if obj is None:
            raise HTTPException(status_code=404, detail=f"item id={item_id} from {self.model.__tablename__} not found")

        return obj

    def get_many(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[ModelType]:

        return db.scalars(select(self.model).offset(skip).limit(limit)).all()

    def create(self, obj: CreateSchemaType, db: Session) -> ModelType:

        new_obj = self.model(**jsonable_encoder(obj))
        db.add(new_obj)
        db.commit()
        # db.refresh(new_obj)

        return new_obj

    def delete(self, db: Session, item_id: int) -> None:

        obj = db.execute(delete(self.model).where(self.model.id == item_id).returning(self.model)).scalar()

        if not obj:
            raise HTTPException(status_code=404, detail=f"item id={item_id} not found")

        db.commit()

        return obj

    def update(self, db: Session, item_id: int, new_obj_schema: UpdateSchemaType) -> ModelType:

        old_obj = self.get_one(item_id, db)

        old_obj_dict = jsonable_encoder(old_obj)
        new_obj_dict = jsonable_encoder(new_obj_schema)

        for field in old_obj_dict:
            if field in new_obj_dict and new_obj_dict[field] != old_obj_dict[field]:
                old_obj_dict[field] = new_obj_dict[field]

        new_obj = self.model(**old_obj_dict)
        db.commit()

        return new_obj
