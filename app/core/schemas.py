from datetime import datetime


class IdMixin:
    id: int


class CreatedUpdatedMixin:
    created: datetime | None = None
    updated: datetime | None = None
