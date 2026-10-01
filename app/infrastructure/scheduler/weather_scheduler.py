import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.monitoring.weather_reading_repository import WeatherReadingRepositoryImpl
from app.domain.use_cases.monitoring.fetch_and_store import FetchAndStoreWeatherUseCase

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def weather_job() -> None:
    try:
        db = next(get_db())
        repo = WeatherReadingRepositoryImpl(db)
        use_case = FetchAndStoreWeatherUseCase(repo)
        result = await use_case.execute()
        if result:
            logger.info("Weather data fetched and stored successfully")
        else:
            logger.warning("Failed to fetch weather data from Open-Meteo")
    except Exception as e:
        logger.error(f"Error in weather job: {e}")


def start_scheduler() -> None:
    scheduler.add_job(
        weather_job,
        CronTrigger(minute="*/30"),
        id="weather_fetch",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Weather scheduler started (every 30 minutes)")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Weather scheduler stopped")
