from app.domain.repositories.general.trained_model_repository import TrainedModelRepository


class ListModelsUseCase:
    def __init__(self, model_repo: TrainedModelRepository) -> None:
        self.model_repo = model_repo

    def execute(self) -> list[dict]:
        models = self.model_repo.list_all()
        return [
            {
                "id": m.id,
                "name": m.name,
                "algorithm": m.algorithm,
                "version": m.version,
                "r2_score": m.r2_score,
                "rmse": m.rmse,
                "mae": m.mae,
                "training_samples": m.training_samples,
                "is_selected": m.is_selected,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in models
        ]
