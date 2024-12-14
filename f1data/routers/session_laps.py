from typing import Annotated
from fastapi import APIRouter, Depends


from core.models.queries import SessionPathRequest
from services.laps.models.laps import DriverLapData
from services.laps.resolver import LapDataResolver

SessionLapsRouter = APIRouter(tags=["SessionLaps"])



@SessionLapsRouter.get("/season/{year}/event/{event}/session/{session_identifier}/laps", tags=["Session laps"])
async def get_session_laptimes(
    path: Annotated[SessionPathRequest, Depends()],
    laps_service: LapDataResolver = Depends(LapDataResolver),
) -> list[DriverLapData]:
    """
    Retrieve laptime data for given session
    """
    return await laps_service.get_laptimes(
        session_identifier=path.session_identifier,
        grand_prix=path.event_name,
        year=path.year,
    )