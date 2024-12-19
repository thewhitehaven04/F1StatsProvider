from enum import StrEnum
from math import isnan
from typing import Annotated
from pydantic import BaseModel, ConfigDict, PlainSerializer
from services.results.models.results import Laptime

IntOrNaN = Annotated[
    float,
    PlainSerializer(lambda x: None if isnan(x) else int(x), return_type=(int | None)),
]

FloatOrNaN = Annotated[
    float,
    PlainSerializer(lambda x: None if isnan(x) else x, return_type=(float | None)),
]


class ECompound(StrEnum):
    SOFT = "SOFT"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    INTERMEDIATE = "INTERMEDIATE"
    WET = "WET"
    TEST_UNKNOWN = "TEST_UNKNOWN"


class LapTimingData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    LapTime: Laptime
    IsPB: bool
    Sector1Time: Laptime
    Sector2Time: Laptime
    Sector3Time: Laptime
    ST1: FloatOrNaN 
    ST2: FloatOrNaN 
    ST3: FloatOrNaN 
    Stint: IntOrNaN
    TyreLife: IntOrNaN
    Compound: ECompound
    IsOutlap: bool
    IsInlap: bool
    IsBestS1: bool
    IsBestS2: bool
    IsBestS3: bool
    IsBestST1: bool
    IsBestST2: bool
    IsBestST3: bool
    IsPBS1: bool
    IsPBS2: bool
    IsPBS3: bool

class DriverLapData(BaseModel):
    driver: str
    team: str
    data: list[LapTimingData]

    class Config:
        to_format = "dict"


class LapIdentifier:
    driver: str | int
    lap: int
