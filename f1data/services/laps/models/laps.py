from enum import StrEnum
from math import isnan
from typing import Union
from pandas import Timedelta, notna 
from pandas.api.typing import NaTType
from pydantic import BaseModel, ConfigDict, field_serializer


class ECompound(StrEnum):
    SOFT = "SOFT"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    INTERMEDIATE = "INTERMEDIATE"
    WET = "WET"
    TEST_UNKNOWN = "TEST_UNKNOWN"

class LapTimingData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    LapTime: Timedelta
    IsPB: bool
    Sector1Time: Timedelta | NaTType  
    Sector2Time: Timedelta | NaTType  
    Sector3Time: Timedelta | NaTType  
    ST1: float
    ST2: float
    ST3: float
    Stint: int
    TyreLife: int
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

    @field_serializer(
        "LapTime",
        "Sector1Time",
        "Sector2Time",
        "Sector3Time",
        mode="plain",
        when_used="json",
        return_type=float | None,
    )
    def serialize_to_sectortime(self, val: Timedelta):
        return val.total_seconds() if notna(val) else None

    @field_serializer(
        "ST1", "ST2", "ST3", mode="plain", when_used="json", return_type=float | None
    )
    def serialize_to_speedtrap(self, val):
        return None if isnan(val) else val

    @field_serializer(
        "Stint", "TyreLife", mode="plain", when_used="json", return_type=int | None
    )
    def serialize_to_int(self, val: int):
        return None if isnan(val) else val


class DriverLapData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    driver: str
    team: str
    color: str
    total_laps: int
    avg_time: Timedelta
    min_time: Timedelta
    max_time: Timedelta
    median: Timedelta
    low_quartile: Timedelta
    high_quartile: Timedelta
    data: list[LapTimingData]

    @field_serializer(
        "avg_time",
        "min_time",
        "max_time",
        "median",
        "low_quartile",
        "high_quartile",
        mode="plain",
        when_used="json",
        return_type=float,
    )
    def serialize_to_seconds(self, val: Timedelta):
        return val.total_seconds()


class LapSelectionData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    driver_lap_data: list[DriverLapData]
    low_decile: Timedelta
    high_decile: Timedelta
    min_time: Timedelta
    max_time: Timedelta

    @field_serializer(
        "low_decile",
        "high_decile",
        "min_time",
        "max_time",
        mode="plain",
        when_used="json",
        return_type=float,
    )
    def serialize_timedelta_to_seconds(self, val: Timedelta):
        return val.total_seconds()


class LapIdentifier:
    driver: str | int
    lap: int
