from typing import Generic, Type

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
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

        obj = db.query(self.model).get(item_id)
        if obj is None:
            raise HTTPException(status_code=404, detail=f"{self.model} id={item_id} not found")

        return obj

    def get_many(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[ModelType]:

        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj: CreateSchemaType, db: Session) -> ModelType:

        new_obj = self.model(**jsonable_encoder(obj))
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)

        return db.add(obj)

    def delete(self, db: Session, item_id: int) -> ModelType:

        obj = self.get_one(item_id, db)
        obj.delete()
        db.commit()

        return obj

    def update(self, db: Session, item_id: int, new_obj_schema: UpdateSchemaType) -> ModelType:

        old_obj = self.get_one(item_id, db)

        new_obj_dict = jsonable_encoder(new_obj_schema)
        for field in old_obj:
            if field in new_obj_dict and new_obj_dict[field] != old_obj[field]:
                setattr(old_obj, field, new_obj_dict[field])

        new_obj = self.model(**jsonable_encoder(old_obj))
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)

        return new_obj
