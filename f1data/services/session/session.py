import asyncio
import fastf1
from fastf1.core import DataNotLoadedError, Laps, Telemetry, SessionResults

from core.models.queries import SessionIdentifier


class SessionLoader:

    def __init__(
        self, year: str, event: str, session_identifier: SessionIdentifier
    ) -> None:
        self.session = fastf1.get_session(
            year=int(year), identifier=session_identifier, gp=event
        )

    @property
    def laps(self) -> Laps:
        try:
            return self.session.laps
        except DataNotLoadedError:
            self.session.load(laps=True, telemetry=False, weather=False, messages=False)
        finally:
            return self.session.laps

    @property
    def results(self) -> SessionResults:
        try:
            return self.session.results
        except DataNotLoadedError:
            self.session.load(laps=True, telemetry=False, weather=False, messages=True)
        finally:
            return self.session.results

    @property
    def car_data(self) -> Telemetry:
        try:
            return self.session.car_data
        except DataNotLoadedError:
            self.session.load(laps=False, telemetry=True, weather=False, messages=False)
        finally:
            return self.session.car_data

    @property
    def lap_telemetry(self) -> Laps:
        try:
            return self.session.laps
        except DataNotLoadedError:
            self.session.load(laps=True, telemetry=True, weather=False, messages=False)
        finally:
            return self.session.laps

    @property
    def weather(self):
        try:
            return self.session.weather_data
        except DataNotLoadedError:
            self.session.load(laps=True, telemetry=False, weather=True, messages=False)
        finally:
            return self.session.weather_data

    def load_all(self):
        self.session.load(laps=True, telemetry=True, weather=False, messages=True)
