from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Profile
from app.domain.repositories import ProfileRepository
from app.infrastructure.orm.security.profile import Profile as ProfileModel


class ProfileRepositoryImpl(ProfileRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, profile_id: int) -> Profile | None:
        stmt = select(ProfileModel).where(
            ProfileModel.id == profile_id,
            ProfileModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def get_by_user_id(self, user_id: int) -> Profile | None:
        stmt = select(ProfileModel).where(
            ProfileModel.user_id == user_id,
            ProfileModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def create(self, user_id: int, first_name: str, last_name: str, phone: str | None, age: int | None) -> Profile:
        orm = ProfileModel(user_id=user_id, first_name=first_name, last_name=last_name, phone=phone, age=age)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    def update(self, profile: Profile, **kwargs) -> Profile:
        orm = self.db.get(ProfileModel, profile.id)
        for key, value in kwargs.items():
            setattr(orm, key, value)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    @staticmethod
    def _to_entity(orm: ProfileModel) -> Profile:
        return Profile(
            id=orm.id,
            user_id=orm.user_id,
            first_name=orm.first_name,
            last_name=orm.last_name,
            phone=orm.phone,
            age=orm.age,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
