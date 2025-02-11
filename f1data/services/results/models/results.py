from pandas import Timedelta, notna
from pandas.api.typing import NaTType
from pydantic import BaseModel, ConfigDict, Field, field_serializer


class SessionBaseResult(BaseModel):
    Driver: str
    DriverNumber: str = Field(coerce_numbers_to_str=True)
    CountryCode: str
    TeamId: str
    TeamName: str


class PracticeResult(SessionBaseResult):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    Time_: Timedelta | NaTType 
    Gap: Timedelta | NaTType
    
    @field_serializer(
        "Time_", "Gap", mode="plain", when_used="json", return_type=float | None
    )
    def serialize_timedelta(self, val):
        return val.total_seconds() if notna(val) else None



class RaceResult(SessionBaseResult):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    GridPosition: int 
    Status: str
    Points: int 
    Time: Timedelta | NaTType 
    Gap: Timedelta | NaTType

    @field_serializer(
        "Time", "Gap", mode="plain", when_used="json", return_type=float | None
    )
    def serialize_timedelta(self, val: Timedelta | NaTType):
        return val.total_seconds() if notna(val) else None

class QualifyingResult(SessionBaseResult):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    Q1Time: Timedelta | NaTType
    Q2Time: Timedelta | NaTType
    Q3Time: Timedelta | NaTType
    
    @field_serializer(
        "Q1Time", "Q2Time", "Q3Time", mode="plain", when_used="json", return_type=float | None
    )
    def serialize_timedelta(self, val):
        return val.total_seconds() if notna(val) else None
