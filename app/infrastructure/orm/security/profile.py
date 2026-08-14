from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class Profile(BitacoraMixin, Base):
    __tablename__ = "profiles"
    __table_args__ = {"schema": Schemas.SECURITY}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user = relationship("User", back_populates="profile", lazy="selectin")
