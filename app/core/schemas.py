from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResponseModel(BaseModel):
    id: int
    deleted: bool

    model_config = ConfigDict(from_attributes=True, json_encoders={datetime: lambda v: v.isoformat()})
