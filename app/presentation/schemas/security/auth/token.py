from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class Token(BaseModel):
    accessToken: str
    tokenType: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None
    scopes: list[str] = []
