from functools import lru_cache

from fastapi import logger
from pandas import DataFrame
from core.models.queries import SessionIdentifier
from fastf1.core import DataNotLoadedError

from services.session.session import get_session
from services.session_summary.models.summary import SessionSummary, Summary
from services.session_summary.models.weather import SessionWeather
from utils.retry import Retry


def _resolve_weather_data(weather_data):
    return SessionWeather(
        air_temp_start=weather_data["AirTemp"].iloc[0],
        air_temp_finish=weather_data["AirTemp"].iloc[-1],
        track_temp_start=weather_data["TrackTemp"].iloc[0],
        track_temp_finish=weather_data["TrackTemp"].iloc[-1],
        humidity_start=weather_data["Humidity"].iloc[-1],
        humidity_finish=weather_data["Humidity"].iloc[-1],
    )

def _resolve_summary_data(session_info):
    return Summary(
        start_time=session_info["StartDate"],
        finish_time=session_info["EndDate"],
        session_type=session_info["Type"],
        round_name=session_info["Meeting"]["Name"],
        official_name=session_info["Meeting"]["OfficialName"],
    )


@lru_cache(maxsize=16)
def load_summary_data(year: int, session_identifier: SessionIdentifier, grand_prix: str) -> tuple[DataFrame, dict]:
    session = get_session(str(year), grand_prix, session_identifier)
    session.load(laps=True, telemetry=False, weather=True, messages=False)
    if session.weather_data is None or session.session_info is None:
        logger.logger.warning(f"Session {session_identifier} {grand_prix} not loaded")
        raise DataNotLoadedError
    return session.weather_data, session.session_info

def get_session_info(
    year: int, session_identifier: SessionIdentifier, grand_prix: str
):
    retry = Retry(polling_interval_seconds=0.5, timeout_seconds=10, ignored_exceptions=(DataNotLoadedError,))
    weather_data, session_info = retry(load_summary_data, year, session_identifier, grand_prix)

    weather = _resolve_weather_data(weather_data)
    summary = _resolve_summary_data(session_info)

    return SessionSummary(weather=weather, summary=summary)
