from functools import cached_property
import fastf1
from fastf1.core import Laps, Telemetry, SessionResults, DataNotLoadedError
from pyparsing import lru_cache

from core.models.queries import SessionIdentifier

class SessionLoader:

    def __init__(
        self, year: str, event: str, session_identifier: SessionIdentifier
    ) -> None:
        self.session = fastf1.get_session(
            year=int(year), identifier=session_identifier, gp=event
        )

    @cached_property
    def laps(self) -> Laps:
        self.session.load(laps=True, telemetry=False, weather=False, messages=False)
        return self.session.laps

    @cached_property
    def results(self) -> SessionResults:
        self.session.load(laps=True, telemetry=False, weather=False, messages=True)
        return self.session.results

    @cached_property
    def car_data(self) -> Telemetry:
        self.session.load(laps=False, telemetry=True, weather=False, messages=False)
        return self.session.car_data

    @cached_property
    def lap_telemetry(self) -> Laps:
        self.session.load(laps=True, telemetry=True, weather=False, messages=False)
        return self.session.laps

    @cached_property
    def weather(self):
        self.session.load(laps=True, telemetry=False, weather=True, messages=False)
        return self.session.weather_data
    
    @cached_property
    def session_info(self):
        self.session.load(laps=True, telemetry=False, weather=False, messages=False)
        return self.session

    def load_all(self):
        self.session.load(laps=True, telemetry=True, weather=False, messages=True)


@lru_cache(maxsize=64)
def get_loader(
    year: str, event: str, session_identifier: SessionIdentifier
) -> SessionLoader:
    return SessionLoader(year, event, session_identifier)
