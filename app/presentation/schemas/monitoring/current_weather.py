from pydantic import BaseModel, Field


class WeatherMetric(BaseModel):
    label: str
    value: float | int
    unit: str
    detail: str
    icon: str


class CurrentWeatherResponse(BaseModel):
    ubicacion: str
    fecha: str | None = None
    stale: bool = False
    temperatura_actual: float | None = None
    descripcion: str
    icono: str
    maxima: float | None = None
    minima: float | None = None
    sensacion_termica: float | None = None
    metrics: list[WeatherMetric] = Field(default_factory=list)
