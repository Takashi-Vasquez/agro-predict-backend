from app.domain.repositories.general.training_record_repository import TrainingRecordRepository


class GetTrainingStatsUseCase:
    def __init__(self, record_repo: TrainingRecordRepository) -> None:
        self.record_repo = record_repo

    def execute(self) -> dict:
        model_version = self.record_repo.get_model_version_stats()
        total = self.record_repo.count_all()
        count_crop = self.record_repo.count_by_crop()
        count_campaign = self.record_repo.count_by_campaign()
        is_all_trained = self.record_repo.validate_is_all_trained()
        return {
            "model_version": model_version,
            "total": total,
            "count_crop": count_crop,
            "count_campaign": count_campaign,
            "is_all_trained": is_all_trained,
        }
