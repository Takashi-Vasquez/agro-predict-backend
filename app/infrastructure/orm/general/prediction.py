from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class Prediction(BitacoraMixin, Base):
    __tablename__ = "predictions"
    __table_args__ = {"schema": Schemas.CORE}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("security.users.id"), index=True, nullable=False)
    crop_id: Mapped[int | None] = mapped_column(ForeignKey("operations.crops.id"), nullable=True)
    predicted_crop: Mapped[str] = mapped_column(String(255), nullable=False)
    probability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    nitrogen: Mapped[float] = mapped_column(Float, default=0.0)
    phosphorus: Mapped[float] = mapped_column(Float, default=0.0)
    potassium: Mapped[float] = mapped_column(Float, default=0.0)
    temperature: Mapped[float] = mapped_column(Float, default=0.0)
    humidity: Mapped[float] = mapped_column(Float, default=0.0)
    ph_soil: Mapped[float] = mapped_column(Float, default=0.0)
    rainfall: Mapped[float] = mapped_column(Float, default=0.0)

    predicted_yield: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_yield: Mapped[float | None] = mapped_column(Float, nullable=True)
    gap: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_algorithm: Mapped[str | None] = mapped_column(String(50), nullable=True)

    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
