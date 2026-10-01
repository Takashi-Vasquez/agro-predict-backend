from datetime import datetime, timedelta, timezone

from app.domain.repositories.monitoring.weather_repository import WeatherReadingRepository
from app.infrastructure.config.settings import get_settings
from app.infrastructure.external.wmo_mapper import wmo_to_icon

TZ_LIMA = timezone(timedelta(hours=-5))

DAY_NAMES_ES = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
MONTH_NAMES_ES = [
    "", "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
]


class GetForecastUseCase:
    def __init__(self, weather_repo: WeatherReadingRepository) -> None:
        self.weather_repo = weather_repo

    def execute(self, days: int = 7) -> dict:
        settings = get_settings()
        location = settings.WEATHER_LOCATION
        now = datetime.now(TZ_LIMA)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=days)

        readings = self.weather_repo.get_by_date_range(location, start, end)

        daily_data: dict[str, dict] = {}
        for r in readings:
            day_key = r.recorded_at.astimezone(TZ_LIMA).strftime("%Y-%m-%d")
            if day_key not in daily_data:
                daily_data[day_key] = {
                    "temps_max": [],
                    "temps_min": [],
                    "rain_probs": [],
                    "codes": [],
                }
            daily_data[day_key]["temps_max"].append(r.temperature_max)
            daily_data[day_key]["temps_min"].append(r.temperature_min)
            daily_data[day_key]["rain_probs"].append(r.precipitation_probability)
            daily_data[day_key]["codes"].append(r.weather_code)

        dias = []
        for i in range(days):
            day_date = start + timedelta(days=i)
            day_key = day_date.strftime("%Y-%m-%d")

            if day_key in daily_data:
                d = daily_data[day_key]
                max_temp = max(d["temps_max"])
                min_temp = min(d["temps_min"])
                rain = max(d["rain_probs"])
                code = d["codes"][0]
            else:
                max_temp = None
                min_temp = None
                rain = None
                code = 0

            dias.append({
                "day": DAY_NAMES_ES[day_date.weekday()],
                "date": f"{day_date.day} {MONTH_NAMES_ES[day_date.month]}",
                "icon": wmo_to_icon(code),
                "high": max_temp,
                "low": min_temp,
                "rain": rain,
            })

        return {"dias": dias}
