from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema


class ProfileCreate(BaseModel):
    full_name: str = Field(alias="fullName", min_length=1, max_length=255)


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, alias="fullName", min_length=1, max_length=255)


class ProfileRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    user_id: int = Field(alias="userId")
    full_name: str = Field(alias="fullName")
    status: str
