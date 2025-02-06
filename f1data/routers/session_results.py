from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks, logger

from core.models.queries import (
    QualiQueryRequest,
    RaceQueryRequest,
    PracticeQueryRequest,
    SessionIdentifier,
)
from services.results.models.results import PracticeResult, QualifyingResult, RaceResult
from services.results.resolver import get_results
from services.session.session import SessionLoader

def load_session(year: str, event: str, session_identifier: SessionIdentifier):
    logger.logger.info('Preloading telemetry data for session: (%s, %s, %s)', year, event, session_identifier)
    loader = SessionLoader(
        year=year, event=event, session_identifier=session_identifier
    )
    loader.load_all()


SessionResults = APIRouter(prefix="/session/results", tags=["SessionData"])


@SessionResults.get("/practice", response_model=list[PracticeResult])
def get_practice_results(
    params: Annotated[PracticeQueryRequest, Depends()],
    tasks: BackgroundTasks
):
    tasks.add_task(load_session, year=params.year, session_identifier=params.practice, event=params.event_name)
    return get_results(
        year=params.year,
        session_identifier=params.practice,
        grand_prix=params.event_name,
    )


@SessionResults.get("/racelike", response_model=list[RaceResult])
def get_racelike_results(
    params: Annotated[RaceQueryRequest, Depends()],
    tasks: BackgroundTasks
):
    tasks.add_task(load_session, year=params.year, session_identifier=params.type, event=params.event_name)
    return get_results(
        year=params.year,
        session_identifier=params.type,
        grand_prix=params.event_name,
    )


@SessionResults.get("/qualilike", response_model=list[QualifyingResult])
def get_qualifying_results(
    params: Annotated[QualiQueryRequest, Depends()],
    tasks: BackgroundTasks
):
    tasks.add_task(load_session, year=params.year, session_identifier=params.type, event=params.event_name)
    return get_results(
        year=params.year,
        session_identifier=params.type,
        grand_prix=params.event_name,
    )