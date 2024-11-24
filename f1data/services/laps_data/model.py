from enum import StrEnum
from pydantic import BaseModel 

class ECompound(StrEnum):
    SOFT = "SOFT"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    INTERMEDIATE = "INTERMEDIATE"
    WET = "WET"

class LapTimingData(BaseModel):
    LapTime: float | None
    Sector1Time: float | None
    Sector2Time: float | None
    Sector3Time: float | None
    ST1: float | None
    ST2: float | None
    ST3: float | None
    LapNumber: int
    Stint: int | None
    TyreLife: int | None
    Position: int | None
    Compound: ECompound 
    IsOutlap: bool
    IsInlap: bool


class LapTimingDataOut(LapTimingData):
    class Config: 
        to_format = "dict"

class DriverLapData(BaseModel):
    driver: str
    team: str
    data: list[LapTimingDataOut]


class DriverLapDataOut(DriverLapData):
    class Config:
        to_format = "dict"
