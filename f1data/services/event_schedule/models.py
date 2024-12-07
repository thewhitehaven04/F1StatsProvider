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


class ScheduledEventCollection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    RoundNumber: list[int]
    Country: list[str]
    EventDate: list[StrTimestamp]
    EventName: list[str]
    OfficialEventName: list[str]
    EventFormat: list[str]
    Session1: list[SessionIdentifier]
    Session1Date: list[StrTimestamp]
    Session1DateUtc: list[StrTimestamp]
    Session2: list[SessionIdentifier]
    Session2Date: list[StrTimestamp]
    Session2DateUtc: list[StrTimestamp]
    Session3: list[SessionIdentifier]
    Session3Date: list[StrTimestamp]
    Session3DateUtc: list[StrTimestamp]
    Session4: list[NullableSession]
    Session4Date: list[StrTimestamp]
    Session4DateUtc: list[StrTimestamp]
    Session5: list[NullableSession]
    Session5Date: list[StrTimestamp]
    Session5DateUtc: list[StrTimestamp]
    F1ApiSupport: list[bool]
