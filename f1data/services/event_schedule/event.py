from typing import Literal, Optional
import fastf1


class EventsService:

    def get_schedule(
        self,
        year: int,
        backend: Optional[Literal["fastf1", "f1timing", "ergast"]] = None,
    ):
        return fastf1.get_event_schedule(year=year, backend=backend).to_dict(
            orient="list"
        )
