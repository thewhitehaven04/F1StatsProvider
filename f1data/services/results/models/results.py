from pydantic import BaseModel, ConfigDict, Field
from core.serializers.timedelta import TimedeltaToFloat


class SessionBaseResult(BaseModel):
    Driver: str
    DriverNumber: str = Field(coerce_numbers_to_str=True)
    CountryCode: str
    TeamId: str
    TeamName: str


class PracticeResult(SessionBaseResult):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    Time: TimedeltaToFloat
    Gap: TimedeltaToFloat


class RaceResult(SessionBaseResult):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    GridPosition: int
    Status: str
    Points: int
    Time: TimedeltaToFloat
    Gap: TimedeltaToFloat


class QualifyingResult(SessionBaseResult):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    Q1Time: TimedeltaToFloat
    Q2Time: TimedeltaToFloat
    Q3Time: TimedeltaToFloat
