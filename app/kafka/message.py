from pydantic import BaseModel


class Message(BaseModel):
    topic: str
    content: str
    partition_key: str | None = None
