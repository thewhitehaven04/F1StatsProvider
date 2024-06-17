from typing import Annotated
from fastapi import APIRouter, Depends


from models.session.results.query import SessionQueryRequest
from services.laps_data.laps import LapData


SessionRouter = APIRouter(prefix='/session', tags=['Laps'])

@SessionRouter.get('')
async def get_session_laptimes(
    params: Annotated[SessionQueryRequest, Depends(SessionQueryRequest)],
    laps_service: LapData = Depends(LapData) 
):
    """
    Retrieve laptime data for given session 
    """
    return laps_service.get_laptimes(
        session_identifier=params.session_identifier,
        grand_prix=params.grand_prix,
        year=params.year,
    )