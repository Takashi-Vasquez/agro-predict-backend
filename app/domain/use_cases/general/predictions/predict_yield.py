from pathlib import Path

from app.domain.repositories.general.prediction_repository import PredictionRepository
from app.domain.repositories.general.trained_model_repository import TrainedModelRepository
from app.infrastructure.ml.yield_predictor import YieldPredictor


class PredictYieldUseCase:
    def __init__(
        self,
        prediction_repo: PredictionRepository,
        model_repo: TrainedModelRepository,
        artifacts_dir: Path,
    ) -> None:
        self.prediction_repo = prediction_repo
        self.model_repo = model_repo
        self.artifacts_dir = artifacts_dir

    def execute(
        self,
        user_id: int,
        data: dict,
        crop_id: int | None = None,
        model_id: int | None = None,
    ) -> dict:
        if model_id:
            model = self.model_repo.get(model_id)
        else:
            model = self.model_repo.get_selected()

        if not model:
            raise ValueError("No hay modelo entrenado disponible. Entrena uno primero.")

        predictor = YieldPredictor(model.artifact_path)
        prediction_result = predictor.predict(data)

        predicted_yield = prediction_result["predicted_yield"]
        target_yield = data.get("target_yield")
        gap = None
        if target_yield is not None and target_yield > 0:
            gap = round(predicted_yield - float(target_yield), 2)

        record = self.prediction_repo.create(
            user_id=user_id,
            crop_id=crop_id,
            predicted_crop="yield_regression",
            probability=0.0,
            nitrogen=data.get("nitrogen", 0),
            phosphorus=data.get("phosphorus", 0),
            potassium=data.get("potassium", 0),
            temperature=data.get("temperature", 0),
            humidity=data.get("humidity", 0),
            ph_soil=data.get("ph_soil", 0),
            rainfall=data.get("rainfall", 0),
            predicted_yield=predicted_yield,
            target_yield=float(target_yield) if target_yield else None,
            gap=gap,
            model_id=model.id,
            model_algorithm=model.algorithm,
            status="ACTIVE",
        )

        return {
            "id": record.id,
            "predicted_yield": predicted_yield,
            "target_yield": float(target_yield) if target_yield else None,
            "gap": gap,
            "model_id": model.id,
            "model_algorithm": model.algorithm,
            "model_r2": model.r2_score,
            "model_rmse": model.rmse,
        }
