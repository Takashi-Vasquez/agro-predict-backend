from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class User(BitacoraMixin, Base):
    __tablename__ = "users"
    __table_args__ = {"schema": Schemas.AUTH}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    profile = relationship("Profile", back_populates="user", uselist=False, lazy="selectin")
    user_roles = relationship("UserRole", back_populates="user", lazy="selectin")
