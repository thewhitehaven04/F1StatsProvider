from typing import Annotated 
from pydantic import BaseModel, ConfigDict, PlainSerializer

from core.models.queries import SessionIdentifier 
from utils.types.timestamp import StrTimestamp


def is_session(x: str) -> bool:
    assert x in [
        "None",
        "Race",
        "Qualifying",
        "Sprint",
        "Sprint Qualifying",
        "Sprint Shootout",
        "Practice 1",
        "Practice 2",
        "Practice 3",
    ]
    return True


NullableSession = Annotated[
    str,
    PlainSerializer(
        lambda x: None if x == "None" else x, return_type=(SessionIdentifier | None)
    ),
]


class ScheduledEvent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    RoundNumber: int
    Country: str
    EventDate: StrTimestamp
    EventName: str
    OfficialEventName: str
    EventFormat: str
    Session1: SessionIdentifier
    Session1Date: StrTimestamp
    Session1DateUtc: StrTimestamp
    Session2: SessionIdentifier
    Session2Date: StrTimestamp
    Session2DateUtc: StrTimestamp
    Session3: SessionIdentifier
    Session3Date: StrTimestamp
    Session3DateUtc: StrTimestamp
    Session4: NullableSession
    Session4Date: StrTimestamp
    Session4DateUtc: StrTimestamp
    Session5: NullableSession
    Session5Date: StrTimestamp
    Session5DateUtc: StrTimestamp
    F1ApiSupport: bool
