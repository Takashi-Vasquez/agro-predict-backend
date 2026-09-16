from abc import ABC, abstractmethod

from app.domain.entities.monitoring.weather import Weather


class WeatherRepository(ABC):
    @abstractmethod
    def get(self, weather_id: int) -> Weather | None: ...

    @abstractmethod
    def list_for_crop(self, crop_id: int, *, offset: int = 0, limit: int = 100) -> list[Weather]: ...

    @abstractmethod
    def create(self, **kwargs) -> Weather: ...
