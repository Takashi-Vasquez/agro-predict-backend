from app.domain.entities import Crop
from app.domain.repositories import CropRepository


class ListCropsUseCase:
    def __init__(self, crop_repo: CropRepository) -> None:
        self.crop_repo = crop_repo

    def execute(self, *, offset: int = 0, limit: int = 100) -> list[Crop]:
        return self.crop_repo.list_all(offset=offset, limit=limit)
