from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class MenuRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: int | None
    name: str
    icon: str | None
    route: str | None
    order_index: int
    status: str


class MenuTreeRead(MenuRead):
    children: list["MenuTreeRead"] = []
    permissions: list[str] = []


class UserMeRead(BaseModel):
    id: int
    email: str
    status: str
    is_admin: bool

    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    age: int | None = None

    roles: list[RoleRead]
    menus: list[MenuTreeRead]
