from typing import Annotated
from fastapi import APIRouter, Depends 

from core.models.queries import (
    QualiQueryRequest,
    RaceQueryRequest,
    PracticeQueryRequest,
    TestingQueryRequest,
)
from services.results.models.results import PracticeResult, QualifyingResult, RaceResult
from services.results.resolver import get_results

SessionResults = APIRouter(prefix="/session/results", tags=["SessionData"])


@SessionResults.get("/practice", response_model=list[PracticeResult])
async def get_practice_results(
    params: Annotated[PracticeQueryRequest, Depends()],
):
    return await get_results(
        year=params.year,
        session_identifier=params.type,
        round=int(params.round),
    )


@SessionResults.get("/racelike", response_model=list[RaceResult])
async def get_racelike_results(
    params: Annotated[RaceQueryRequest, Depends()],
):
    return await get_results(
        year=params.year,
        session_identifier=params.type,
        round=int(params.round),
    )


@SessionResults.get("/qualilike", response_model=list[QualifyingResult])
async def get_qualifying_results(
    params: Annotated[QualiQueryRequest, Depends()],
):
    return await get_results(
        year=params.year,
        session_identifier=params.type,
        round=int(params.round),
    )

@SessionResults.get("/testing", response_model=list[PracticeResult])
def get_testing_results(
    params: Annotated[TestingQueryRequest, Depends()],
):
    return get_results(
        year=params.year,
        session_identifier=params.day,
        round=int(params.round),
        is_testing=True
    )