from app.domain.entities.operations.crop import Crop
from app.domain.entities.general.prediction import Prediction
from app.domain.entities.general.training_record import TrainingRecord
from app.domain.entities.general.campaign import Campaign
from app.domain.entities.monitoring.weather import WeatherReading
from app.domain.entities.security.user import User
from app.domain.entities.security.role_permissions import RolePermission
from app.domain.entities.security.role_permission_details import RolePermissionDetail
from app.domain.entities.security.menu import Menu
from app.domain.entities.security.permission import Permission
from app.domain.entities.security.profile import Profile
from app.domain.entities.security.user_role import UserRole
from app.domain.entities.security.menu_permission import MenuPermission
from app.domain.entities.security.user_company import UserCompany

__all__ = [
    "Crop",
    "Prediction",
    "TrainingRecord",
    "Campaign",
    "WeatherReading",
    "User",
    "RolePermission",
    "RolePermissionDetail",
    "Menu",
    "Permission",
    "Profile",
    "UserRole",
    "MenuPermission",
    "UserCompany",
]
