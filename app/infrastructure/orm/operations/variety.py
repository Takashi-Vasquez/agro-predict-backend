from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class Variety(BitacoraMixin, Base):
    __tablename__ = "varieties"
    __table_args__ = {"schema": Schemas.OPERATIONS}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
