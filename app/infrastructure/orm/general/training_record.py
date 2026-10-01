from datetime import datetime
from uuid import UUID

from sqlalchemy import Float, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class TrainingRecord(BitacoraMixin, Base):
    __tablename__ = "training_records"
    __table_args__ = {"schema": Schemas.CORE}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("security.users.id"), index=True, nullable=False)
    crop_id: Mapped[int | None] = mapped_column(ForeignKey("operations.crops.id"), nullable=True)
    campaign: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    nitrogen: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    phosphorus: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    potassium: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ph_soil: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rainfall: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    irrigation_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    variety: Mapped[str | None] = mapped_column(String(100), nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_yield: Mapped[float] = mapped_column(Float, nullable=False)

    source: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)
    import_batch_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    is_trained: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
