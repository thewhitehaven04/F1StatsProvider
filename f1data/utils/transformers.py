import pandas as pd

int_or_null = lambda x: int(x) if not pd.isna(x) else None

laptime_to_seconds = lambda x: (float(x.total_seconds()) if pd.notna(x) else 0)

identity = lambda x: x
