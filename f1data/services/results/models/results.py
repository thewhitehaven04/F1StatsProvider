from pydantic import BaseModel


class DriverBaseResult(BaseModel):
    Driver: str
    DriverNumber: str
    CountryCode: str
    TeamId: str
    TeamName: str
    Position: int


class DriverResultDto(DriverBaseResult):
    Time: float

class DriverQualifyingResultDto(BaseModel):
    Q1: float
    Q2: float
    Q3: float

