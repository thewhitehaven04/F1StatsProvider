from typing import TypeVar
from pydantic import BaseModel


T = TypeVar("T")

class SessionWeather(BaseModel):
    air_temp_start: float
    air_temp_finish: float
    track_temp_start: float 
    track_temp_finish: float
    humidity_start: float
    humidity_finish: float