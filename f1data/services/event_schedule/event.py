from typing import Literal, Optional
import fastf1
from pycountry import countries


def get_schedule(year: int, backend: Optional[Literal["fastf1", "f1timing", "ergast"]] = None):
    event_schedule = fastf1.get_event_schedule(year=year, backend=backend)
    event_schedule['Country'] = event_schedule['Country'].map(lambda x: countries.get(name=x).alpha_2 if countries.get(name=x) is not None else x)

    return event_schedule.to_dict(orient='records')