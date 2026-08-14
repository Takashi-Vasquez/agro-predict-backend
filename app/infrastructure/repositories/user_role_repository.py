from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import UserRole
from app.domain.repositories import UserRoleRepository
from app.infrastructure.orm.security.user_role import UserRole as UserRoleModel


class UserRoleRepositoryImpl(UserRoleRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_id(self, user_id: int) -> list[UserRole]:
        stmt = select(UserRoleModel).where(
            UserRoleModel.user_id == user_id,
            UserRoleModel.status == "ACTIVE",
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def assign(self, user_id: int, role_id: int) -> UserRole:
        orm = UserRoleModel(user_id=user_id, role_id=role_id)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def remove_by_user_id(self, user_id: int) -> None:
        stmt = select(UserRoleModel).where(
            UserRoleModel.user_id == user_id,
            UserRoleModel.status == "ACTIVE",
        )
        for orm in self.db.scalars(stmt).all():
            orm.status = "DELETED"
        self.db.commit()

    @staticmethod
    def _to_entity(orm: UserRoleModel) -> UserRole:
        return UserRole(
            id=orm.id,
            user_id=orm.user_id,
            role_id=orm.role_id,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
