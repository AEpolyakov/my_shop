from pydantic import BaseModel


class Message(BaseModel):
    topic: str
    content: str
    partition_key: str | None = None


class ConsumerStatus(BaseModel):
    running: bool
    topic: str
    group_id: str
    auto_commit: bool
    partitions: list[dict] | None = None
