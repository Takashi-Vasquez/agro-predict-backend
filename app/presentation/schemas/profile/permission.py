from pydantic import ConfigDict, Field

from app.presentation.schemas import BaseReadSchema


class PermissionRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    code: str = Field(alias="code")
    name: str = Field(alias="name")
