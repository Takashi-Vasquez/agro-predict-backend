from app.domain.entities import Prediction
from app.domain.repositories import PredictionRepository
from app.infrastructure.ml.model import CropPredictor


class PredictUseCase:
    def __init__(self, prediction_repo: PredictionRepository, predictor: CropPredictor) -> None:
        self.prediction_repo = prediction_repo
        self.predictor = predictor

    def execute(self, user_id: int, data: dict, crop_id: int | None = None) -> Prediction:
        try:
            label, probability = self.predictor.predict(data)
        except FileNotFoundError as exc:
            self._record_error(user_id, data, crop_id, str(exc))
            raise ValueError("Modelo no disponible. Entrena el modelo primero.") from exc

        return self.prediction_repo.create(
            user_id=user_id,
            crop_id=crop_id,
            predicted_crop=label,
            probability=probability,
            nitrogen=data.get("nitrogen", 0.0),
            phosphorus=data.get("phosphorus", 0.0),
            potassium=data.get("potassium", 0.0),
            temperature=data.get("temperature", 0.0),
            humidity=data.get("humidity", 0.0),
            ph_soil=data.get("ph_soil", 0.0),
            rainfall=data.get("rainfall", 0.0),
            status="ok",
        )

    def _record_error(self, user_id: int, data: dict, crop_id: int | None, message: str) -> None:
        try:
            self.prediction_repo.create(
                user_id=user_id,
                crop_id=crop_id,
                predicted_crop="",
                probability=0.0,
                nitrogen=data.get("nitrogen", 0.0),
                phosphorus=data.get("phosphorus", 0.0),
                potassium=data.get("potassium", 0.0),
                temperature=data.get("temperature", 0.0),
                humidity=data.get("humidity", 0.0),
                ph_soil=data.get("ph_soil", 0.0),
                rainfall=data.get("rainfall", 0.0),
                status="error",
                error_message=message[:500],
            )
        except Exception:
            pass
