from pydantic import BaseModel, Field


class ForecastDay(BaseModel):
    day: str
    date: str
    icon: str
    high: float | None = None
    low: float | None = None
    rain: int | None = None


class ForecastResponse(BaseModel):
    dias: list[ForecastDay] = Field(default_factory=list)
