from app.domain.entities import Prediction
from app.domain.repositories import PredictionRepository


class ListPredictionsUseCase:
    def __init__(self, prediction_repo: PredictionRepository) -> None:
        self.prediction_repo = prediction_repo

    def execute(self, user_id: int, *, offset: int = 0, limit: int = 100) -> list[Prediction]:
        return self.prediction_repo.list_for_user(user_id, offset=offset, limit=limit)
