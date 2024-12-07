from typing import Annotated
from fastapi import APIRouter, Depends

from core.models.queries import (
    EventQueryRequest,
    PracticeQueryRequest,
    SessionIdentifier,
)
from services.results.models.results import DriverQualifyingResultDto, PracticeDriverResultDto, RaceDriverResultDto
from services.results.resolver import ResultsDataResolver


SessionResults = APIRouter(prefix="/session/results", tags=["SessionData"])


@SessionResults.get("/practice", response_model=list[PracticeDriverResultDto])
async def get_practice_results(
    params: Annotated[PracticeQueryRequest, Depends()],
    results_service: ResultsDataResolver = Depends(ResultsDataResolver),
):
    return await results_service.get(
        year=params.year,
        session_identifier=params.practice,
        grand_prix=params.event_name,
    )


@SessionResults.get("/race", response_model=list[RaceDriverResultDto])
async def get_race_results(
    params: Annotated[EventQueryRequest, Depends()],
    results_service: ResultsDataResolver = Depends(ResultsDataResolver),
):
    return await results_service.get(
        year=params.year,
        session_identifier=SessionIdentifier.RACE,
        grand_prix=params.event_name,
    )


@SessionResults.get("/qualifying", response_model=list[DriverQualifyingResultDto])
async def get_qualifying_results(
    params: Annotated[EventQueryRequest, Depends()],
    results_service: ResultsDataResolver = Depends(ResultsDataResolver),
):
    return await results_service.get(
        year=params.year,
        session_identifier=SessionIdentifier.QUALIFYING,
        grand_prix=params.event_name,
    )


@SessionResults.get("/sprint", response_model=list[PracticeDriverResultDto])
async def get_sprint_results(
    params: Annotated[EventQueryRequest, Depends()],
    results_service: ResultsDataResolver = Depends(ResultsDataResolver),
):
    return await results_service.get(
        year=params.year,
        session_identifier=SessionIdentifier.SPRINT,
        grand_prix=params.event_name,
    )
