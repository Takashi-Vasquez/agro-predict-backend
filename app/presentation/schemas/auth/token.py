from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.presentation.schemas import BaseReadSchema


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")


class TokenPayload(BaseModel):
    sub: str | None = None
