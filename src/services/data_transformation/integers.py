import pandas as pd
import numpy as np


int_or_null = lambda x: np.int16(x) if not pd.isna(x) else None