from core.models.queries import SessionIdentifier
from fastf1.core import Session

from services.session.session import SessionLoader
from services.session_summary.models.summary import SessionSummary, Summary
from services.session_summary.models.weather import SessionWeather


class SessionSummaryService:

    @staticmethod
    def _resolve_weather_data(weather):
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

    def get_session_summary(
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ):
        loader = SessionLoader(str(year), grand_prix, session_identifier)
        weather = loader.weather

        weather = self._resolve_weather_data(weather)
        summary = self._resolve_summary_data(loader.session)

        return SessionSummary(weather=weather, summary=summary)
