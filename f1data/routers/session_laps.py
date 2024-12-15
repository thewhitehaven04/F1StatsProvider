from fastapi import APIRouter, Depends


from core.models.queries import SessionIdentifier, SessionQueryFilter
from services.laps.models.laps import DriverLapData
from services.laps.resolver import LapDataResolver

SessionLapsRouter = APIRouter(tags=["Session laps data"])


@SessionLapsRouter.post(
    "/season/{year}/event/{event}/session/{session_identifier}/laps",
    response_model=list[DriverLapData]
)
async def get_session_laptimes(
    year: int,
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
        drivers=body.drivers,
    )
