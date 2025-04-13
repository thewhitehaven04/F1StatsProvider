import json
import pandas as pd
import fastf1
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.dialects.postgresql import insert

def insert_events_into_db():
    years = range(2019, 2026, 1)
    postgres = create_engine(
        "postgresql://germanbulavkin:postgres@127.0.0.1:5432/postgres"
    )
    schedules = []
    for year in years:
        schedule = fastf1.get_event_schedule(year=year)[
            ["EventName", "OfficialEventName", "EventDate", "Country", "EventFormat"]
        ].rename(
            columns={
                "EventName": "event_name",
                "OfficialEventName": "event_official_name",
                "EventDate": "date_start",
                "Country": "country",
                "EventFormat": "event_format_name",
            }
        )
        schedule[["season_year"]] = year
        schedules.append(schedule)

    schedule = pd.concat(schedules)

    with postgres.connect() as pg_con:
        events_table = Table("events", MetaData(), autoload_with=postgres)
        pg_con.execute(
            insert(table=events_table).values(schedule.to_dict(orient="records"))
        )
        pg_con.commit()
    return schedule

def store_event_sessions(season: int):
    sessions = []
    schedule = fastf1.get_event_schedule(year=season, include_testing=False)

    for i in range(len(schedule.index)):
        for identifier in range(1, 6): 
            try: 
                session = fastf1.get_session(year=season, gp=i, identifier=identifier)
                session.load(laps=False, telemetry=False, weather=False, messages=False)
                session_info = session.session_info
                sessions.append({ 
                    'start_time': session_info['StartDate'], 
                    'end_time': session_info['EndDate'], 
                    'season_year': season,
                    'event_name': session.event.EventName,
                    'session_type_id': session.event[f'Session{identifier}']
                })
            finally:
                continue
    
    with open(f'/sessions_{season}.json', 'w') as file:
        file.write(json.dumps(sessions))


def insert_event_sessions(season: int):
    postgres = create_engine("postgresql://germanbulavkin:postgres@127.0.0.1:5432/postgres")
    with open(f'/sessions_{season}.json', 'r') as file:
        sessions = json.loads(file.read())
        with postgres.connect() as pg_con:
            events_sessions_table = Table('event_sessions', MetaData(), autoload_with=postgres)
            pg_con.execute(
                insert(table=events_sessions_table).values(
                    sessions
                ) 
            )
            pg_con.commit()