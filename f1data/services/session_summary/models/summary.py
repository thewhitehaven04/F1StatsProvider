from typing import Sequence
from pydantic import BaseModel, ConfigDict

from services.session_summary.models.weather import SessionWeather
from utils.types.timestamp import StrDatetime


class Summary(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    start_time: StrDatetime
    finish_time: StrDatetime
    round_name: str
    official_name: str
    session_type: str


class SessionSummary(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    weather: SessionWeather
    summary: Summary