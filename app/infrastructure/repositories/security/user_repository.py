from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import User
from app.domain.repositories import UserRepository
from app.infrastructure.orm.security.user import User as UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: int) -> User | None:
        orm = self.db.get(UserModel, user_id)
        return self._to_entity(orm) if orm else None

    def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(
            UserModel.email == email,
            UserModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def list(self, *, offset: int = 0, limit: int = 100) -> list[User]:
        stmt = (
            select(UserModel)
            .where(UserModel.status != "DELETED")
            .offset(offset)
            .limit(limit)
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def create(self, email: str, hashed_password: str, is_admin: bool) -> User:
        orm = UserModel(email=email, hashed_password=hashed_password, is_admin=is_admin)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, user: User, **kwargs) -> User:
        orm = self.db.get(UserModel, user.id)
        for key, value in kwargs.items():
            setattr(orm, key, value)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def delete(self, user: User) -> None:
        orm = self.db.get(UserModel, user.id)
        orm.status = "DELETED"
        orm.deleted_at = datetime.utcnow()
        self.db.commit()

    @staticmethod
    def _to_entity(orm: UserModel) -> User:
        return User(
            id=orm.id,
            email=orm.email,
            hashed_password=orm.hashed_password,
            is_admin=orm.is_admin,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
