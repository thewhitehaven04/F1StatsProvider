import json
import pandas as pd
import fastf1
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.dialects.postgresql import insert
from scripts.db_population.connection import engine as postgres, con 


def store_sprint_race_results(season: int):
    results_arr = []
    sprint_results = []

    schedule = fastf1.get_event_schedule(year=season, include_testing=False)
    sprint_schedule = schedule[schedule["EventFormat"] == "sprint_qualifying"]
    for round_number in sprint_schedule["RoundNumber"].values:
        try:
            session = fastf1.get_session(year=season, gp=round_number, identifier=3)
            # uncomment if previously loaded
            session.load(laps=True, telemetry=False, weather=False, messages=False)
            results = session.results.rename(
                columns={"FullName": "Driver", "Time": "Gap"}
            ).assign(
                Time=pd.Series(
                    index=session.results.index,
                    data=[
                        session.results["Time"].iloc[0],
                        *(
                            session.results["Time"]
                            .iloc[1:]
                            .add(session.results["Time"].iloc[0])
                        ),
                    ],
                )
            )
        except:
            continue
        for result in results.iterrows():
            results_arr.append(
                {
                    "event_name": session.event.EventName,
                    "season_year": season,
                    "session_type_id": f"Sprint",
                    "driver_id": result[1][1],
                }
            )
            time = result[1][21].total_seconds()
            gap = result[1][18].total_seconds()
            sprint_results.append(
                {
                    "total_time": time if pd.notna(time) else None,
                    "result_status": result[1][19],
                    "classified_position": result[1][13],
                    "points": result[1][20],
                    "gap": gap if pd.notna(gap) else None,
                }
            )

    with open(f"base_race_results_{season}.json", "w") as file:
        file.write(json.dumps(results_arr))

    with open(f"race_results_{season}.json", "w") as file:
        file.write(json.dumps(sprint_results))


def insert_sprint_race_results(season: int):
    with open(f"base_race_results_{season}.json", "r") as file:
        results_arr = json.loads(file.read())

    with open(f"race_results_{season}.json", "r") as file:
        race_results = json.loads(file.read())

    with con as pg_con:
        metadata = MetaData()
        session_results_table = Table(
            "session_results", metadata, autoload_with=postgres
        )
        race_results_table = Table(
            "race_session_results", metadata, autoload_with=postgres
        )
        for result, sprint_result in zip(results_arr, race_results):
            result_id = pg_con.execute(
                insert(table=session_results_table).values(result)
            ).inserted_primary_key[0]
            pg_con.execute(
                insert(table=race_results_table).values(
                    {"id": result_id, **sprint_result}
                )
            )
        pg_con.commit()


def store_race_results(season: int):
    results_arr = []
    race_results = []

    schedule = fastf1.get_event_schedule(year=season, include_testing=False)
    for round_number in schedule["RoundNumber"].values:
        try:
            session = fastf1.get_session(year=season, gp=round_number, identifier=5)
            # uncomment if previously loaded
            session.load(laps=True, telemetry=False, weather=False, messages=False)
            results = session.results.rename(
                columns={"FullName": "Driver", "Time": "Gap"}
            ).assign(
                Time=pd.Series(
                    index=session.results.index,
                    data=[
                        session.results["Time"].iloc[0],
                        *(
                            session.results["Time"]
                            .iloc[1:]
                            .add(session.results["Time"].iloc[0])
                        ),
                    ],
                )
            )
        except:
            continue
        for result in results.iterrows():
            results_arr.append(
                {
                    "event_name": session.event.EventName,
                    "season_year": season,
                    "session_type_id": "Race",
                    "driver_id": result[1][1],
                }
            )
            time = result[1][21].total_seconds()
            gap = result[1][18].total_seconds()
            race_results.append(
                {
                    "total_time": time if pd.notna(time) else None,
                    "result_status": result[1][19],
                    "classified_position": result[1][13],
                    "points": result[1][20],
                    "gap": gap if pd.notna(gap) else None,
                }
            )

    with open(f"base_race_results_{season}.json", "w") as file:
        file.write(json.dumps(results_arr))

    with open(f"race_results_{season}.json", "w") as file:
        file.write(json.dumps(race_results))


