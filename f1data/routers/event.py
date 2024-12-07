from typing import Annotated 
from fastapi import APIRouter, Depends, Path
from core.models.queries import SessionIdentifier
from services.event_schedule.models import ScheduledEventCollection
from services.event_schedule.event import EventsService
from services.session_summary.models.summary import SessionSummary
from services.session_summary.service import SessionSummaryService


EventRouter = APIRouter(prefix="/season", tags=["Event Schedule"])


@EventRouter.get("/{year}", response_model=ScheduledEventCollection)
async def year_events(
    year: Annotated[int, Path(title="Year")],
    event_schedule_service: EventsService = Depends(EventsService),
):
    return event_schedule_service.get_schedule(year=year, backend="fastf1")


@EventRouter.get(
    "/{year}/telemetry", response_model=ScheduledEventCollection
)
async def year_telemetry_events(
    year: Annotated[int, Path(title="Year", gt=2018)],
    event_schedule_service: EventsService = Depends(EventsService),
):
    return event_schedule_service.get_schedule(year=year)


@EventRouter.get(
    "/{year}/event/{event_name}/session/{session_identifier}/summary",
    response_model=SessionSummary,
)
async def get_session_summary(
    year: Annotated[int, Path(title="Year", gt=2018)],
    event_name: Annotated[str, Path(title="Event Name")],
    session_identifier: Annotated[SessionIdentifier, Path(title="Session Identifier")],
    session_summary_service: SessionSummaryService = Depends(SessionSummaryService),
): 
    return await session_summary_service.get_session_summary(
        year=year,
        grand_prix=event_name,
        session_identifier=session_identifier,
    )