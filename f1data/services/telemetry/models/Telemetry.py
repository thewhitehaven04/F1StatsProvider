from typing import Sequence
from xmlrpc.client import Boolean 
from pandas import Timedelta, notna
from pydantic import BaseModel, ConfigDict, field_serializer

class TelemetryData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    Throttle: Sequence[float]
    Brake: Sequence[Boolean]
    Gear: Sequence[int]
    Speed: Sequence[float]
    RPM: Sequence[float]
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
    alternative_style: bool 
    telemetry: TelemetryData


class DeltaData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    distance: Sequence[float]
    gap: Sequence[float]


class DriverTelemetryComparison(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    driver: str
    color: str
    alternative_style: bool
    comparison: DeltaData


class CircuitDataInstance(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    X: float
    Y: float
    Distance: float
    RelativeDistance: float
    FastestDriver: str
    Color: str
    AlternativeStyle: bool

class CircuitData(BaseModel): 
    model_config = ConfigDict(arbitrary_types_allowed=True)

    position_data: Sequence[CircuitDataInstance]
    rotation: float

class TelemetryComparison(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    reference: str
    telemetries: list[DriverTelemetryComparison]
    circuit_data: CircuitData 
