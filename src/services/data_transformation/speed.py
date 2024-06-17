import numpy as np
import pandas as pd


speed_to_float_or_null = lambda x: np.float16(x) if not pd.isna(x) else None