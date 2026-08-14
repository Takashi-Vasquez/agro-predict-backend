from pydantic import BaseModel, ConfigDict


class MenuRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: int | None
    name: str
    icon: str | None
    route: str | None
    order_index: int
    status: str


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class MenuTreeRead(MenuRead):
    children: list["MenuTreeRead"] = []
    available_permissions: list[PermissionRead] = []
