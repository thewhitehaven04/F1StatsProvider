from typing import Literal, Optional
from numpy import float64, int64
from pydantic import BaseModel, Field

COMPOUND_VALUES = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
CompoundLiteral = Literal["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]


class LapTimingData(BaseModel):

    LapTime: Optional[float] = Field(nullable=True)
    Sector1Time: Optional[float] = Field(nullable=True)
    Sector2Time: Optional[float] = Field(nullable=True)
    Sector3Time: Optional[float]= Field(nullable=True)
    LapNumber: Optional[int] = Field(nullable=True)
    Stint: Optional[int] = Field(nullable=True)
    TyreLife: Optional[int] = Field(nullable=True)
    Position: Optional[int] = Field(nullable=True)
    Compound: str = Field(
        isin=COMPOUND_VALUES,
        coerce=True,
    )
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
