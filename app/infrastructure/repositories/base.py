from typing import Any, Generic, TypeVar

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.core.company_context import CompanyContext
from app.infrastructure.database.base import Base

ModelType = TypeVar("ModelType", bound="Base")


def apply_company_filter(stmt, model):
    """Aplica filtro de empresa al stmt si el modelo tiene company_id y hay empresa en contexto."""
    empresa_id = CompanyContext.get_empresa_id()
    if empresa_id is not None and hasattr(model, "company_id"):
        return stmt.where(model.company_id == empresa_id)
    return stmt


def get_company_id_or_none() -> int | None:
    return CompanyContext.get_empresa_id()


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: type) -> None:
        self.db = db
        self.model = model

    def _apply_company_filter(self, stmt):
        """Aplica filtro de empresa automáticamente si el modelo tiene company_id"""
        return apply_company_filter(stmt, self.model)

    def get(self, id: int) -> "ModelType | None":
        stmt = select(self.model).where(self.model.id == id)
        stmt = self._apply_company_filter(stmt)
        return self.db.scalar(stmt)

    def list(self, *, offset: int = 0, limit: int = 100):
        stmt = select(self.model).offset(offset).limit(limit)
        stmt = self._apply_company_filter(stmt)
        return list(self.db.scalars(stmt).all())

    def create(self, **kwargs: Any) -> "ModelType":
        from app.core.company_context import CompanyContext
        empresa_id = CompanyContext.get_empresa_id()
        if empresa_id is not None and hasattr(self.model, "company_id"):
            kwargs.setdefault("company_id", CompanyContext.get_empresa_id())
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj, **kwargs: Any):
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj) -> None:
        self.db.delete(obj)
        self.db.commit()
