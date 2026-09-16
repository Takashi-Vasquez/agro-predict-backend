from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema


class MenuRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    parent_id: int | None = Field(default=None, alias="parentId")
    code: str
    name: str
    icon: str | None = None
    badge: str | None = None
    route: str | None = None
    order_index: int = Field(alias="orderIndex")
    status: str


class MenuTreeRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    parent_id: int | None = Field(default=None, alias="parentId")
    code: str = Field(default="")
    name: str = Field(alias="name")
    icon: str | None = Field(default=None, alias="icon")
    route: str | None = Field(default=None, alias="route")
    order_index: int = Field(alias="orderIndex")
    badge: str | None = Field(default=None, alias="badge")
    status: str
    children: list["MenuTreeRead"] = Field(default=[], alias="children")
    available_permissions: list = Field(default=[], alias="availablePermissions")
