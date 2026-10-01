from uuid import UUID

from pydantic import BaseModel

class UploadErrorRecord(BaseModel):
    row: int
    error: str
    model_config = {"extra": "allow"}
    source: str | None = None
    import_batch_id: UUID | None = None
    status: str | None = None


class UploadResult(BaseModel):
    total: int
    has_errors: bool
    records: list[UploadErrorRecord] | None = None
    batch_id: str | None = None
    saved: int | None = None