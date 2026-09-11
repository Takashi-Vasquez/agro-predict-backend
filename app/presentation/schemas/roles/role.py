from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema


class RoleBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class RoleRead(RoleBase, BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    status: str
    created_at: datetime
    updated_at: datetime
