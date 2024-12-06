import fastf1
import pandas
from core.models.queries import SessionIdentifier
from fastf1.core import SessionResults, DataNotLoadedError, Laps, Session

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
    def _resolve_racelike_data(data: SessionResults, laps: Laps):
        pass

    @staticmethod
    def _resolve_practice_data(data: SessionResults, laps: Laps):
        temp = (
            data[
                [
                    "DriverNumber",
                    "FullName",
                    "TeamName",
                    "TeamId",
                    "CountryCode",
                ]
            ]
            .rename(
                columns={
                    "FullName": "Driver",
                }
            )
            .assign(Time=laps.groupby("DriverNumber").agg({"LapTime": "min"}))
            .transform(
                {
                    "DriverNumber": lambda x: pandas.to_numeric(x, "coerce", "integer"),
                    "Driver": transformers.identity,
                    "TeamName": transformers.identity,
                    "TeamId": transformers.identity,
                    "CountryCode": transformers.identity,
                    "Time": transformers.laptime_to_seconds,
                }
            )
            .sort_values(by=["Time"])
            .to_dict(orient="records")
        )
        return temp

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
            .rename(
                columns={
                    "FullName": "Driver",
                }
            )
            .to_dict(orient="records")
        )

    def _get_session(
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ) -> Session:
        session = fastf1.get_session(
            year=year, identifier=session_identifier, gp=grand_prix
        )
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        return session

    async def get(
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ):
        session = self._get_session(year, session_identifier, grand_prix)

        if (
            session_identifier == SessionIdentifier.QUALIFYING
            or session_identifier == SessionIdentifier.SPRINT_QUALIFYING
        ):
            return await self.retry(
                self._resolve_qualifying_data, session.results, session.laps
            )
        elif session_identifier in [
            SessionIdentifier.FP1,
            SessionIdentifier.FP2,
            SessionIdentifier.FP3,
        ]:
            return await self.retry(
                self._resolve_practice_data, session.results, session.laps
            )

        return await self.retry(
            self._resolve_racelike_data, session.results, session.laps
        )