def insert_race_results(season: int):
    with open(f"base_race_results_{season}.json", "r") as file:
        results_arr = json.loads(file.read())

    with open(f"race_results_{season}.json", "r") as file:
        race_results = json.loads(file.read())

    with con as pg_con:
        metadata = MetaData()
        session_results_table = Table(
            "session_results", metadata, autoload_with=postgres
        )
        race_results_table = Table(
            "race_session_results", metadata, autoload_with=postgres
        )
        for result, race_result in zip(results_arr, race_results):
            result_id = pg_con.execute(
                insert(table=session_results_table).values(result)
            ).inserted_primary_key[0]
            pg_con.execute(
                insert(table=race_results_table).values(
                    {"id": result_id, **race_result}
                )
            )
        pg_con.commit()


def store_sprint_quali_results(season: int):
    results_arr = []
    sprint_quali_results = []

    schedule = fastf1.get_event_schedule(year=season, include_testing=False)
    sprint_schedule = schedule[schedule["EventFormat"] == "sprint_qualifying"]
    for round_number in sprint_schedule["RoundNumber"].values:
        try:
            session = fastf1.get_session(year=season, gp=round_number, identifier=2)
            # uncomment if previously loaded
            session.load(laps=True, telemetry=False, weather=False, messages=True)
            results = session.results
        except:
            continue

        for result in results.iterrows():
            results_arr.append(
                {
                    "event_name": session.event.EventName,
                    "season_year": season,
                    "session_type_id": f"Sprint Qualifying",
                    "driver_id": result[1][1],
                }
            )
            sprint_quali_results.append(
                {
                    "q1_laptime": result[1][15].total_seconds(),
                    "q2_laptime": result[1][16].total_seconds(),
                    "q3_laptime": result[1][17].total_seconds(),
                    "position": result[1][12],
                }
            )

        with open(f"base_sprint_quali_results_{season}.json", "w") as file:
            file.write(json.dumps(results_arr))

        with open(f"sprint_quali_results_{season}.json", "w") as file:
            file.write(json.dumps(sprint_quali_results))


def insert_sprint_quali_results(season: int):
    with open(f"base_sprint_quali_results_{season}.json", "r") as file:
        results_arr = json.loads(file.read())

    with open(f"sprint_quali_results_{season}.json", "r") as file:
        sprint_quali_results = json.loads(file.read())

    with postgres.connect() as pg_con:
        metadata = MetaData()
        session_results_table = Table(
            "session_results", metadata, autoload_with=postgres
        )
        quali_results_table = Table(
            "qualifying_session_results", metadata, autoload_with=postgres
        )
        for result, quali_result in zip(results_arr, sprint_quali_results):
            result_id = pg_con.execute(
                insert(table=session_results_table).values(result)
            ).inserted_primary_key[0]
            pg_con.execute(
                insert(table=quali_results_table).values(
                    {"id": result_id, **quali_result}
                )
            )
        pg_con.commit()


def store_quali_results(season: int):
    results_arr = []
    quali_results = []

    schedule = fastf1.get_event_schedule(year=season, include_testing=False)[
        "RoundNumber"
    ]
    for round_number in schedule.values:
        try:
            session = fastf1.get_session(year=season, gp=round_number, identifier=4)
            # uncomment if previously loaded
            session.load(laps=True, telemetry=False, weather=False, messages=False)
            results = session.results
        except:
            continue
        for result in results.iterrows():
            results_arr.append(
                {
                    "event_name": session.event.EventName,
                    "season_year": season,
                    "session_type_id": f"Qualifying",
                    "driver_id": result[1][1],
                }
            )
            quali_results.append(
                {
                    "q1_laptime": result[1][15].total_seconds(),
                    "q2_laptime": result[1][16].total_seconds(),
                    "q3_laptime": result[1][17].total_seconds(),
                    "position": result[1][12],
                }
            )

        with open(f"base_quali_results_{season}.json", "w") as file:
            file.write(json.dumps(results_arr))

        with open(f"quali_results_{season}.json", "w") as file:
            file.write(json.dumps(quali_results))


