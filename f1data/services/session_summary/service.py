import fastf1

from core.models.queries import SessionIdentifier
from fastf1.core import Session, DataNotLoadedError

from services.session_summary.models.summary import SessionSummary, Summary
from services.session_summary.models.weather import SessionWeather
from utils.retry import Retry


class SessionSummaryService:

    def _get_session(
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ):
        session = fastf1.get_session(
            year=year, identifier=session_identifier, gp=grand_prix
        )
        session.load(laps=False, telemetry=False, weather=True, messages=False)
        return session

    @staticmethod
    def _resolve_weather_data(session: Session):
        weather = session.weather_data
        return SessionWeather(
            air_temp_start=weather["AirTemp"].iloc[0],
            air_temp_finish=weather["AirTemp"].iloc[-1],
            track_temp_start=weather["TrackTemp"].iloc[0],
            track_temp_finish=weather["TrackTemp"].iloc[-1],
            humidity_start=weather["Humidity"].iloc[-1],
            humidity_finish=weather["Humidity"].iloc[-1],
        )

    @staticmethod
    def _resolve_summary_data(session: Session):
        return Summary(
            start_time=session.session_info["StartDate"],
            finish_time=session.session_info["EndDate"],
            session_type=session.session_info["Type"],
            round_name=session.session_info["Meeting"]["Name"],
            official_name=session.session_info["Meeting"]["OfficialName"],
        )

    async def get_session_summary(
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ):
        retry = Retry(
            polling_interval_seconds=0.3,
            timeout_seconds=30,
            ignored_exceptions=(DataNotLoadedError, KeyError),
        )
        session = self._get_session(year, session_identifier, grand_prix)

        weather = await retry(self._resolve_weather_data, session)
        summary = await retry(self._resolve_summary_data, session)

        return SessionSummary(weather=weather, summary=summary)
