from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Role
from app.domain.repositories import RoleRepository
from app.infrastructure.orm.security.role import Role as RoleModel


class RoleRepositoryImpl(RoleRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, role_id: int) -> Role | None:
        stmt = select(RoleModel).where(
            RoleModel.id == role_id,
            RoleModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def get_by_name(self, name: str) -> Role | None:
        stmt = select(RoleModel).where(
            RoleModel.name == name,
            RoleModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def list(self, *, offset: int = 0, limit: int = 100) -> list[Role]:
        stmt = (
            select(RoleModel)
            .where(RoleModel.status != "DELETED")
            .offset(offset)
            .limit(limit)
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def create(self, name: str, description: str | None) -> Role:
        orm = RoleModel(name=name, description=description)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, role: Role, **kwargs) -> Role:
        orm = self.db.get(RoleModel, role.id)
        for key, value in kwargs.items():
            setattr(orm, key, value)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, role: Role) -> None:
        orm = self.db.get(RoleModel, role.id)
        orm.status = "DELETED"
        orm.deleted_at = datetime.utcnow()
        self.db.commit()

    @staticmethod
    def _to_entity(orm: RoleModel) -> Role:
        return Role(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
