from typing import Annotated
from fastapi import APIRouter, Depends 


from core.models.queries import SessionIdentifier, SessionQueryFilter, TelemetryRequest
from services.laps.models.laps import LapSelectionData
from services.laps.resolver import get_resolved_laptime_data
from services.session.session import SessionLoader
from services.telemetry.models.Telemetry import DriverTelemetryData, TelemetryComparison
from services.telemetry.resolver import get_interpolated_telemetry_comparison, get_telemetry

SessionRouter = APIRouter(tags=["Session level data"])


@SessionRouter.post(
    "/season/{year}/event/{event}/session/{session_identifier}/laps",
    response_model=LapSelectionData,
)
async def get_session_laptimes(
    loader: Annotated[SessionLoader, Depends()],
    body: SessionQueryFilter,
):
    """
    Retrieve laptime data for given session
    """
    return await get_resolved_laptime_data(loader, body.queries)


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
    return await get_interpolated_telemetry_comparison(SessionLoader(year, event, session_identifier), body)


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
    return await get_telemetry(SessionLoader(year, event, session_identifier), driver, lap)

