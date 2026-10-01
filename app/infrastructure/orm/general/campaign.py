from datetime import date
from sqlalchemy import Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class Campaign(BitacoraMixin, Base):
    __tablename__ = "campaigns"
    __table_args__ = (
        UniqueConstraint("code", name="uq_campaign_code"),
        {"schema": Schemas.CORE},
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("security.users.id"), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    crop_id: Mapped[int] = mapped_column(ForeignKey("operations.crops.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="PLANIFICADA")

    crop = relationship("Crop", lazy="selectin")
