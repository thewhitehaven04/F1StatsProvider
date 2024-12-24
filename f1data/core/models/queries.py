from enum import StrEnum
from typing import Literal 

from pydantic import BaseModel


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
    year: int
    event_name: str


class PracticeQueryRequest(BaseModel):
    year: int
    event_name: str
    practice: Literal[
        SessionIdentifier.FP1,
        SessionIdentifier.FP2,
        SessionIdentifier.FP3,
    ]

class SessionQueryFilter(BaseModel):
    drivers: list[str]

class TelemetryRequest(BaseModel):
    driver: str
    laps: list[int] 