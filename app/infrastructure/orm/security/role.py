from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class Role(BitacoraMixin, Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": Schemas.SECURITY}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user_roles = relationship("UserRole", back_populates="role", lazy="selectin")
    role_menu_permissions = relationship("RoleMenuPermission", back_populates="role", lazy="selectin")