def insert_quali_results(season: int):
    with open(f"base_quali_results_{season}.json", "r") as file:
        results_arr = json.loads(file.read())

    with open(f"quali_results_{season}.json", "r") as file:
        quali_results = json.loads(file.read())

    with con as pg_con:
        metadata = MetaData()
        session_results_table = Table(
            "session_results", metadata, autoload_with=postgres
        )
        quali_results_table = Table(
            "qualifying_session_results", metadata, autoload_with=postgres
        )
        for result, quali_result in zip(results_arr, quali_results):
            result_id = pg_con.execute(
                insert(table=session_results_table).values(result)
            ).inserted_primary_key[0]
            pg_con.execute(
                insert(table=quali_results_table).values(
                    {"id": result_id, **quali_result}
                )
            )
        pg_con.commit()


def store_practice_results(season: int):
    results_arr = []
    practice_results = []
    schedule = fastf1.get_event_schedule(year=season, include_testing=False)
    for round_number in schedule["RoundNumber"].values:
        max_range = (
            4
            if schedule[schedule["RoundNumber"] == round_number]["EventFormat"].iloc[0]
            == "conventional"
            else 2
        )
        for identifier in range(1, max_range):
            try:
                session = fastf1.get_session(
                    year=season, gp=round_number, identifier=identifier
                )
                # uncomment if previously loaded
                session.load(laps=True, telemetry=False, weather=False, messages=False)
                laps = session.laps
                results = (
                    session.results.assign(
                        Time_=laps.groupby("DriverNumber").agg({"LapTime": "min"})
                    )
                    .sort_values(by=["Time_"], ascending=True)
                    .assign(Gap=lambda x: x["Time_"].sub(x["Time_"].iloc[0]))
                    .dropna(subset=["BroadcastName"])
                )
            except:
                continue
            for result in results.iterrows():
                results_arr.append(
                    {
                        "event_name": session.event.EventName,
                        "season_year": season,
                        "session_type_id": f"Practice {identifier}",
                        "driver_id": result[1][1],
                    }
                )
                practice_results.append(
                    {
                        "laptime": result[1][21].total_seconds(),
                        "gap": result[1][22].total_seconds(),
                    }
                )

    with open(f"base_practice_results_{season}.json", "w") as file:
        file.write(json.dumps(results_arr))

    with open(f"practice_results_{season}.json", "w") as file:
        file.write(json.dumps(practice_results))


def insert_practice_results(season: int):
    with con as pg_con:
        metadata = MetaData()
        session_results_table = Table(
            "session_results", metadata, autoload_with=postgres
        )
        practice_results_table = Table(
            "practice_session_results", metadata, autoload_with=postgres
        )

        with open(f"base_practice_results_{season}.json", "r") as file:
            results_arr = json.loads(file.read())

        with open(f"practice_results_{season}.json", "r") as file:
            practice_results = json.loads(file.read())

        for result, practice_result in zip(results_arr, practice_results):
            result_id = pg_con.execute(
                insert(table=session_results_table).values(result)
            ).inserted_primary_key[0]
            pg_con.execute(
                insert(table=practice_results_table).values(
                    {"id": result_id, **practice_result}
                )
            )
        pg_con.commit()


def store_testing_sessions(season: int):
    sessions = []

    for session in range(1, 3):
        try:
            session = fastf1.get_testing_session(
                year=season, test_number=1, session_number=session
            )
            session.load(laps=False, telemetry=False, weather=False, messages=False)
            session_info = session.session_info
            sessions.append(
                {
                    "start_time": session_info["StartDate"],
                    "end_time": session_info["EndDate"],
                    "season_year": season,
                    "event_name": session.event.EventName,
                    "session_type_id": session.event[f"Session{session}"],
                }
            )
        finally:
            continue

    with open(f"/testing_sessions_{season}.json", "w") as file:
        file.write(json.dumps(sessions))


def insert_testing_sessions(season: int):
    with open(f"/sessions_{season}.json", "r") as file:
        sessions = json.loads(file.read())
        with con as pg_con:
            events_sessions_table = Table(
                "event_sessions", MetaData(), autoload_with=postgres
            )
            pg_con.execute(insert(table=events_sessions_table).values(sessions))
            pg_con.commit()