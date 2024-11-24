from typing import Annotated
from fastapi import APIRouter, Depends


from models.session.results.query import SessionQueryRequest
from services.laps_data.resolver import LapDataResolver
from services.laps_data.model import DriverLapDataOut

SessionRouter = APIRouter(prefix="/session", tags=["Laps"])


@SessionRouter.get("/all")
async def get_session_laptimes(
    params: Annotated[SessionQueryRequest, Depends(SessionQueryRequest)],
    laps_service: LapDataResolver = Depends(LapDataResolver),
) -> list[DriverLapDataOut]:
    """
    Retrieve laptime data for given session
    """
    return await laps_service.get_laptimes(
        session_identifier=params.session_identifier,
        grand_prix=params.grand_prix,
        year=params.year,
    )
