import fastf1
from core.models.queries import SessionIdentifier
from fastf1.core import SessionResults, DataNotLoadedError

from utils import transformers
from utils.retry import Retry


class ResultsDataResolver:
    def __init__(self):
        self.retry = Retry(
            polling_interval_seconds=0.2,
            timeout_seconds=30,
            ignored_exceptions=(DataNotLoadedError,),
        )

    @staticmethod
    def _resolve(data: SessionResults):
        return (
            data[
                [
                    "DriverNumber",
                    "FullName",
                    "TeamName",
                    "TeamId",
                    "Position",
                    "Time",
                    "CountryCode",
                ]
            ]
            .transform(
                {
                    "DriverNumber": transformers.int_or_null,
                    "FullName": transformers.identity,
                    "TeamName": transformers.identity,
                    "TeamId": transformers.identity,
                    "Position": transformers.int_or_null,
                    "Time": transformers.laptime_to_seconds,
                    "CountryCode": transformers.identity,
                }
            )
            .to_dict(orient="records")
        )

    @staticmethod
    def _resolve_session_data(data: SessionResults):
        return ResultsDataResolver._resolve(data)

    @staticmethod
    def _resolve_qualifying_data(data: SessionResults):
        return (
            data[
                [
                    "DriverNumber",
                    "FullName",
                    "TeamName",
                    "TeamId",
                    "Position",
                    "Q1",
                    "Q2",
                    "Q3",
                    "CountryCode",
                ]
            ]
            .transform(
                {
                    "DriverNumber": transformers.int_or_null,
                    "FullName": transformers.identity,
                    "TeamName": transformers.identity,
                    "TeamId": transformers.identity,
                    "Position": transformers.int_or_null,
                    "Q1": transformers.laptime_to_seconds,
                    "Q2": transformers.laptime_to_seconds,
                    "Q3": transformers.laptime_to_seconds,
                    "CountryCode": transformers.identity,
                }
            )
            .to_dict(orient="records")
        )

    def _get_results(
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ) -> SessionResults:
        session = fastf1.get_session(
            year=year, identifier=session_identifier, gp=grand_prix
        )
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        return session.results

    async def get(
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ):
        results = self._get_results(year, session_identifier, grand_prix)

        if session_identifier == SessionIdentifier.QUALIFYING or session_identifier == SessionIdentifier.SPRINT_QUALIFYING:
            return await self.retry(self._resolve_qualifying_data, results)

        return await self.retry(self._resolve_session_data, results)
