from datetime import datetime


class IdMixin:
    id: int | None = None


class CreatedUpdatedMixin:
    created: datetime | None = None
    updated: datetime | None = None
