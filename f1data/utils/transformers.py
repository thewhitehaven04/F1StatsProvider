import pandas as pd


int_or_null = lambda x: int(x) if not pd.isna(x) else None

laptime_to_seconds = lambda x: float(x.total_seconds()) if not pd.isna(x) else None

identity = lambda x: x