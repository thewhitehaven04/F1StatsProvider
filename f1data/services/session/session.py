from fastapi import logger
import fastf1
from fastf1.core import Laps, SessionResults
from pandas import DataFrame
from pyparsing import lru_cache
from fastf1.core import DataNotLoadedError
from anyio import Lock

from core.models.queries import SessionIdentifier
from utils.retry import Retry


class SessionLoader:
    """The loader is used to minimize the amount of data loaded"""

    def __init__(
        self,
        year: str,
        round: int | str,
        session_identifier: SessionIdentifier | int,
        is_testing: bool,
    ) -> None:
        self._session = (
            fastf1.get_testing_session(
                year=int(year),
                test_number=int(round),
                session_number=session_identifier,
            )
            if is_testing and isinstance(session_identifier, int)
            else fastf1.get_session(
                year=int(year), identifier=session_identifier, gp=round
            )
        )
        self.retry = Retry(
            polling_interval_seconds=1,
            attempt_count=3,
            ignored_exceptions=(DataNotLoadedError,),
        )

        self._has_essentials_loaded = False
        self._has_loaded_laps = False
        self._has_loaded_telemetry = False
        self._has_loaded_messages = False
        self._has_loaded_weather = False

        self.lock = Lock()

    @staticmethod
    def get_is_testing(year: str, round: int):
        if round == 0:
            return True
        elif year in ["2018", "2019", "2022"] and round == 1:
            return True
        return False

    @property
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

    async def fetch_lap_telemetry(self) -> Laps:
        async with self.lock:
            logger.logger.warning("Under lock")
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

    @property
    async def lap_telemetry(self) -> Laps:
        if self._has_loaded_telemetry:
            return self._session.laps

        return await self.fetch_lap_telemetry()

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


@lru_cache(maxsize=48)
def get_loader(
    year: str, round: int, session_identifier: SessionIdentifier | int, is_testing: bool = False
) -> SessionLoader:
    return SessionLoader(year, round, session_identifier, is_testing)
