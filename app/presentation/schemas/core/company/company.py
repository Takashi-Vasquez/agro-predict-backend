from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema, _to_camel

class CompanyRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    code: str = Field(alias="code")
    name: str = Field(alias="name")
    ruc: str | None = Field(default=None, alias="ruc")
    description: str | None = Field(default=None, alias="description")
    logo_path: str | None = Field(default=None, alias="logoPath")
