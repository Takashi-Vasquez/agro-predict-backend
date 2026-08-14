from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoleMenuPermissionCreate(BaseModel):
    role_id: int
    menu_id: int
    permission_id: int


class RoleMenuPermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    menu_id: int
    permission_id: int
    status: str
    created_at: datetime


class AssignmentItem(BaseModel):
    menu_id: int
    permission_id: int


class RoleMenuPermissionBulkCreate(BaseModel):
    assignments: list[AssignmentItem]
