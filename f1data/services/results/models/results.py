from typing import Annotated, Union
from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, field_serializer
import pandas as pd


NullableLaptime = Annotated[
    Union[pd.Timedelta, type(pd.NaT)],
    PlainSerializer(
        lambda x: x.total_seconds() if pd.notna(x) else None, return_type=(float | None)
    ),
]


class DriverBaseResult(BaseModel):
    Driver: str
    DriverNumber: str = Field(coerce_numbers_to_str=True)
    CountryCode: str
    TeamId: str
    TeamName: str


class DriverResultDto(DriverBaseResult):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    Time: NullableLaptime


class DriverQualifyingResultDto(DriverBaseResult):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    Q1Time: NullableLaptime
    Q2Time: NullableLaptime
    Q3Time: NullableLaptime
