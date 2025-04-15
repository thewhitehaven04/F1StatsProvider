import json
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.dialects.postgresql import insert
import fastf1
import pandas as pd


def store_practice_laps(season: int):
    practice_laps = []
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
                session = fastf1.get_session(year=season, gp=round_number, identifier=4)
                # uncomment if previously loaded
                session.load(laps=True, telemetry=False, weather=False, messages=False)
                laps = session.laps[
                    [
                        "Sector1Time",
                        "Sector2Time",
                        "Sector3Time",
                        "SpeedI1",
                        "SpeedI2",
                        "SpeedFL",
                        "Stint",
                        "Compound",
                        "LapNumber",
                        "DriverNumber",
                    ]
                ].rename(
                    columns={
                        "Sector1Time": "sector_1_time",
                        "Sector2Time": "sector_2_time",
                        "Sector3Time": "sector_3_time",
                        "SpeedI1": "speedtrap_1",
                        "SpeedI2": "speedtrap_2",
                        "SpeedFL": "speedtrap_fl",
                        "Stint": "stint",
                        "Compound": "compound_id",
                        "LapNumber": "lap_number",
                    }
                )
                results = session.results[["DriverNumber", "BroadcastName"]]
                laps = (
                    laps.join(results.set_index("DriverNumber"), on="DriverNumber")
                    .rename(columns={"BroadcastName": "driver_id"})
                    .drop(columns=["DriverNumber"])
                )
                laps[["event_name"]] = session.event.EventName
                laps[["session_type_id"]] = f"Practice {identifier}"
                laps[["season_year"]] = season
                practice_laps.extend(laps.to_dict(orient="records"))
            except:
                continue

    def transform(val):
        val["sector_1_time"] = (
            val["sector_1_time"]
            if isinstance(val["sector_1_time"], float)
            else (
                val["sector_1_time"].total_seconds()
                if pd.notna(val["sector_1_time"])
                else None
            )
        )
        val["sector_2_time"] = (
            val["sector_2_time"]
            if isinstance(val["sector_2_time"], float)
            else (
                val["sector_2_time"].total_seconds()
                if pd.notna(val["sector_2_time"])
                else None
            )
        )
        val["sector_3_time"] = (
            val["sector_3_time"]
            if isinstance(val["sector_3_time"], float)
            else (
                val["sector_3_time"].total_seconds()
                if pd.notna(val["sector_3_time"])
                else None
            )
        )
        val["speedtrap_1"] = (
            int(val["speedtrap_1"]) if pd.notna(val["speedtrap_1"]) else None
        )
        val["speedtrap_2"] = (
            int(val["speedtrap_2"]) if pd.notna(val["speedtrap_2"]) else None
        )
        val["speedtrap_fl"] = (
            int(val["speedtrap_fl"]) if pd.notna(val["speedtrap_fl"]) else None
        )
        return val

    laps_transformed = list(map(transform, practice_laps))
    with open(f"practice_laps_{season}.json", "w") as file:
        file.write(json.dumps(laps_transformed))


def insert_practice_laps(season: int):
    postgres = create_engine(
        "postgresql://germanbulavkin:postgres@127.0.0.1:5432/postgres"
    )
    with open(f"practice_laps_{season}.json", "r") as file:
        laps = json.loads(file.read())

    with postgres.connect() as pg_con:
        laps_table = Table("laps", MetaData(), autoload_with=postgres)
        pg_con.execute(insert(table=laps_table).values(laps))
        pg_con.commit()


def store_quali_laps(season: int):
    quali_laps = []
    schedule = fastf1.get_event_schedule(year=season, include_testing=False)
    for round_number in schedule["RoundNumber"].values:
        sessions = (
            [4]
            if schedule[schedule["RoundNumber"] == round_number]["EventFormat"].iloc[0]
            == "conventional"
            else [2, 4]
        )
        for identifier in sessions:
            try:
                session = fastf1.get_session(
                    year=season, gp=round_number, identifier=identifier
                )
                # uncomment if previously loaded
                session.load(laps=True, telemetry=False, weather=False, messages=False)
                laps = session.laps[
                    [
                        "Sector1Time",
                        "Sector2Time",
                        "Sector3Time",
                        "SpeedI1",
                        "SpeedI2",
                        "SpeedFL",
                        "Stint",
                        "Compound",
                        "LapNumber",
                        "DriverNumber",
                    ]
                ].rename(
                    columns={
                        "Sector1Time": "sector_1_time",
                        "Sector2Time": "sector_2_time",
                        "Sector3Time": "sector_3_time",
                        "SpeedI1": "speedtrap_1",
                        "SpeedI2": "speedtrap_2",
                        "SpeedFL": "speedtrap_fl",
                        "Stint": "stint",
                        "Compound": "compound_id",
                        "LapNumber": "lap_number",
                    }
                )
                results = session.results[["DriverNumber", "BroadcastName"]]
                laps = (
                    laps.join(results.set_index("DriverNumber"), on="DriverNumber")
                    .rename(columns={"BroadcastName": "driver_id"})
                    .drop(columns=["DriverNumber"])
                )
                laps[["event_name"]] = session.event.EventName
                laps[["session_type_id"]] = (
                    "Qualifying" if identifier == 4 else "Sprint Qualifying"
                )
                laps[["season_year"]] = season
                quali_laps.extend(laps.to_dict(orient="records"))
            except:
                continue

    def transform(val):
        val["sector_1_time"] = (
            val["sector_1_time"]
            if isinstance(val["sector_1_time"], float)
            else (
                val["sector_1_time"].total_seconds()
                if pd.notna(val["sector_1_time"])
                else None
            )
        )
        val["sector_2_time"] = (
            val["sector_2_time"]
            if isinstance(val["sector_2_time"], float)
            else (
                val["sector_2_time"].total_seconds()
                if pd.notna(val["sector_2_time"])
                else None
            )
        )
        val["sector_3_time"] = (
            val["sector_3_time"]
            if isinstance(val["sector_3_time"], float)
            else (
                val["sector_3_time"].total_seconds()
                if pd.notna(val["sector_3_time"])
                else None
            )
        )
        val["speedtrap_1"] = (
            int(val["speedtrap_1"]) if pd.notna(val["speedtrap_1"]) else None
        )
        val["speedtrap_2"] = (
            int(val["speedtrap_2"]) if pd.notna(val["speedtrap_2"]) else None
        )
        val["speedtrap_fl"] = (
            int(val["speedtrap_fl"]) if pd.notna(val["speedtrap_fl"]) else None
        )
        return val

    laps_transformed = list(map(transform, quali_laps))
    with open(f"quali_laps_{season}.json", "w") as file:
        file.write(json.dumps(laps_transformed))


