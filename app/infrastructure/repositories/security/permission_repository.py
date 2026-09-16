from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Permission
from app.domain.repositories import PermissionRepository
from app.infrastructure.orm.security.permission import Permission as PermissionModel


class PermissionRepositoryImpl(PermissionRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, permission_id: int) -> Permission | None:
        stmt = select(PermissionModel).where(
            PermissionModel.id == permission_id,
            PermissionModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def get_by_code(self, code: str) -> Permission | None:
        stmt = select(PermissionModel).where(
            PermissionModel.code == code,
            PermissionModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def get_all(self) -> list[Permission]:
        stmt = select(PermissionModel).where(PermissionModel.status != "DELETED")
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    @staticmethod
    def _to_entity(orm: PermissionModel) -> Permission:
        return Permission(
            id=orm.id,
            code=orm.code,
            name=orm.name,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
