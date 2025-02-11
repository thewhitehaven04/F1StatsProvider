from typing import Annotated
from fastapi import APIRouter, Depends 

from core.models.queries import (
    QualiQueryRequest,
    RaceQueryRequest,
    PracticeQueryRequest,
)
from services.results.models.results import PracticeResult, QualifyingResult, RaceResult
from services.results.resolver import get_results

SessionResults = APIRouter(prefix="/session/results", tags=["SessionData"])


@SessionResults.get("/practice", response_model=list[PracticeResult])
def get_practice_results(
    params: Annotated[PracticeQueryRequest, Depends()],
):
    return get_results(
        year=params.year,
        session_identifier=params.type,
        round=int(params.round),
    )


@SessionResults.get("/racelike", response_model=list[RaceResult])
def get_racelike_results(
    params: Annotated[RaceQueryRequest, Depends()],
):
    return get_results(
        year=params.year,
        session_identifier=params.type,
        round=int(params.round),
    )


@SessionResults.get("/qualilike", response_model=list[QualifyingResult])
def get_qualifying_results(
    params: Annotated[QualiQueryRequest, Depends()],
):
    return get_results(
        year=params.year,
        session_identifier=params.type,
        round=int(params.round),
    )