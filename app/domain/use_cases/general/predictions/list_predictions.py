from app.domain.entities import Prediction
from app.domain.repositories import PredictionRepository


class ListPredictionsUseCase:
    def __init__(self, prediction_repo: PredictionRepository) -> None:
        self.prediction_repo = prediction_repo

    def execute(self, *, offset: int = 0, limit: int = 100) -> list[Prediction]:
        return self.prediction_repo.list_all(offset=offset, limit=limit)
