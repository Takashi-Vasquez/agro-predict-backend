from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, BitacoraMixin, Schemas


class Permission(BitacoraMixin, Base):
    __tablename__ = "permissions"
    __table_args__ = {"schema": Schemas.SECURITY}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    menu_permissions = relationship("MenuPermission", back_populates="permission", lazy="selectin")
    role_menu_permissions = relationship("RoleMenuPermission", back_populates="permission", lazy="selectin")
