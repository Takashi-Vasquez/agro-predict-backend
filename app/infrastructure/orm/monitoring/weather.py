from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class WeatherReading(BitacoraMixin, Base):
    __tablename__ = "weather_readings"
    __table_args__ = {"schema": Schemas.MONITORING}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    crop_id: Mapped[int | None] = mapped_column(ForeignKey("operations.crops.id"), nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    weather_code: Mapped[int] = mapped_column(Integer, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    temperature_max: Mapped[float] = mapped_column(Float, nullable=False)
    temperature_min: Mapped[float] = mapped_column(Float, nullable=False)
    apparent_temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[int] = mapped_column(Integer, nullable=False)
    precipitation: Mapped[float] = mapped_column(Float, nullable=False)
    precipitation_probability: Mapped[int] = mapped_column(Integer, nullable=False)
    wind_speed: Mapped[float] = mapped_column(Float, nullable=False)
    wind_direction_degrees: Mapped[float] = mapped_column(Float, nullable=False)
    pressure: Mapped[float] = mapped_column(Float, nullable=False)
    uv_index: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
