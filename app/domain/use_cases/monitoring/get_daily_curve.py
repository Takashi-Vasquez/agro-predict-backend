from datetime import datetime, timedelta, timezone

from app.domain.repositories.monitoring.weather_repository import WeatherReadingRepository
from app.infrastructure.config.settings import get_settings

TZ_LIMA = timezone(timedelta(hours=-5))


class GetDailyCurveUseCase:
    def __init__(self, weather_repo: WeatherReadingRepository) -> None:
        self.weather_repo = weather_repo

    def execute(self) -> dict:
        settings = get_settings()
        location = settings.WEATHER_LOCATION
        now = datetime.now(TZ_LIMA)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        readings = self.weather_repo.get_by_date_range(location, start, end)

        if not readings:
            return {"values": [], "labels": [], "max": 32}

        values = [r.temperature for r in readings]
        labels = [
            r.recorded_at.astimezone(TZ_LIMA).strftime("%H:%M")
            for r in readings
        ]
        max_temp = max(r.temperature_max for r in readings)

        return {
            "values": values,
            "labels": labels,
            "max": max_temp,
        }
