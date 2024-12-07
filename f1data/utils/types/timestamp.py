from datetime import datetime
from typing import Annotated, Union

from pandas import NaT, Timestamp
from pydantic import PlainSerializer


StrTimestamp = Annotated[
    Union[Timestamp, type(NaT)],
    PlainSerializer(
        lambda x: None if not isinstance(x, Timestamp) else x.isoformat(),
        return_type=(str | None),
    ),
]

StrDatetime = Annotated[
    Union[datetime, type(NaT)],
    PlainSerializer(
        lambda x: None if not isinstance(x, datetime) else x.isoformat(),
        return_type=(str | None),
    ),
]
