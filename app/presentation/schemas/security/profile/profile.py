from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema


class ProfileCreate(BaseModel):
    first_name: str = Field(alias="firstName", min_length=1, max_length=100)
    last_name: str = Field(alias="lastName", min_length=1, max_length=100)
    phone: str | None = Field(default=None, alias="phone")
    age: int | None = Field(default=None, alias="age")
    document_number: str | None = Field(default=None, alias="documentNumber", max_length=30)


class ProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, alias="firstName", min_length=1, max_length=100)
    last_name: str | None = Field(default=None, alias="lastName", min_length=1, max_length=100)
    phone: str | None = Field(default=None, alias="phone")
    age: int | None = Field(default=None, alias="age")
    document_number: str | None = Field(default=None, alias="documentNumber", max_length=30)


class ProfileRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    user_id: int = Field(alias="userId")
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    phone: str | None = Field(default=None, alias="phone")
    age: int | None = Field(default=None, alias="age")
    document_number: str | None = Field(default=None, alias="documentNumber")
    status: str
    created_at: datetime
    updated_at: datetime
