from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, noload, selectinload

from app.domain.entities import User
from app.domain.repositories import AuthRepository
from app.infrastructure.orm.security.user import User as UserModel
from app.infrastructure.orm.security.user_role import UserRole as UserRoleModel
from app.infrastructure.orm.security.profile import Profile as ProfileModel
from app.infrastructure.config.security import create_access_token, verify_password
from app.infrastructure.config.settings import get_settings


class AuthRepositoryImpl:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def _user_options(self):
        return (
            joinedload(UserModel.profile),
            selectinload(UserModel.user_roles).selectinload(UserRoleModel.role),
            noload(UserModel.user_companies),
        )

    def get(self, user_id: int) -> User | None:
        stmt = (
            select(UserModel)
            .options(*self._user_options())
            .where(UserModel.id == user_id, UserModel.status != "DELETED")
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def get_by_email(self, email: str) -> User | None:
        stmt = (
            select(UserModel)
            .options(*self._user_options())
            .where(UserModel.email == email, UserModel.status != "DELETED")
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        from app.infrastructure.config.security import verify_password
        return verify_password(plain_password, hashed_password)

    def create_access_token(self, subject: str | int) -> str:
        from app.infrastructure.config.security import create_access_token
        return create_access_token(subject=subject)

    def _to_entity(self, orm) -> User:
        from app.domain.entities import User as UserEntity
        from app.domain.entities import Profile as ProfileEntity
        from app.domain.entities import RolePermission as RoleEntity

        profile = None
        if orm.profile:
            profile = ProfileEntity(
                id=orm.profile.id,
                user_id=orm.profile.user_id,
                first_name=orm.profile.first_name,
                last_name=orm.profile.last_name,
                document_number=orm.profile.document_number,
                phone=orm.profile.phone,
                age=orm.profile.age,
                status=orm.profile.status,
                created_at=orm.profile.created_at,
                updated_at=orm.profile.updated_at,
                deleted_at=orm.profile.deleted_at,
            )

        roles = []
        if orm.user_roles:
            for ur in orm.user_roles:
                if ur.status != "ACTIVE" or not ur.role or ur.role.status != "ACTIVE":
                    continue
                roles.append(RoleEntity(
                        id=ur.role.id,
                        name=ur.role.name,
                        status=ur.role.status,
                        created_at=ur.role.created_at,
                        updated_at=ur.role.updated_at,
                        deleted_at=ur.role.deleted_at,
                    ))

        return User(
            id=orm.id,
            email=orm.email,
            hashed_password=orm.hashed_password,
            is_admin=orm.is_admin,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
            profile=profile,
            roles=roles,
        )