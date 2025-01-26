from typing import Sequence 
from pandas import Timedelta, notna
from pydantic import BaseModel, ConfigDict, field_serializer
from pandas.api.typing import NaTType

class TelemetryData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    Throttle: Sequence[int]
    Gear: Sequence[int]
    Speed: Sequence[int]
    RPM: Sequence[int]
    Time: Sequence[Timedelta]
    RelativeDistance: Sequence[float]
    Distance: Sequence[float]

    @field_serializer('Time', mode='plain', when_used='json', return_type=Sequence[float])
    def serialize_time(self, seq: Sequence[Timedelta]): 
        return [val.total_seconds() if notna else None for val in seq] 


class DriverTelemetryData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    driver: str
    color: str
    telemetry: TelemetryData


class SessionTelemetryData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    telemetry: list[DriverTelemetryData]
    track_data: TelemetryData


class DeltaData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    Distance: Sequence[float]
    Speed: Sequence[float]
    Gap: Sequence[float]


class DriverTelemetryComparison(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    driver: str
    color: str
    comparison: DeltaData


class TelemetryComparison(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    reference: str
    telemetries: list[DriverTelemetryComparison]
