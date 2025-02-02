from typing import Annotated
from fastapi import APIRouter, Depends, Response


from core.models.queries import SessionQueryFilter, TelemetryRequest
from services.laps.models.laps import LapSelectionData
from services.laps.resolver import get_resolved_laptime_data
from services.session.session import SessionLoader
from services.telemetry.models.Telemetry import DriverTelemetryData, TelemetryComparison
from services.telemetry.resolver import (
    get_interpolated_telemetry_comparison,
    get_telemetries,
    get_telemetry,
)

SessionRouter = APIRouter(tags=["Session level data"])


@SessionRouter.post(
    "/season/{year}/event/{event}/session/{session_identifier}/laps",
    response_model=LapSelectionData,
)
async def get_session_laptimes(
    loader: Annotated[SessionLoader, Depends()],
    body: SessionQueryFilter,
    response: Response
):
    """
    Retrieve laptime data for given session
    """
    response.headers['Cache-Control'] = 'public, max-age=604800'
    return await get_resolved_laptime_data(loader, body.queries)


@SessionRouter.post(
    "/season/{year}/event/{event}/session/{session_identifier}/telemetry/comparison",
    response_model=TelemetryComparison,
)
async def get_session_telemetry(
    loader: Annotated[SessionLoader, Depends()],
    body: list[TelemetryRequest],
):
    return await get_interpolated_telemetry_comparison(loader, body)


@SessionRouter.get(
    "/season/{year}/event/{event}/session/{session_identifier}/lap/{lap}/driver/{driver}/telemetry",
    response_model=DriverTelemetryData,
)
async def get_session_lap_driver_telemetry(
    loader: Annotated[SessionLoader, Depends()],
    lap: str,
    driver: str,
    response: Response
):
    response.headers['Cache-Control'] = 'public, max-age=604800'
    return await get_telemetry(loader, driver, lap)

@SessionRouter.post("/season/{year}/event/{event}/session/{session_identifier}/telemeries", response_model=list[DriverTelemetryData])
async def get_session_lap_telemetries(
    loader: Annotated[SessionLoader, Depends()],
    body: list[TelemetryRequest],
):
    return await get_telemetries(loader, body) 