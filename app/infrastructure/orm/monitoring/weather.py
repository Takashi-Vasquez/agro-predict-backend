from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class Weather(BitacoraMixin, Base):
    __tablename__ = "weather"
    __table_args__ = {"schema": Schemas.MONITORING}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    crop_id: Mapped[int | None] = mapped_column(ForeignKey("operations.crops.id"), nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    wind_speed: Mapped[float] = mapped_column(Float, nullable=False)
    wind_direction: Mapped[str | None] = mapped_column(String(50), nullable=True)
    precipitation: Mapped[float] = mapped_column(Float, nullable=False)
    pressure: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
