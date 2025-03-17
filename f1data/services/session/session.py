from functools import cache
from threading import Lock
from fastapi import logger
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

        self._has_essentials_loaded = False
        self._has_loaded_laps = False
        self._has_loaded_telemetry = False
        self._has_loaded_messages = False
        self._has_loaded_weather = False

        self.year = year
        self.round = round 
        self.session_identifier = session_identifier

        self.essentials_lock = Lock()
        self.laps_lock = Lock()
        self.telemetry_lock = Lock()
        self.weather_lock = Lock()

    @staticmethod
    def get_is_testing(year: str, round: int):
        if round == 0:
            return True
        elif year in ["2018", "2019", "2022"] and round == 1:
            return True
        return False

    def _fetch_laps(self) -> Laps:
        with self.laps_lock:
            self._session.load(
                laps=True, telemetry=False, weather=False, messages=False
            )
            if self._session.laps is not None:
                self._has_loaded_laps = True
                return self._session.laps
            raise DataNotLoadedError

    @property
    def laps(self) -> Laps:
        if self._has_loaded_laps:
            return self._session.laps

        return self._fetch_laps()

    def _fetch_results(self) -> SessionResults:
        with self.essentials_lock:
            self._session.load(
                laps=False, telemetry=False, weather=False, messages=False
            )
            if self._session.results is not None:
                return self._session.results
            raise DataNotLoadedError

    @property
    def results(self) -> SessionResults:
        if self._has_essentials_loaded and self._session.results is not None:
            return self._session.results

        return self._fetch_results()

    def fetch_lap_telemetry(self) -> Laps:
        with self.telemetry_lock:
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
    def lap_telemetry(self) -> Laps:
        if self._has_loaded_telemetry:
            return self._session.laps

        return self.fetch_lap_telemetry()

    def _fetch_session_info(self) -> dict:
        with self.essentials_lock:
            self._session.load(
                laps=False, telemetry=False, weather=False, messages=False
            )
            if self._session.session_info:
                self._has_essentials_loaded = True
                return self._session.session_info
            else:
                raise DataNotLoadedError

    @property
    def session_info(self) -> dict:
        if self._has_essentials_loaded and self._session.session_info:
            return self._session.session_info

        return self._fetch_session_info()

    def _fetch_weather_data(self) -> DataFrame:
        with self.weather_lock: 
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

    @property
    def weather(self):
        if self._has_loaded_weather and self._session.weather_data is not None:
            return self._session.weather_data

        return self._fetch_weather_data()

    @property
    def circuit_info(self):
        if self._has_loaded_telemetry and self._has_loaded_laps:
            circuit_info = self._session.get_circuit_info()
            if circuit_info: 
                return circuit_info
            raise DataNotLoadedError

        self.fetch_lap_telemetry()

        circuit_info = self._session.get_circuit_info()
        if circuit_info: 
            return circuit_info

        raise DataNotLoadedError
    
    def fetch_all_data(self):
        logger.logger.warning('Loading data for %s %s %s', self.year, self.session_identifier, self.round)
        with self.laps_lock:
            with self.telemetry_lock:
                with self.weather_lock: 
                    self._session.load(laps=True, telemetry=True, weather=True, messages=False)
                    self._has_loaded_laps = True
                    self._has_loaded_telemetry = True
                    self._has_loaded_weather = True

@lru_cache(maxsize=48)
def get_loader(
    year: str,
    round: int,
    session_identifier: SessionIdentifier | int,
    is_testing: bool = False,
) -> SessionLoader:
    return SessionLoader(year, round, session_identifier, is_testing)
