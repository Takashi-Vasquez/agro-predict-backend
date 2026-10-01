from abc import ABC, abstractmethod

from app.domain.entities.operations.variety import Variety


class VarietyRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Variety]: ...

    @abstractmethod
    def get_by_name(self, name: str) -> Variety | None: ...
