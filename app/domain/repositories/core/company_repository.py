from abc import ABC, abstractmethod

from app.domain.entities.core.company import Company


class CompanyRepository(ABC):
    @abstractmethod
    def get(self, company_id: int) -> Company | None: ...

    @abstractmethod
    def get_by_code(self, code: str) -> Company | None: ...

    @abstractmethod
    def list_all(self) -> list[Company]:
        """Todas las empresas activas ordenadas por nombre."""
        ...

    @abstractmethod
    def list_for_user(self, user_id: int) -> list[tuple[Company, bool]]:
        """Empresas activas del usuario con su flag is_default (desde user_company)."""
        ...

    @abstractmethod
    def get_default_company_id(self, user_id: int) -> int | None:
        """company_id de la empresa default del usuario (is_default o la primera activa)."""
        ...

    @abstractmethod
    def user_has_company(self, user_id: int, company_id: int) -> bool:
        """True si el usuario tiene una fila activa en user_company para esa empresa."""
        ...
