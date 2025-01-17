from fastapi import APIRouter, Depends


from core.models.queries import SessionIdentifier, SessionQueryFilter, TelemetryRequest
from services.laps.models.laps import DriverLapData
from services.laps.resolver import LapDataResolver
from services.telemetry.models.Telemetry import DriverTelemetryData
from services.telemetry.resolver import TelemetryResolver

SessionRouter = APIRouter(tags=["Session level data"])


@SessionRouter.post(
    "/season/{year}/event/{event}/session/{session_identifier}/laps",
    response_model=list[DriverLapData],
)
async def get_session_laptimes(
    year: str,
    event: str,
    session_identifier: SessionIdentifier,
    body: SessionQueryFilter,
    laps_service: LapDataResolver = Depends(LapDataResolver),
):
    """
    Retrieve laptime data for given session
    """
    return await laps_service.get_laptimes(
        session_identifier=session_identifier,
        grand_prix=event,
        year=year,
        queries=body.queries,
    )


@SessionRouter.post(
    "/season/{year}/event/{event}/session/{session_identifier}/telemetry/compare",
    response_model=list[DriverTelemetryData],
)
async def get_session_telemetry(
    year: str,
    event: str,
    session_identifier: SessionIdentifier,
    body: list[TelemetryRequest],
):
    return await TelemetryResolver(
        year=year, session_identifier=session_identifier, grand_prix=event
    ).get_telemetry_comparison(body)


@SessionRouter.post(
    "/season/{year}/event/{event}/session/{session_identifier}/telemetry/interpolated",
    response_model=list[DriverTelemetryData],
)
async def get_session_telemetry_interpolated(
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
