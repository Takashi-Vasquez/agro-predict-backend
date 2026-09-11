from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema


class PredictionInput(BaseModel):
    N: float = Field(ge=0, le=150, description="Nitrogeno (mg/kg)")
    P: float = Field(ge=0, le=150, description="Fosforo (mg/kg)")
    K: float = Field(ge=0, le=210, description="Potasio (mg/kg)")
    temperature: float = Field(ge=0, le=60, description="Temperatura (C)")
    humidity: float = Field(ge=0, le=110, description="Humedad relativa (%)")
    ph: float = Field(ge=0, le=14, description="pH del suelo")
    rainfall: float = Field(ge=0, le=400, description="Precipitacion (mm)")
    crop_id: int | None = Field(default=None, description="Cultivo opcional asociado")


class PredictionRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    predicted_crop: str = Field(alias="predictedCrop")
    probability: float = Field(alias="probability")
    status: str
    created_at: datetime
    crop_id: int | None = Field(default=None, alias="cropId")
