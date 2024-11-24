from typing import Annotated, Union
from pandas import NaT, Timestamp
from pydantic import BaseModel, ConfigDict, PlainSerializer 

from models.session.Identifier import SessionIdentifier


StrTimestamp = Annotated[
    Union[Timestamp, type(NaT)],
    PlainSerializer(
        lambda x: None if not isinstance(x, Timestamp) else x.isoformat(),
        return_type=(str | None),
    ),
]


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
