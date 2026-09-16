from app.domain.entities import Crop
from app.domain.repositories import CropRepository


class CreateCropUseCase:
    def __init__(self, crop_repo: CropRepository) -> None:
        self.crop_repo = crop_repo

    def execute(
        self,
        owner_id: int,
        name: str,
        variety: str,
        category: str,
        cycle: int,
        temperature: str,
        water: str,
        color: str,
    ) -> Crop:
        return self.crop_repo.create(
            owner_id=owner_id,
            name=name,
            variety=variety,
            category=category,
            cycle=cycle,
            temperature=temperature,
            water=water,
            color=color,
        )
