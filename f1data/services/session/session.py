from functools import cached_property
import fastf1
from fastf1.core import Laps, SessionResults
from pandas import DataFrame
from pyparsing import lru_cache
from fastf1.core import DataNotLoadedError

from core.models.queries import SessionIdentifier
from utils.retry import Retry


class SessionLoader:
    """The loader is used to minimize the amount of data loaded"""

    def __init__(
        self, year: str, event: str, session_identifier: SessionIdentifier
    ) -> None:
        self._session = fastf1.get_session(
            year=int(year), identifier=session_identifier, gp=event
        )
        self.retry = Retry(
            polling_interval_seconds=0.5,
            timeout_seconds=10,
            ignored_exceptions=(DataNotLoadedError,),
        )

        self._has_essentials_loaded = False
        self._has_loaded_laps = False
        self._has_loaded_telemetry = False
        self._has_loaded_messages = False
        self._has_loaded_weather = False

    @cached_property
    def laps(self) -> Laps:
        def fetch_laps() -> Laps:
            self._session.load(
                laps=True, telemetry=False, weather=False, messages=False
            )
            if self._session.laps is not None:
                self._has_loaded_laps = True
                return self._session.laps
            raise DataNotLoadedError

        if self._has_loaded_laps:
            return self._session.laps

        return self.retry(fetch_laps)

    @property
    def results(self) -> SessionResults:
        def fetch_results() -> SessionResults:
            self._session.load(
                laps=False, telemetry=False, weather=False, messages=False
            )
            if self._session.results is not None:
                return self._session.results
            raise DataNotLoadedError

        if self._has_essentials_loaded and self._session.results is not None:
            return self._session.results
        return self.retry(fetch_results)

    @cached_property
    def lap_telemetry(self) -> Laps:
        def fetch_lap_telemetry() -> Laps:
            if self._has_loaded_laps:
                self._session.load(
                    laps=False, telemetry=True, weather=False, messages=False
                )
            else:
                self._session.load(
                    laps=True, telemetry=True, weather=False, messages=False
                )
            if self._session.laps is not None:
                self._has_loaded_telemetry = True
                return self._session.laps
            raise DataNotLoadedError

        if self._has_loaded_telemetry:
            return self._session.laps

        return self.retry(fetch_lap_telemetry)

    @property
    def session_info(self) -> dict:
        def fetch_session_info() -> dict:
            self._session.load(
                laps=False, telemetry=False, weather=False, messages=False
            )
            if self._session.session_info:
                self._has_essentials_loaded = True
                return self._session.session_info
            else:
                raise DataNotLoadedError

        if self._has_essentials_loaded and self._session.session_info:
            return self._session.session_info
        return self.retry(fetch_session_info)

    @property
    def weather(self):
        def fetch_weather_data() -> DataFrame:
            self._session.load(
                laps=False,
                telemetry=False,
                weather=True,
                messages=False,
            )
            if self._session.weather_data is not None:
                self._has_loaded_weather = True
                return self._session.weather_data
            else:
                raise DataNotLoadedError

        if self._has_loaded_weather and self._session.weather_data is not None:
            return self._session.weather_data
        return self.retry(fetch_weather_data)

    @cached_property
    def session(self):
        self._session.load(
            laps=False if self._has_loaded_laps else True,
            telemetry=False if self._has_loaded_telemetry else True,
            weather=False if self._has_loaded_weather else True,
            # there is no case where we need to load messages
            messages=False,
        )
        return self._session


@lru_cache(maxsize=32)
def get_loader(
    year: str, event: str, session_identifier: SessionIdentifier
) -> SessionLoader:
    return SessionLoader(year, event, session_identifier)
