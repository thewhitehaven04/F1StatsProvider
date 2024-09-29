import pandas as pd

speed_to_float_or_null = lambda x: float(x) if not pd.isna(x) else None