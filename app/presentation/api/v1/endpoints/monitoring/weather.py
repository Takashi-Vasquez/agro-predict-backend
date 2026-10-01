from fastapi import APIRouter, Query

from app.presentation.api.deps import CurrentUser, DbDep
from app.presentation.utils.api_response_factory import ApiResponseFactory
from app.infrastructure.repositories.monitoring.weather_reading_repository import WeatherReadingRepositoryImpl
from app.domain.use_cases.monitoring.get_current_weather import GetCurrentWeatherUseCase
from app.domain.use_cases.monitoring.get_forecast import GetForecastUseCase
from app.domain.use_cases.monitoring.get_daily_curve import GetDailyCurveUseCase
from app.domain.use_cases.monitoring.get_alerts import GetAlertsUseCase

router = APIRouter(prefix="/weather", tags=["Monitoring/Weather"])


@router.get("/current")
def get_current_weather(user: CurrentUser, db: DbDep):
    use_case = GetCurrentWeatherUseCase(WeatherReadingRepositoryImpl(db))
    data = use_case.execute()
    return ApiResponseFactory.ok(data, "Clima actual obtenido correctamente")


@router.get("/forecast")
def get_forecast(
    user: CurrentUser,
    db: DbDep,
    days: int = Query(7, ge=1, le=14, description="Numero de dias de pronostico"),
):
    use_case = GetForecastUseCase(WeatherReadingRepositoryImpl(db))
    data = use_case.execute(days=days)
    return ApiResponseFactory.ok(data, "Pronostico obtenido correctamente")


@router.get("/daily-curve")
def get_daily_curve(user: CurrentUser, db: DbDep):
    use_case = GetDailyCurveUseCase(WeatherReadingRepositoryImpl(db))
    data = use_case.execute()
    return ApiResponseFactory.ok(data, "Curva diaria obtenida correctamente")


@router.get("/alerts")
def get_alerts(user: CurrentUser, db: DbDep):
    use_case = GetAlertsUseCase(WeatherReadingRepositoryImpl(db))
    data = use_case.execute()
    return ApiResponseFactory.ok(data, "Alertas obtenidas correctamente")
