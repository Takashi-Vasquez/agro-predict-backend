from dataclasses import dataclass, field
from datetime import datetime
from typing import TypedDict

from app.domain.entities.security.profile import Profile
from app.domain.entities.security.role_permissions import RolePermission
from app.domain.entities.security.user_company import UserCompany

class UserCompanyDict(TypedDict):
    id: int
    is_default: bool
@dataclass
class User:
    id: int = 0
    email: str = ""
    hashed_password: str = ""
    is_admin: bool = False
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
    profile: Profile | None = None
    roles: list[RolePermission] = field(default_factory=list)
    userCompany: list[UserCompany] = field(default_factory=list)

    @property
    def first_name(self) -> str | None:
        return self.profile.first_name if self.profile else None

    @property
    def last_name(self) -> str | None:
        return self.profile.last_name if self.profile else None

    @property
    def phone(self) -> str | None:
        return self.profile.phone if self.profile else None

    @property
    def age(self) -> int | None:
        return self.profile.age if self.profile else None

    @property
    def role_ids(self) -> list[int]:
        return [r.id for r in self.roles] if self.roles else []

    @property
    def document_number(self) -> str | None:
        return self.profile.document_number if self.profile else None

    @property
    def companies(self) -> list[UserCompanyDict]:
        return [{"id": r.company_id, "is_default": r.is_default} for r in self.userCompany] if self.userCompany else []
