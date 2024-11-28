from typing import Annotated
from fastapi import APIRouter, Depends


from core.models.queries import SessionQueryRequest
from services.laps.models.laps import DriverLapDataOut
from services.laps.resolver import LapDataResolver

SessionLapsRouter = APIRouter(prefix="/session/laps", tags=["SessionLaps"])



@SessionLapsRouter.get("/all")
async def get_session_laptimes(
    params: Annotated[SessionQueryRequest, Depends()],
    laps_service: LapDataResolver = Depends(LapDataResolver),
) -> list[DriverLapDataOut]:
    """
    Retrieve laptime data for given session
    """
    return await laps_service.get_laptimes(
        session_identifier=params.session_identifier,
        grand_prix=params.event_name,
        year=params.year,
    )
