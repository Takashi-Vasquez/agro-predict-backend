from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.core.company import Company
from app.domain.repositories.core.company_repository import CompanyRepository
from app.infrastructure.orm.core.company import Company as CompanyModel
from app.infrastructure.orm.security.user_company import UserCompany as UserCompanyModel
from app.infrastructure.repositories.base import apply_company_filter


class CompanyRepositoryImpl(CompanyRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, company_id: int) -> Company | None:
        orm = (
            self.db.query(CompanyModel)
            .filter(
                CompanyModel.id == company_id,
                CompanyModel.status != "DELETED",
            )
            .first()
        )
        return self._to_entity(orm) if orm else None

    def get_by_code(self, code: str) -> Company | None:
        orm = (
            self.db.query(CompanyModel)
            .filter(
                CompanyModel.code == code,
                CompanyModel.status != "DELETED",
            )
            .first()
        )
        return self._to_entity(orm) if orm else None

    def list_all(self) -> list[Company]:
        stmt = (
            select(CompanyModel)
            .where(CompanyModel.status != "DELETED")
            .order_by(CompanyModel.name)
        )
        stmt = apply_company_filter(stmt, CompanyModel)
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def list_for_user(self, user_id: int) -> list[tuple[Company, bool]]:
        rows = (
            self.db.query(CompanyModel, UserCompanyModel.is_default)
            .join(UserCompanyModel, UserCompanyModel.company_id == CompanyModel.id)
            .filter(
                UserCompanyModel.user_id == user_id,
                UserCompanyModel.is_active.is_(True),
                UserCompanyModel.status != "DELETED",
                CompanyModel.status != "DELETED",
            )
            .order_by(UserCompanyModel.is_default.desc(), CompanyModel.name)
            .all()
        )
        return [(self._to_entity(company), is_default) for company, is_default in rows]

    def get_default_company_id(self, user_id: int) -> int | None:
        row = (
            self.db.query(UserCompanyModel.company_id)
            .join(CompanyModel, CompanyModel.id == UserCompanyModel.company_id)
            .filter(
                UserCompanyModel.user_id == user_id,
                UserCompanyModel.is_active.is_(True),
                UserCompanyModel.status != "DELETED",
                CompanyModel.status != "DELETED",
            )
            .order_by(UserCompanyModel.is_default.desc(), UserCompanyModel.id)
            .first()
        )
        return row[0] if row else None

    def user_has_company(self, user_id: int, company_id: int) -> bool:
        row = (
            self.db.query(UserCompanyModel.id)
            .filter(
                UserCompanyModel.user_id == user_id,
                UserCompanyModel.company_id == company_id,
                UserCompanyModel.is_active.is_(True),
                UserCompanyModel.status != "DELETED",
            )
            .first()
        )
        return row is not None

    @staticmethod
    def _to_entity(orm: CompanyModel) -> Company:
        return Company(
            id=orm.id,
            code=orm.code,
            name=orm.name,
            ruc=orm.ruc,
            description=orm.description,
            logo_path=orm.logo_path,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