def insert_quali_laps(season: int):
    postgres = create_engine(
        "postgresql://germanbulavkin:postgres@127.0.0.1:5432/postgres"
    )
    with open(f"quali_laps_{season}.json", "r") as file:
        laps = json.loads(file.read())

    with postgres.connect() as pg_con:
        laps_table = Table("laps", MetaData(), autoload_with=postgres)
        pg_con.execute(insert(table=laps_table).values(laps))
        pg_con.commit()


def store_race_laps(season: int):
    quali_laps = []
    schedule = fastf1.get_event_schedule(year=season, include_testing=False)
    for round_number in schedule["RoundNumber"].values:
        sessions = (
            [5]
            if schedule[schedule["RoundNumber"] == round_number]["EventFormat"].iloc[0]
            == "conventional"
            else [3, 5]
        )
        for identifier in sessions:
            try:
                session = fastf1.get_session(
                    year=season, gp=round_number, identifier=identifier
                )
                # uncomment if previously loaded
                session.load(laps=True, telemetry=False, weather=False, messages=False)
                laps = session.laps[
                    [
                        "Sector1Time",
                        "Sector2Time",
                        "Sector3Time",
                        "SpeedI1",
                        "SpeedI2",
                        "SpeedFL",
                        "Stint",
                        "Compound",
                        "LapNumber",
                        "DriverNumber",
                    ]
                ].rename(
                    columns={
                        "Sector1Time": "sector_1_time",
                        "Sector2Time": "sector_2_time",
                        "Sector3Time": "sector_3_time",
                        "SpeedI1": "speedtrap_1",
                        "SpeedI2": "speedtrap_2",
                        "SpeedFL": "speedtrap_fl",
                        "Stint": "stint",
                        "Compound": "compound_id",
                        "LapNumber": "lap_number",
                    }
                )
                results = session.results[["DriverNumber", "BroadcastName"]]
                laps = (
                    laps.join(results.set_index("DriverNumber"), on="DriverNumber")
                    .rename(columns={"BroadcastName": "driver_id"})
                    .drop(columns=["DriverNumber"])
                )
                laps[["event_name"]] = session.event.EventName
                laps[["session_type_id"]] = "Race" if identifier == 5 else "Sprint"
                laps[["season_year"]] = season
                quali_laps.extend(laps.to_dict(orient="records"))
            except:
                continue

    def transform(val):
        val["sector_1_time"] = (
            val["sector_1_time"]
            if isinstance(val["sector_1_time"], float)
            else (
                val["sector_1_time"].total_seconds()
                if pd.notna(val["sector_1_time"])
                else None
            )
        )
        val["sector_2_time"] = (
            val["sector_2_time"]
            if isinstance(val["sector_2_time"], float)
            else (
                val["sector_2_time"].total_seconds()
                if pd.notna(val["sector_2_time"])
                else None
            )
        )
        val["sector_3_time"] = (
            val["sector_3_time"]
            if isinstance(val["sector_3_time"], float)
            else (
                val["sector_3_time"].total_seconds()
                if pd.notna(val["sector_3_time"])
                else None
            )
        )
        val["speedtrap_1"] = (
            int(val["speedtrap_1"]) if pd.notna(val["speedtrap_1"]) else None
        )
        val["speedtrap_2"] = (
            int(val["speedtrap_2"]) if pd.notna(val["speedtrap_2"]) else None
        )
        val["speedtrap_fl"] = (
            int(val["speedtrap_fl"]) if pd.notna(val["speedtrap_fl"]) else None
        )
        return val

    laps_transformed = list(map(transform, quali_laps))
    with open(f"race_laps_{season}.json", "w") as file:
        file.write(json.dumps(laps_transformed))


def insert_race_laps(season: int):
    postgres = create_engine(
        "postgresql://germanbulavkin:postgres@127.0.0.1:5432/postgres"
    )
    with open(f"race_laps_{season}.json", "r") as file:
        laps = json.loads(file.read())

    with postgres.connect() as pg_con:
        laps_table = Table("laps", MetaData(), autoload_with=postgres)
        pg_con.execute(insert(table=laps_table).values(laps))
        pg_con.commit()
