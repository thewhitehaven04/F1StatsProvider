from typing import Annotated
from fastapi import APIRouter, Depends

from core.models.queries import (
    EventQueryRequest,
    PracticeQueryRequest,
    SessionIdentifier,
)
from services.results.models.results import DriverQualifyingResultDto, DriverResultDto
from services.results.resolver import ResultsDataResolver


SessionResultsRouter = APIRouter(prefix="/session/results", tags=["SessionResults"])


@SessionResultsRouter.get("/practice", response_model=list[DriverResultDto])
async def get_practice_results(
    params: Annotated[PracticeQueryRequest, Depends()],
    results_service: ResultsDataResolver = Depends(ResultsDataResolver),
):
    return await results_service.get(
        year=params.year,
        session_identifier=params.practice,
        grand_prix=params.event_name,
    )


@SessionResultsRouter.get("/race", response_model=list[DriverResultDto])
async def get_race_results(
    params: Annotated[EventQueryRequest, Depends()],
    results_service: ResultsDataResolver = Depends(ResultsDataResolver),
):
    return await results_service.get(
        year=params.year,
        session_identifier=SessionIdentifier.RACE,
        grand_prix=params.event_name,
    )


@SessionResultsRouter.get("/qualifying", response_model=list[DriverQualifyingResultDto])
async def get_qualifying_results(
    params: Annotated[EventQueryRequest, Depends()],
    results_service: ResultsDataResolver = Depends(ResultsDataResolver),
):
    return await results_service.get(
        year=params.year,
        session_identifier=SessionIdentifier.QUALIFYING,
        grand_prix=params.event_name,
    )


@SessionResultsRouter.get("/sprint", response_model=list[DriverResultDto])
async def get_sprint_results(
    params: Annotated[EventQueryRequest, Depends()],
    results_service: ResultsDataResolver = Depends(ResultsDataResolver),
):
    return await results_service.get(
        year=params.year,
        session_identifier=SessionIdentifier.SPRINT,
        grand_prix=params.event_name,
    )
