from app.domain.entities import Crop
from app.domain.repositories import CropRepository


class GetCropUseCase:
    def __init__(self, crop_repo: CropRepository) -> None:
        self.crop_repo = crop_repo

    def execute(self, crop_id: int) -> Crop | None:
        return self.crop_repo.get(crop_id)
