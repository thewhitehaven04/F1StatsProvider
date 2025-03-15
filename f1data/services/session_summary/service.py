from core.models.queries import SessionIdentifier

from services.session.session import get_loader
from services.session_summary.models.summary import SessionSummary, Summary
from services.session_summary.models.weather import SessionWeather


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


async def get_session_info(
    year: int, session_identifier: SessionIdentifier | int, round: int, is_testing: bool
):
    loader = get_loader(year, round, session_identifier, is_testing)

    weather = _resolve_weather_data(await loader.weather)
    summary = _resolve_summary_data(await loader.session_info)

    return SessionSummary(weather=weather, summary=summary)