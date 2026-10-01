from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.monitoring.weather import WeatherReading


class WeatherReadingRepository(ABC):
    @abstractmethod
    def get(self, reading_id: int) -> WeatherReading | None: ...

    @abstractmethod
    def get_latest(self, location: str) -> WeatherReading | None: ...

    @abstractmethod
    def get_by_date_range(
        self, location: str, start: datetime, end: datetime
    ) -> list[WeatherReading]: ...

    @abstractmethod
    def create(self, **kwargs) -> WeatherReading: ...
