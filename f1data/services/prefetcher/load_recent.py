from datetime import datetime
import fastf1
from services.session.session import SessionLoader


async def prefetch_recent_events():
    now = datetime.now()
    schedule = fastf1.get_event_schedule(year=now.year)
    past_weekends = schedule[schedule["Session1DateUtc"] < now].tail(1)
    for weekend in past_weekends.iterrows():
        for session_index, key in enumerate(
            [
                "Session1DateUtc",
                "Session2DateUtc",
                "Session3DateUtc",
                "Session4DateUtc",
                "Session5DateUtc",
            ]
        ):
            if weekend[1][key] < now:
                round_number = weekend[1]["RoundNumber"]
                if weekend[1][key]:
                    is_testing = weekend[1]["EventFormat"] == "testing"
                    loader = SessionLoader(
                        year=str(now.year),
                        round=round_number + 1 if is_testing else round_number,
                        session_identifier=session_index + 1,
                        is_testing=is_testing,
                    )
                    await loader.fetch_all_data() 