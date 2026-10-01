from datetime import datetime, timezone

from app.domain.repositories.monitoring.weather_repository import WeatherReadingRepository
from app.infrastructure.config.settings import get_settings
from app.infrastructure.external.open_meteo_client import fetch_current_weather


class FetchAndStoreWeatherUseCase:
    def __init__(self, weather_repo: WeatherReadingRepository) -> None:
        self.weather_repo = weather_repo

    async def execute(self) -> bool:
        settings = get_settings()
        data = await fetch_current_weather(settings.WEATHER_LAT, settings.WEATHER_LON)

        if data is None:
            return False

        current = data.get("current", {})
        daily = data.get("daily", {})

        now = datetime.now(timezone.utc)

        self.weather_repo.create(
            location=settings.WEATHER_LOCATION,
            latitude=settings.WEATHER_LAT,
            longitude=settings.WEATHER_LON,
            weather_code=current.get("weather_code", 0),
            temperature=current.get("temperature_2m", 0.0),
            temperature_max=(daily.get("temperature_2m_max", [0.0]))[0] if daily.get("temperature_2m_max") else 0.0,
            temperature_min=(daily.get("temperature_2m_min", [0.0]))[0] if daily.get("temperature_2m_min") else 0.0,
            apparent_temperature=current.get("apparent_temperature", 0.0),
            humidity=current.get("relative_humidity_2m", 0),
            precipitation=current.get("precipitation", 0.0),
            precipitation_probability=(daily.get("precipitation_probability_max", [0]))[0] if daily.get("precipitation_probability_max") else 0,
            wind_speed=current.get("wind_speed_10m", 0.0),
            wind_direction_degrees=current.get("wind_direction_10m", 0.0),
            pressure=current.get("surface_pressure", 0.0),
            uv_index=(daily.get("uv_index_max", [0.0]))[0] if daily.get("uv_index_max") else 0.0,
            recorded_at=now,
        )

        return True
