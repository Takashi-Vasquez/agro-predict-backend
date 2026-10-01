from app.domain.repositories.general.trained_model_repository import TrainedModelRepository


class SelectModelUseCase:
    def __init__(self, model_repo: TrainedModelRepository) -> None:
        self.model_repo = model_repo

    def execute(self, model_id: int) -> dict:
        model = self.model_repo.get(model_id)
        if not model:
            raise ValueError("Modelo no encontrado")

        self.model_repo.set_selected(model_id)
        return {"id": model.id, "algorithm": model.algorithm, "is_selected": True}
