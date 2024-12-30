from typing import Annotated, Sequence, Union
import pandas as pd
from pydantic import BaseModel, ConfigDict
from core.serializers.timedelta import timedelta_serializer

Laptime = Annotated[Union[pd.Timedelta, type(pd.NaT)], timedelta_serializer]


class TelemetryData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    Throttle: Sequence[int]
    Gear: Sequence[int]
    Speed: Sequence[int]
    RPM: Sequence[int]
    Time: Sequence[Laptime]
    RelativeDistance: Sequence[float]
    Distance: Sequence[float]


class DriverTelemetryData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    driver: str
    color: str
    telemetry: TelemetryData


class TelemetryTrackData(BaseModel):
    length: float
class SessionTelemetryData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    telemetry: list[DriverTelemetryData]
    track_data: TelemetryData 
