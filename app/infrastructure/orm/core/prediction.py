from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class Prediction(BitacoraMixin, Base):
    __tablename__ = "predictions"
    __table_args__ = {"schema": Schemas.CORE}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("security.users.id"), index=True, nullable=False)
    crop_id: Mapped[int | None] = mapped_column(ForeignKey("core.crops.id"), nullable=True)
    predicted_crop: Mapped[str] = mapped_column(String(255), nullable=False)
    probability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    N: Mapped[float] = mapped_column(Float, default=0.0)
    P: Mapped[float] = mapped_column(Float, default=0.0)
    K: Mapped[float] = mapped_column(Float, default=0.0)
    temperature: Mapped[float] = mapped_column(Float, default=0.0)
    humidity: Mapped[float] = mapped_column(Float, default=0.0)
    ph: Mapped[float] = mapped_column(Float, default=0.0)
    rainfall: Mapped[float] = mapped_column(Float, default=0.0)

    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
