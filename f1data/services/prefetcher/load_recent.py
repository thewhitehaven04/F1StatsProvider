from asyncio import TaskGroup, as_completed, create_task
from datetime import datetime
import fastf1

from services.session.session import SessionLoader



async def load_recent():
    now = datetime.now()
    schedule = fastf1.get_event_schedule(year=now.year)
    past_weekends = schedule[schedule["Session1DateUtc"] < now].tail(1)
    tasks = []
    for weekend in past_weekends.iterrows():
        for session_index, key in enumerate(
            [
                "Session1DateUtc",
                "Session2DateUtc",
                "Session3DateUtc",
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
                    tasks.append(create_task(loader.fetch_all_data()))
    
    as_completed(tasks)