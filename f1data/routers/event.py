from typing import Annotated 
from fastapi import APIRouter, Depends, Path
from services.event_schedule.models import ScheduledEventCollection
from services.event_schedule.event import EventsService


EventRouter = APIRouter(prefix="/event")


@EventRouter.get("/year/{year}", response_model=ScheduledEventCollection)
async def year_events(
    year: Annotated[int, Path(title="Year")],
    event_schedule_service: Annotated[EventsService, Depends()],
):
    return event_schedule_service.get_schedule(year=year, backend="fastf1")


@EventRouter.get(
    "/year/{year}/telemetry", response_model=ScheduledEventCollection
)
async def year_telemetry_events(
    year: Annotated[int, Path(title="Year", gt=2018)],
    event_schedule_service: Annotated[EventsService, Depends()],
):
    return event_schedule_service.get_schedule(year=year)
