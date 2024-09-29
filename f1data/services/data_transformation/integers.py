import pandas as pd


int_or_null = lambda x: int(x) if not pd.isna(x) else None