from datetime import datetime, timedelta, timezone

from app.domain.repositories.monitoring.weather_repository import WeatherReadingRepository
from app.infrastructure.config.settings import get_settings

TZ_LIMA = timezone(timedelta(hours=-5))


class GetAlertsUseCase:
    def __init__(self, weather_repo: WeatherReadingRepository) -> None:
        self.weather_repo = weather_repo

    def execute(self) -> dict:
        settings = get_settings()
        location = settings.WEATHER_LOCATION
        now = datetime.now(TZ_LIMA)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_start = today_start + timedelta(days=1)
        tomorrow_end = tomorrow_start + timedelta(days=1)

        today_readings = self.weather_repo.get_by_date_range(
            location, today_start, tomorrow_start
        )
        tomorrow_readings = self.weather_repo.get_by_date_range(
            location, tomorrow_start, tomorrow_end
        )

        alertas = []

        if tomorrow_readings:
            max_rain_prob = max(r.precipitation_probability for r in tomorrow_readings)
            if max_rain_prob >= 70:
                alertas.append({
                    "icon": "rain",
                    "titulo": "Posibilidad de lluvias",
                    "detalle": f"Se esperan lluvias con {max_rain_prob}% de probabilidad manana.",
                    "nivel": "Moderada",
                })

        if today_readings:
            max_uv = max(r.uv_index for r in today_readings)
            if max_uv >= 8:
                alertas.append({
                    "icon": "sun",
                    "titulo": "Mayor radiacion al mediodia",
                    "detalle": f"Indice UV maximo de {max_uv}. Use protector solar.",
                    "nivel": "Informativa",
                })

        return {"alertas": alertas}
