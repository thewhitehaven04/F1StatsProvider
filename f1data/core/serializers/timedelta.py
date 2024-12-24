from pydantic import PlainSerializer
import pandas as pd


timedelta_serializer = PlainSerializer(
    lambda x: x.total_seconds() if pd.notna(x) else None, return_type=(float | None)
)
