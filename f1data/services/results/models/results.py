from typing import Annotated, Union
from pydantic import BaseModel, ConfigDict, Field, PlainSerializer 
import pandas as pd


Laptime = Annotated[
    Union[pd.Timedelta, type(pd.NaT)],
    PlainSerializer(
        lambda x: x.total_seconds() if pd.notna(x) else None, return_type=(float | None)
    ),
]


class SessionBaseResult(BaseModel):
    Driver: str
    DriverNumber: str = Field(coerce_numbers_to_str=True)
    CountryCode: str
    TeamId: str
    TeamName: str


class PracticeResult(SessionBaseResult):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    Time: Laptime
    Gap: Laptime

class RaceResult(SessionBaseResult):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    GridPosition: int
    Status: str 
    Points: int
    Time: Laptime
    Gap: Laptime

class QualifyingResult(SessionBaseResult):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    Q1Time: Laptime
    Q2Time: Laptime
    Q3Time: Laptime