from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.monitoring.weather import WeatherReading
from app.domain.repositories.monitoring.weather_repository import WeatherReadingRepository
from app.infrastructure.orm.monitoring.weather import WeatherReading as WeatherReadingModel


class WeatherReadingRepositoryImpl(WeatherReadingRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, reading_id: int) -> WeatherReading | None:
        stmt = select(WeatherReadingModel).where(
            WeatherReadingModel.id == reading_id,
            WeatherReadingModel.status != "DELETED",
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def get_latest(self, location: str) -> WeatherReading | None:
        stmt = (
            select(WeatherReadingModel)
            .where(
                WeatherReadingModel.location == location,
                WeatherReadingModel.status != "DELETED",
            )
            .order_by(WeatherReadingModel.recorded_at.desc())
            .limit(1)
        )
        orm = self.db.scalar(stmt)
        return self._to_entity(orm) if orm else None

    def get_by_date_range(
        self, location: str, start: datetime, end: datetime
    ) -> list[WeatherReading]:
        stmt = (
            select(WeatherReadingModel)
            .where(
                WeatherReadingModel.location == location,
                WeatherReadingModel.status != "DELETED",
                WeatherReadingModel.recorded_at >= start,
                WeatherReadingModel.recorded_at <= end,
            )
            .order_by(WeatherReadingModel.recorded_at.asc())
        )
        return [self._to_entity(o) for o in self.db.scalars(stmt).all()]

    def create(self, **kwargs) -> WeatherReading:
        orm = WeatherReadingModel(**kwargs)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_entity(orm)

    @staticmethod
    def _to_entity(orm: WeatherReadingModel) -> WeatherReading:
        return WeatherReading(
            id=orm.id,
            crop_id=orm.crop_id,
            location=orm.location,
            latitude=orm.latitude,
            longitude=orm.longitude,
            weather_code=orm.weather_code,
            temperature=orm.temperature,
            temperature_max=orm.temperature_max,
            temperature_min=orm.temperature_min,
            apparent_temperature=orm.apparent_temperature,
            humidity=orm.humidity,
            precipitation=orm.precipitation,
            precipitation_probability=orm.precipitation_probability,
            wind_speed=orm.wind_speed,
            wind_direction_degrees=orm.wind_direction_degrees,
            pressure=orm.pressure,
            uv_index=orm.uv_index,
            recorded_at=orm.recorded_at,
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            deleted_at=orm.deleted_at,
        )
