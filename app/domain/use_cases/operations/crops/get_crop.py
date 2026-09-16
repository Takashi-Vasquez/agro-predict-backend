from app.domain.entities import Crop
from app.domain.repositories import CropRepository


class GetCropUseCase:
    def __init__(self, crop_repo: CropRepository) -> None:
        self.crop_repo = crop_repo

    def execute(self, owner_id: int, crop_id: int) -> Crop | None:
        return self.crop_repo.get_owned(owner_id, crop_id)
