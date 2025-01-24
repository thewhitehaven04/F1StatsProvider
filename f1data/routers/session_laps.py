from fastapi import APIRouter 


from core.models.queries import SessionIdentifier, SessionQueryFilter, TelemetryRequest
from services.laps.models.laps import LapSelectionData
from services.laps.resolver import get_resolved_laptime_data
from services.telemetry.models.Telemetry import DriverTelemetryData, TelemetryComparison
from services.telemetry.resolver import TelemetryResolver

SessionRouter = APIRouter(tags=["Session level data"])


@SessionRouter.post(
    "/season/{year}/event/{event}/session/{session_identifier}/laps",
    response_model=LapSelectionData,
)
async def get_session_laptimes(
    year: str,
    event: str,
    session_identifier: SessionIdentifier,
    body: SessionQueryFilter,
):
    """
    Retrieve laptime data for given session
    """
    res = await get_resolved_laptime_data(
        session_identifier=session_identifier,
        grand_prix=event,
        year=year,
        queries=body.queries,
    )

    return res


@SessionRouter.post(
    "/season/{year}/event/{event}/session/{session_identifier}/telemetry/comparison",
    response_model=TelemetryComparison
)
async def get_session_telemetry(
    year: str,
    event: str,
    session_identifier: SessionIdentifier,
    body: list[TelemetryRequest],
):
    return await TelemetryResolver(
        year=year, session_identifier=session_identifier, grand_prix=event
    ).get_interpolated_telemetry_comparison(body)


@SessionRouter.get(
    "/season/{year}/event/{event}/session/{session_identifier}/lap/{lap}/driver/{driver}/telemetry",
    response_model=DriverTelemetryData,
)
async def get_session_lap_driver_telemetry(
    year: str,
    event: str,
    session_identifier: SessionIdentifier,
    lap: str,
    driver: str,
):
    return await TelemetryResolver(
        year=year, session_identifier=session_identifier, grand_prix=event
    ).get_telemetry(driver=driver, lap=lap)
