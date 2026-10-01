from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema, _to_camel


class PredictionInput(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    nitrogen: float = Field(ge=0, le=500, description="Nitrógeno (kg/ha)")
    phosphorus: float = Field(ge=0, le=200, description="Fósforo (kg/ha)")
    potassium: float = Field(ge=0, le=400, description="Potasio (kg/ha)")
    temperature: float = Field(ge=0, le=45, description="Temperatura (°C)")
    humidity: float = Field(ge=0, le=100, description="Humedad del suelo (%)")
    ph_soil: float = Field(ge=3, le=10, description="pH del suelo")
    rainfall: float = Field(ge=0, le=500, description="Precipitación (mm)")
    crop_id: int | None = Field(default=None, description="Cultivo opcional asociado")
    target_yield: float | None = Field(default=None, description="Rendimiento real (t/ha) para comparar")


class YieldPredictionResponse(BaseModel):
    id: int
    predicted_yield: float = Field(alias="predictedYield")
    target_yield: float | None = Field(default=None, alias="targetYield")
    gap: float | None = None
    model_id: int = Field(alias="modelId")
    model_algorithm: str = Field(alias="modelAlgorithm")
    model_r2: float = Field(alias="modelR2")


class PredictionRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    predicted_crop: str = Field(alias="predictedCrop")
    probability: float = Field(alias="probability")
    predicted_yield: float | None = Field(default=None, alias="predictedYield")
    target_yield: float | None = Field(default=None, alias="targetYield")
    gap: float | None = None
    model_id: int | None = Field(default=None, alias="modelId")
    model_algorithm: str | None = Field(default=None, alias="modelAlgorithm")
    modelo_version_id: int | None = Field(default=None, alias="modeloVersionId")
    status: str
    created_at: datetime
    crop_id: int | None = Field(default=None, alias="cropId")
