import fastf1
from core.models.queries import SessionIdentifier
from utils.retry import Retry
from fastf1.core import DataNotLoadedError


class SessionLoader:

    def __init__(
        self, year: str, session_identifier: SessionIdentifier, grand_prix: str
    ) -> None:
        self.poll = Retry(
            polling_interval_seconds=0.2,
            timeout_seconds=30,
            ignored_exceptions=(DataNotLoadedError,),
        )
        self._session = fastf1.get_session(
            year=int(year), identifier=session_identifier, gp=grand_prix
        )

    @property
    def session(self):
        return self._session

    @property
    async def laps(self):
        self._session.load(laps=True, telemetry=False, weather=False, messages=False)   
        return await self.poll(lambda: self._session.laps)

    @property
    async def car_data(self):
        self._session.load(laps=False, telemetry=True, weather=False, messages=False)   
        return await self.poll(lambda: self._session.car_data)

    @property
    async def lap_telemetry(self):
        self._session.load(laps=True, telemetry=True, weather=False, messages=False)   
        return await self.poll(lambda: self._session.laps)
