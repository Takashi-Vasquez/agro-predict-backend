from app.domain.repositories import CropRepository


class DeleteCropUseCase:
    def __init__(self, crop_repo: CropRepository) -> None:
        self.crop_repo = crop_repo

    def execute(self, owner_id: int, crop_id: int) -> None:
        crop = self.crop_repo.get_owned(owner_id, crop_id)
        if not crop:
            raise ValueError("Cultivo no encontrado")
        self.crop_repo.delete(crop)
