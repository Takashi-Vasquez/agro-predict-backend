from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(populate_by_name=True)

    statusCode: int = Field(alias="statusCode")
    message: str = Field(alias="message")
    data: T | None = Field(default=None, alias="data")


class Message(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    detail: str = Field(alias="detail")
