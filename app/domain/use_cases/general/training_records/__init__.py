from app.domain.use_cases.general.training_records.create import CreateTrainingRecordUseCase
from app.domain.use_cases.general.training_records.list_records import ListTrainingRecordsUseCase
from app.domain.use_cases.general.training_records.get_record import GetTrainingRecordUseCase
from app.domain.use_cases.general.training_records.delete import DeleteTrainingRecordUseCase
from app.domain.use_cases.general.training_records.stats import GetTrainingStatsUseCase

__all__ = [
    "CreateTrainingRecordUseCase",
    "ListTrainingRecordsUseCase",
    "GetTrainingRecordUseCase",
    "DeleteTrainingRecordUseCase",
    "GetTrainingStatsUseCase",
]
