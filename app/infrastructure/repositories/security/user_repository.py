from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.domain.entities import User
from app.domain.repositories import UserRepository
from app.infrastructure.repositories.base import apply_company_filter
from app.infrastructure.orm.security.user import User as UserModel
from app.infrastructure.orm.security.user_role import UserRole as UserRoleModel
from app.infrastructure.orm.security.profile import Profile as ProfileModel
from app.infrastructure.orm.security.user_company import UserCompany as UserCompanyModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _user_options():
        return (
            joinedload(UserModel.profile),
            selectinload(UserModel.user_roles).selectinload(UserRoleModel.role),
            selectinload(UserModel.user_companies),
        )

    def _load_full(self, user_id: int) -> UserModel | None:
        stmt = (
            select(UserModel)
            .options(*self._user_options())
            .where(UserModel.id == user_id)
        )
        return self.db.scalar(stmt)

    def get(self, user_id: int) -> User | None:
        stmt = (
            select(UserModel)
            .options(*self._user_options())
            .where(UserModel.id == user_id, UserModel.status != "DELETED", UserModel.is_admin.is_(False))
        )
        stmt = apply_company_filter(stmt, UserModel)
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

    def list(self, *, offset: int = 0, limit: int = 100) -> list[User]:
        stmt = (
            select(UserModel)
            .options(*self._user_options())
            .where(UserModel.status != "DELETED", UserModel.is_admin.is_(False))
            .order_by(UserModel.id)
            .offset(offset)
            .limit(limit)
        )
        stmt = apply_company_filter(stmt, UserModel)
        return [self._to_entity(o) for o in self.db.scalars(stmt).unique().all()]

    def create(self, email: str, hashed_password: str, is_admin: bool, status: str = "ACTIVE") -> User:
        orm = UserModel(
            email=email,
            hashed_password=hashed_password,
            is_admin=is_admin,
            status=status,
        )
        self.db.add(orm)
        self.db.commit()
        return self._to_entity(self._load_full(orm.id))

    def update(self, user: User, **kwargs) -> User:
        orm = self.db.get(UserModel, user.id)
        for key, value in kwargs.items():
            setattr(orm, key, value)
        self.db.commit()
        return self._to_entity(self._load_full(user.id))

    def delete(self, user: User) -> None:
        orm = self.db.get(UserModel, user.id)
        orm.status = "DELETED"
        orm.deleted_at = datetime.now(timezone.utc)
        self.db.commit()

    def _to_entity(self, orm) -> User:
        from app.domain.entities import User as UserEntity
        from app.domain.entities import Profile as ProfileEntity
        from app.domain.entities import RolePermission as RoleEntity
        from app.domain.entities import UserCompany as UserCompanyEntity

        profile = None
        if orm.profile:
            profile = ProfileEntity(
                id=orm.profile.id,
                user_id=orm.profile.user_id,
                document_number=orm.profile.document_number,
                first_name=orm.profile.first_name,
                last_name=orm.profile.last_name,
                phone=orm.profile.phone,
                age=orm.profile.age,
                status=orm.profile.status,
                created_at=orm.profile.created_at,
                updated_at=orm.profile.updated_at,
                deleted_at=orm.profile.deleted_at,
            )

        roles = []
        if orm.user_roles:
            for ur in orm.user_roles or []:
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
                    
                    
        userCompany = []
        if orm.user_companies:
            for uc in orm.user_companies or []:
                if not uc.is_active or uc.status != "ACTIVE":
                    continue
                userCompany.append(UserCompanyEntity(
                    id=uc.id,
                    user_id=uc.user_id,
                    company_id=uc.company_id,
                    is_default=uc.is_default,
                    is_active=uc.is_active,
                    status=uc.status,
                    created_at=uc.created_at,
                    updated_at=uc.updated_at,
                    deleted_at=uc.deleted_at,
                ))

        return UserEntity(
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
            userCompany=userCompany,
        )
