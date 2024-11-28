from pydantic import BaseModel, Field


class DriverBaseResult(BaseModel):
    Driver: str
    DriverNumber: str = Field(coerce_numbers_to_str=True) 
    CountryCode: str
    TeamId: str
    TeamName: str
    Position: int | None


class DriverResultDto(DriverBaseResult):
    Time: float | None

class DriverQualifyingResultDto(BaseModel):
    Q1Time: float | None
    Q2Time: float | None
    Q3Time: float | None

