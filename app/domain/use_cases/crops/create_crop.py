from app.domain.entities import Crop
from app.domain.repositories import CropRepository


class CreateCropUseCase:
    def __init__(self, crop_repo: CropRepository) -> None:
        self.crop_repo = crop_repo

    def execute(
        self,
        owner_id: int,
        name: str,
        location: str | None = None,
        area_hectares: float = 0.0,
        notes: str | None = None,
    ) -> Crop:
        return self.crop_repo.create(
            owner_id=owner_id,
            name=name,
            location=location,
            area_hectares=area_hectares,
            notes=notes,
        )
