from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: type[ModelType]) -> None:
        self.db = db
        self.model = model

    def get(self, id: int) -> ModelType | None:
        return self.db.get(self.model, id)

    def list(self, *, offset: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, **kwargs: Any) -> ModelType:
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType, **kwargs: Any) -> ModelType:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.commit()
