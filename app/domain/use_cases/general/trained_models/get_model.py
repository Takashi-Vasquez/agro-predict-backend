from app.domain.repositories.general.trained_model_repository import TrainedModelRepository


class GetModelUseCase:
    def __init__(self, model_repo: TrainedModelRepository) -> None:
        self.model_repo = model_repo

    def execute(self, model_id: int) -> dict | None:
        model = self.model_repo.get(model_id)
        if not model:
            return None
        return {
            "id": model.id,
            "name": model.name,
            "algorithm": model.algorithm,
            "version": model.version,
            "r2_score": model.r2_score,
            "rmse": model.rmse,
            "mae": model.mae,
            "feature_importance": model.feature_importance,
            "hyperparameters": model.hyperparameters,
            "training_samples": model.training_samples,
            "feature_names": model.feature_names,
            "is_selected": model.is_selected,
            "notes": model.notes,
            "created_at": model.created_at.isoformat() if model.created_at else None,
        }
