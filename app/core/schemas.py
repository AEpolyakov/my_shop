from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer


class ResponseModel(BaseModel):
    id: int
    created: datetime
    updated: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created", "updated")
    def serialize_datetime(self, value: datetime, _info):
        return value.strftime("%Y-%m-%d %H:%M:%S")
