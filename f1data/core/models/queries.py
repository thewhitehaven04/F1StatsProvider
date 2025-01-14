from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict


class SessionIdentifier(StrEnum):
    RACE = "Race"
    QUALIFYING = "Qualifying"
    SPRINT = "Sprint"
    SPRINT_QUALIFYING = "Sprint Qualifying"
    SHOOTOUT = "Sprint Shootout"
    FP1 = "Practice 1"
    FP2 = "Practice 2"
    FP3 = "Practice 3"


class EventQueryRequest(BaseModel):
    year: str 
    event_name: str


class PracticeQueryRequest(BaseModel):
    year: str 
    event_name: str
    practice: Literal[
        SessionIdentifier.FP1,
        SessionIdentifier.FP2,
        SessionIdentifier.FP3,
    ]

class SessionQuery(BaseModel): 
    driver: str
    lap_filter: list[int] | None

class SessionQueryFilter(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    queries: list[SessionQuery]

class TelemetryRequest(BaseModel):
    driver: str
    lap_filter: list[int] 