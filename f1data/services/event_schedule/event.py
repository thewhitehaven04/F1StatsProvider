from typing import Literal, Optional
import fastf1
from pycountry import countries


class EventsService:

    def get_schedule(
        self,
        year: int,
        backend: Optional[Literal["fastf1", "f1timing", "ergast"]] = None,
    ):
        event_schedule = fastf1.get_event_schedule(year=year, backend=backend)
        event_schedule['Country'] = event_schedule['Country'].map(lambda x: countries.get(name=x).alpha_2 or '')

        return event_schedule.to_dict(orient='records')
