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


class RaceQueryRequest(BaseModel):
    year: str
    round: str 
    type: Literal[SessionIdentifier.SPRINT, SessionIdentifier.RACE]


class QualiQueryRequest(BaseModel):
    year: str
    round: str 
    type: Literal[SessionIdentifier.QUALIFYING, SessionIdentifier.SHOOTOUT, SessionIdentifier.SPRINT_QUALIFYING]


class PracticeQueryRequest(BaseModel):
    year: str
    round: str 
    type: Literal[SessionIdentifier.FP1, SessionIdentifier.FP2, SessionIdentifier.FP3]

class TestingQueryRequest(BaseModel):
    year: str
    round: str
    day: int 

class SessionQuery(BaseModel):
    driver: str
    lap_filter: list[int] | None

class SessionQueryFilter(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    queries: list[SessionQuery]


class TelemetryRequest(BaseModel):
    driver: str
    lap_filter: list[int]
