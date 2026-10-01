from datetime import date, datetime
from typing import Dict
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema, _to_camel


class TrainingRecordCreate(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    crop_id: int | None = Field(alias="cropId", default=None, description="ID del cultivo")
    campaign: str | None = Field(default=None, max_length=50, description="Campaña o año")
    location: str | None = Field(default=None, max_length=255, description="Ubicación")

    nitrogen: float = Field(ge=0, le=500, description="Nitrógeno (kg/ha)")
    phosphorus: float = Field(ge=0, le=200, description="Fósforo (kg/ha)")
    potassium: float = Field(ge=0, le=400, description="Potasio (kg/ha)")
    temperature: float = Field(ge=0, le=45, description="Temperatura (°C)")
    humidity: float = Field(ge=0, le=100, description="Humedad del suelo (%)")
    ph_soil: float = Field(alias="phSoil", ge=3, le=10, description="pH del suelo")
    rainfall: float = Field(ge=0, le=500, description="Precipitación (mm)")
    irrigation_type: str | None = Field(alias="irrigationType", default=None, max_length=50, description="Tipo de riego")
    variety: str | None = Field(default=None, max_length=100, description="Variedad")
    soil_type: str | None = Field(alias="soilType", default=None, max_length=50, description="Tipo de suelo")
    
    target_yield: float = Field(gt=0, le=250, description="Rendimiento real obtenido (t/ha)")


class TrainingRecordRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    user_id: int = Field(alias="userId")
    crop_id: int | None = Field(default=None, alias="cropId")
    campaign: str | None = None
    location: str | None = None

    nitrogen: float
    phosphorus: float
    potassium: float
    temperature: float
    humidity: float
    ph_soil: float
    rainfall: float
    irrigation_type: str | None = Field(default=None, alias="irrigationType")
    variety: str | None = None
    soil_type: str | None = Field(default=None, alias="soilType")

    target_yield: float = Field(alias="targetYield")

    source: str
    import_batch_id: UUID | None = Field(default=None, alias="importBatchId")
    is_trained: bool = Field(alias="isTrained")

    status: str
    created_at: datetime

class CandidateMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    r2: float
    mae: float
    rmse: float

class TrainingRecordModelVersion(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    version: str
    trained_at : datetime = Field(default=None, alias="trainedAt")
    data_from: date = Field(default=None, alias="dataFrom")
    data_to: date = Field(default=None, alias="dataTo")
    metrics: CandidateMetrics = Field(default=None, alias="metrics")

class TrainingRecordStats(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    model_version: TrainingRecordModelVersion = Field(alias="modelVersion")
    total: int
    count_crop: int = Field(alias="countCrop")
    count_campaign: int = Field(alias="countCampaign")
    is_all_trained: bool = Field(alias="isAllTrained")
