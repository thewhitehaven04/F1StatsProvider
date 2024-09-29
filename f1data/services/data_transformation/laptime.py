import pandas as pd

laptime_to_seconds = lambda x: float(x.total_seconds()) if not pd.isna(x) else None