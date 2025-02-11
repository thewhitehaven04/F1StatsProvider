from functools import cached_property
import fastf1
from fastf1.core import Laps, Telemetry, SessionResults
from pyparsing import lru_cache

from core.models.queries import SessionIdentifier


@lru_cache(maxsize=32)
def get_session(year: str, event: str, session_identifier: SessionIdentifier):
    return fastf1.get_session(year=int(year), identifier=session_identifier, gp=event)


class SessionLoader:

    def __init__(
        self, year: str, event: str, session_identifier: SessionIdentifier
    ) -> None:
        self._session = fastf1.get_session(
            year=int(year), identifier=session_identifier, gp=event
        )

    @cached_property
    def laps(self) -> Laps:
        self._session.load(laps=True, telemetry=False, weather=False, messages=False)
        return self._session.laps

    @cached_property
    def results(self) -> SessionResults:
        self._session.load(laps=True, telemetry=False, weather=False, messages=True)
        return self._session.results

    @cached_property
    def car_data(self) -> Telemetry:
        self._session.load(laps=False, telemetry=True, weather=False, messages=False)
        return self._session.car_data

    @cached_property
    def lap_telemetry(self) -> Laps:
        self._session.load(laps=True, telemetry=True, weather=False, messages=False)
        return self._session.laps

    @cached_property
    def session(self):
        self._session.load(laps=True, telemetry=False, weather=True, messages=False)
        return self._session

    def load_all(self):
        self._session.load(laps=True, telemetry=True, weather=False, messages=True)


@lru_cache(maxsize=32)
def get_loader(
    year: str, event: str, session_identifier: SessionIdentifier
) -> SessionLoader:
    return SessionLoader(year, event, session_identifier)
