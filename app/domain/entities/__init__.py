from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    id: int = 0
    email: str = ""
    hashed_password: str = ""
    is_admin: bool = False
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None


@dataclass
class Crop:
    id: int = 0
    owner_id: int = 0
    name: str = ""
    variety: str = ""
    category: str = ""
    cycle: int = 0
    temperature: str = ""
    water: str = ""
    color: str = ""
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None


@dataclass
class Prediction:
    id: int = 0
    user_id: int = 0
    crop_id: int | None = None
    predicted_crop: str = ""
    probability: float = 0.0
    N: float = 0.0
    P: float = 0.0
    K: float = 0.0
    temperature: float = 0.0
    humidity: float = 0.0
    ph: float = 0.0
    rainfall: float = 0.0
    error_message: str | None = None
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None


@dataclass
class Profile:
    id: int = 0
    user_id: int = 0
    first_name: str = ""
    last_name: str = ""
    phone: str | None = None
    age: int | None = None
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None


@dataclass
class Role:
    id: int = 0
    name: str = ""
    description: str | None = None
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None


@dataclass
class Menu:
    id: int = 0
    code: str = ""
    parent_id: int | None = None
    name: str = ""
    icon: str | None = None
    route: str | None = None
    order_index: int = 0
    badge: str | None = None
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None


@dataclass
class Permission:
    id: int = 0
    code: str = ""
    name: str = ""
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None


@dataclass
class UserRole:
    id: int = 0
    user_id: int = 0
    role_id: int = 0
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None


@dataclass
class MenuPermission:
    id: int = 0
    menu_id: int = 0
    permission_id: int = 0
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None


@dataclass
class RoleMenuPermission:
    id: int = 0
    role_id: int = 0
    menu_id: int = 0
    permission_id: int = 0
    status: str = "ACTIVE"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
