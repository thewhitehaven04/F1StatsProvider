import fastf1
from fastf1.core import DataNotLoadedError, Session, Laps, Telemetry, SessionResults

from core.models.queries import SessionIdentifier
from utils.retry import Retry


def get_cached_session(
    year: str, session_identifier: SessionIdentifier, grand_prix: str
) -> Session:
    return fastf1.get_session(
        year=int(year), identifier=session_identifier, gp=grand_prix
    )


class SessionLoader:

    def __init__(
        self, year: str, event: str, session_identifier: SessionIdentifier
    ) -> None:
        self.poll = Retry(
            polling_interval_seconds=0.05,
            timeout_seconds=30,
            ignored_exceptions=(DataNotLoadedError,),
        )
        self.session = get_cached_session(year, session_identifier, event)

    @property
    async def laps(self) -> Laps:
        try:
            return self.session.laps
        except DataNotLoadedError:
            self.session.load(laps=True, telemetry=False, weather=False, messages=False)
        finally:
            return await self.poll(lambda: self.session.laps)

    @property
    async def results(self) -> SessionResults:
        try:
            return self.session.results
        except DataNotLoadedError:
            self.session.load(laps=True, telemetry=False, weather=False, messages=True)
        finally:
            return await self.poll(lambda: self.session.results)

    @property
    async def car_data(self) -> Telemetry:
        self.session.load(laps=False, telemetry=True, weather=False, messages=False)
        return await self.poll(lambda: self.session.car_data)

    @property
    async def lap_telemetry(self) -> Laps:
        try:
            return self.session.laps
        except DataNotLoadedError:
            self.session.load(laps=True, telemetry=True, weather=False, messages=False)
        finally:
            return await self.poll(lambda: self.session.laps)

    def load_all(self):
        self.session.load(laps=True, telemetry=True, weather=False, messages=True)
