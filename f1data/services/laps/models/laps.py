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
    model_config = ConfigDict(arbitrary_types_allowed=True)

    driver: str
    team: str
    color: str
    total_laps: int 
    avg_time: Laptime 
    min_time: Laptime
    max_time: Laptime
    median: Laptime
    low_quartile: Laptime
    high_quartile: Laptime
    data: list[LapTimingData]

class LapSelectionData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    driver_lap_data: list[DriverLapData]
    low_decile: Laptime 
    high_decile: Laptime 
    min_time: Laptime
    max_time: Laptime

class LapIdentifier:
    driver: str | int
    lap: int
