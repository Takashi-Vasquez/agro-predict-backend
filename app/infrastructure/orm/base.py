from app.infrastructure.database.base import Base, Schemas

from app.infrastructure.orm.security.user import User
from app.infrastructure.orm.operations.crop import Crop
from app.infrastructure.orm.operations.variety import Variety
from app.infrastructure.orm.general.prediction import Prediction
from app.infrastructure.orm.general.training_field import TrainingField
from app.infrastructure.orm.general.training_record import TrainingRecord
from app.infrastructure.orm.general.trained_model import TrainedModel
from app.infrastructure.orm.general.campaign import Campaign
from app.infrastructure.orm.monitoring.weather import WeatherReading
from app.infrastructure.orm.security.profile import Profile
from app.infrastructure.orm.security.user_role import UserRole
from app.infrastructure.orm.security.menu import Menu
from app.infrastructure.orm.security.permission import Permission
from app.infrastructure.orm.security.menu_permission import MenuPermission
from app.infrastructure.orm.security.role_permission_details import RolePermissionDetail
from app.infrastructure.orm.security.role_permissions import RolePermission
from app.infrastructure.orm.core.catalog import Catalog
from app.infrastructure.orm.core.catalog_detail import CatalogDetail
from app.infrastructure.orm.core.company import Company
from app.infrastructure.orm.security.user_company import UserCompany

__all__ = [
    "Base",
    "User",
    "Crop",
    "Variety",
    "Prediction",
    "TrainingField",
    "TrainingRecord",
    "TrainedModel",
    "Campaign",
    "WeatherReading",
    "Profile",
    "RolePermission",
    "RolePermissionDetail",
    "UserRole",
    "Menu",
    "Permission",
    "MenuPermission",
    "Catalog",
    "CatalogDetail",
    "Company",
    "UserCompany",
]
