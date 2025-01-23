from typing import Annotated, Union
from pydantic import PlainSerializer
import pandas as pd


timedelta_serializer = PlainSerializer(
    lambda x: x.total_seconds() if pd.notna(x) else None, return_type=(float | None)
)
TimedeltaToFloat = Annotated[Union[pd.Timedelta, type(pd.NaT)], timedelta_serializer]
