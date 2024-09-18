import pandas as pd

laptime_to_seconds = lambda x: x.total_seconds() if not pd.isna(x) else None