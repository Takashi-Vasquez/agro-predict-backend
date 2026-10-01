from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WeatherReading:
    id: int = 0
    crop_id: int | None = None
    location: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    weather_code: int = 0
    temperature: float = 0.0
    temperature_max: float = 0.0
    temperature_min: float = 0.0
    apparent_temperature: float = 0.0
    humidity: int = 0
    precipitation: float = 0.0
    precipitation_probability: int = 0
    wind_speed: float = 0.0
    wind_direction_degrees: float = 0.0
    pressure: float = 0.0
    uv_index: float = 0.0
    recorded_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
