from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.presentation.schemas import BaseReadSchema


class CampaignCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(min_length=1, max_length=50, description="Código único de la campaña")
    name: str = Field(min_length=1, max_length=255, description="Nombre de la campaña")
    start_date: date = Field(alias="startDate", description="Fecha estimada de inicio")
    end_date: date = Field(alias="endDate", description="Fecha estimada de fin")
    crop_id: int = Field(alias="cropId", gt=0, description="ID del cultivo asociado")
    status: str | None = None


class CampaignUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")
    crop_id: int | None = Field(default=None, alias="cropId", gt=0)
    status: str | None = None


class CampaignRead(BaseReadSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(alias="id")
    user_id: int = Field(alias="userId")
    code: str
    name: str
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    crop_id: int = Field(alias="cropId")
    crop_name: str = Field(default="", alias="cropName")
    status: str
    created_at: datetime
    updated_at: datetime
