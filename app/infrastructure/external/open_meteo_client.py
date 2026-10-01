from typing import Any

import httpx

OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"


async def fetch_current_weather(lat: float, lon: float) -> dict[str, Any] | None:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
            "surface_pressure",
        ]),
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "uv_index_max",
        ]),
        "timezone": "America/Lima",
        "forecast_days": 1,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(OPEN_METEO_BASE, params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None


async def fetch_forecast(lat: float, lon: float, days: int = 7) -> dict[str, Any] | None:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "weather_code",
            "uv_index_max",
        ]),
        "timezone": "America/Lima",
        "forecast_days": days,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(OPEN_METEO_BASE, params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None
