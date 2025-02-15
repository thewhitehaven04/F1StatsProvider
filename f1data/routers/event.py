from typing import Annotated
from fastapi import APIRouter, Path, Response 
from core.models.queries import SessionIdentifier
from services.event_schedule.models import ScheduledEvent
from services.event_schedule.event import get_schedule
from services.session_summary.models.summary import SessionSummary
from services.session_summary.service import get_session_info


EventRouter = APIRouter(prefix="/season", tags=["Event Schedule"])


@EventRouter.get("/{year}", response_model=list[ScheduledEvent])
def year_events(
    year: Annotated[int, Path(title="Year")],
):
    return get_schedule(year=year, backend="fastf1")


@EventRouter.get("/{year}/telemetry", response_model=list[ScheduledEvent])
def year_telemetry_events(
    year: Annotated[int, Path(title="Year", gt=2018)],
):
    return get_schedule(year=year)


@EventRouter.get(
    "/{year}/round/{round_number}/session/{session_identifier}/summary",
    response_model=SessionSummary,
)
def get_session_summary(
    year: Annotated[int, Path(title="Year", gt=2018)],
    round_number: Annotated[str, Path(title="Round number")],
    session_identifier: Annotated[SessionIdentifier, Path(title="Session Identifier")],
    response: Response,
):
    response.headers["Cache-Control"] = "max-age=4322600, public"
    return get_session_info(
        year=year,
        round=int(round_number),
        session_identifier=session_identifier,
    )
