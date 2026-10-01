from pydantic import BaseModel, Field


class DailyCurveResponse(BaseModel):
    values: list[float] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    max: float = 32.0
