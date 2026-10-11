from app.domain.entities.core.company import Company
from app.domain.repositories.core.company_repository import CompanyRepository


class ListCompaniesUseCase:
    def __init__(self, company_repo: CompanyRepository) -> None:
        self.company_repo = company_repo

    def execute(self, *, show_all: bool = False, user_id: int) -> list[Company]:
        if show_all:
            return self.company_repo.list_all()
        return [company for company, _is_default in self.company_repo.list_for_user(user_id)]
