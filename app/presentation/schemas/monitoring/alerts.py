from pydantic import BaseModel, Field


class WeatherAlert(BaseModel):
    icon: str
    titulo: str
    detalle: str
    nivel: str


class AlertsResponse(BaseModel):
    alertas: list[WeatherAlert] = Field(default_factory=list)
