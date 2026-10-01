from app.domain.entities import Crop
from app.domain.repositories import CropRepository


class UpdateCropUseCase:
    def __init__(self, crop_repo: CropRepository) -> None:
        self.crop_repo = crop_repo

    def execute(self, crop_id: int, **kwargs) -> Crop:
        crop = self.crop_repo.get(crop_id)
        if not crop:
            raise ValueError("Cultivo no encontrado")
        return self.crop_repo.update(crop, **kwargs)
