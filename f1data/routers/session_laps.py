from fastapi import APIRouter, Response


from core.models.queries import SessionIdentifier, SessionQueryFilter, TelemetryRequest
from services.laps.models.laps import LapSelectionData
from services.laps.resolver import get_resolved_laptime_data
from services.tasks.preload_telemetry import preload_telemetry
from services.telemetry.models.Telemetry import DriverTelemetryData, TelemetryComparison
from services.telemetry.resolver import (
    get_interpolated_telemetry_comparison,
    get_telemetries,
    get_telemetry,
)
from fastapi import BackgroundTasks

SessionRouter = APIRouter(tags=["Session level data"])


@SessionRouter.post(
    "/season/{year}/round/{round_number}/session/{session_identifier}/laps",
    response_model=LapSelectionData,
)
def get_session_laptimes(
    year: str,
    round_number: str,
    session_identifier: SessionIdentifier,
    body: SessionQueryFilter,
    response: Response,
    background_tasks: BackgroundTasks,
):
    """
    Retrieve laptime data for given session
    """
    background_tasks.add_task(
        preload_telemetry, year, round_number, session_identifier, is_testing=False
    )
    response.headers["Cache-Control"] = "public, max-age=604800"
    return get_resolved_laptime_data(
        year=year,
        round_number=int(round_number),
        session_identifier=session_identifier,
        queries=body.queries,
        is_testing=False,
    )


@SessionRouter.post(
    "/season/{year}/round/{round_number}/session/{session_identifier}/telemetry/comparison",
    response_model=TelemetryComparison,
)
async def get_session_telemetry(
    year: str,
    round_number: str,
    session_identifier: SessionIdentifier,
    body: list[TelemetryRequest],
):
    return await get_interpolated_telemetry_comparison(
        year, int(round_number), session_identifier, body, is_testing=False
    )


@SessionRouter.get(
    "/season/{year}/round/{round_number}/session/{session_identifier}/lap/{lap}/driver/{driver}/telemetry",
    response_model=DriverTelemetryData,
)
async def get_session_lap_driver_telemetry(
    year: str,
    round_number: str,
    session_identifier: SessionIdentifier,
    lap: str,
    driver: str,
    response: Response,
):
    response.headers["Cache-Control"] = "public, max-age=604800"
    return await get_telemetry(
        year, int(round_number), session_identifier, driver, lap, is_testing=False
    )


@SessionRouter.post(
    "/season/{year}/round/{round_number}/session/{session_identifier}/telemetries",
    response_model=list[DriverTelemetryData],
)
async def get_session_lap_telemetries(
    year: str,
    round_number: str,
    session_identifier: SessionIdentifier,
    body: list[TelemetryRequest],
):
    return await get_telemetries(
        year=year,
        round_number=int(round_number),
        session_identifier=session_identifier,
        queries=body,
        is_testing=False,
    )


@SessionRouter.post(
    "/season/{year}/testing_round/{round_number}/day/{day}/laps",
    response_model=LapSelectionData,
)
def get_testing_session_laptimes(
    year: str,
    round_number: str,
    day: int,
    body: SessionQueryFilter,
    response: Response,
    background_tasks: BackgroundTasks,
):
    """
    Retrieve laptime data for given session
    """
    background_tasks.add_task(
        preload_telemetry, year, round_number, day, is_testing=True
    )
    response.headers["Cache-Control"] = "public, max-age=604800"
    return get_resolved_laptime_data(
        year=year,
        round_number=int(round_number),
        session_identifier=day,
        queries=body.queries,
        is_testing=True,
    )


@SessionRouter.post(
    "/season/{year}/testing_round/{round_number}/day/{day}/telemetry/comparison",
    response_model=TelemetryComparison,
)
async def get_testing_session_telemetry(
    year: str,
    round_number: str,
    day: int,
    body: list[TelemetryRequest],
):
    return await get_interpolated_telemetry_comparison(
        year=year,
        round_number=int(round_number),
        session_identifier=day,
        comparison=body,
        is_testing=True,
    )


@SessionRouter.get(
    "/season/{year}/testing_round/{round_number}/day/{day}/lap/{lap}/driver/{driver}/telemetry",
    response_model=DriverTelemetryData,
)
async def get_testing_session_lap_driver_telemetry(
    year: str,
    round_number: str,
    day: int,
    lap: str,
    driver: str,
    response: Response,
):
    response.headers["Cache-Control"] = "public, max-age=604800"
    return await get_telemetry(
        year=year,
        round_number=int(round_number),
        session_identifier=day,
        driver=driver,
        lap=lap,
        is_testing=True,
    )


@SessionRouter.post(
    "/season/{year}/testing_round/{round_number}/day/{day}/telemetries",
    response_model=list[DriverTelemetryData],
)
async def get_testing_session_lap_telemetries(
    year: str,
    round_number: str,
    day: int,
    body: list[TelemetryRequest],
):
    return await get_telemetries(
        year=year,
        round_number=int(round_number),
        session_identifier=day,
        queries=body,
        is_testing=True,
    )
