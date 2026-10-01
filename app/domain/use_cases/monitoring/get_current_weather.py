from datetime import datetime, timedelta, timezone

from app.domain.repositories.monitoring.weather_repository import WeatherReadingRepository
from app.infrastructure.config.settings import get_settings
from app.infrastructure.external.wmo_mapper import wmo_to_description, wmo_to_icon

TZ_LIMA = timezone(timedelta(hours=-5))

STALE_THRESHOLD_MINUTES = 30


class GetCurrentWeatherUseCase:
    def __init__(self, weather_repo: WeatherReadingRepository) -> None:
        self.weather_repo = weather_repo

    def execute(self) -> dict:
        settings = get_settings()
        location = settings.WEATHER_LOCATION
        reading = self.weather_repo.get_latest(location)

        if reading is None:
            return {
                "ubicacion": location,
                "fecha": None,
                "stale": True,
                "temperatura_actual": None,
                "descripcion": "Sin datos",
                "icono": "cloud",
                "maxima": None,
                "minima": None,
                "sensacion_termica": None,
                "metrics": [],
            }

        now = datetime.now(TZ_LIMA)
        diff = now - reading.recorded_at.astimezone(TZ_LIMA)
        is_stale = diff.total_seconds() > STALE_THRESHOLD_MINUTES * 60

        return {
            "ubicacion": reading.location,
            "fecha": reading.recorded_at.isoformat(),
            "stale": is_stale,
            "temperatura_actual": reading.temperature,
            "descripcion": wmo_to_description(reading.weather_code),
            "icono": wmo_to_icon(reading.weather_code),
            "maxima": reading.temperature_max,
            "minima": reading.temperature_min,
            "sensacion_termica": reading.apparent_temperature,
            "metrics": [
                {
                    "label": "Humedad relativa",
                    "value": reading.humidity,
                    "unit": "%",
                    "detail": f"Humedad relativa actual: {reading.humidity}%",
                    "icon": "drop",
                },
                {
                    "label": "Velocidad del viento",
                    "value": round(reading.wind_speed * 3.6, 1),
                    "unit": "km/h",
                    "detail": f"Viento a {round(reading.wind_speed * 3.6, 1)} km/h",
                    "icon": "wind",
                },
                {
                    "label": "Probabilidad de lluvia",
                    "value": reading.precipitation_probability,
                    "unit": "%",
                    "detail": f"Probabilidad de precipitacion: {reading.precipitation_probability}%",
                    "icon": "rain",
                },
                {
                    "label": "Indice UV",
                    "value": reading.uv_index,
                    "unit": "/ 11",
                    "detail": f"Indice UV: {reading.uv_index}",
                    "icon": "sun",
                },
            ],
        }
