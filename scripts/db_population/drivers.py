from itertools import product
import json
from fastapi import logger
import pandas as pd
import fastf1
from sqlalchemy import MetaData, Table, select, update
from sqlalchemy.dialects.postgresql import insert
from scripts.db_population.connection import engine as postgres, con


def store_driver_data_to_json():
    years = range(2024, 2025, 1)
    year_data: list[pd.DataFrame] = []
    for year in years:
        session = fastf1.get_session(
            year=year, gp="Abu Dhabi Grand Prix", identifier="Practice 1"
        )
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        results = session.results
        year_data.append(
            results[
                [
                    "BroadcastName",
                    "Abbreviation",
                    "FirstName",
                    "LastName",
                    "CountryCode",
                ]
            ]
        )

    all_drivers = (
        pd.concat(year_data)
        .drop_duplicates("BroadcastName")
        .rename(
            columns={
                "BroadcastName": "id",
                "Abbreviation": "abbreviation",
                "FirstName": "first_name",
                "LastName": "last_name",
                "CountryCode": "country_alpha3",
            }
        )
    )
    all_drivers.to_json("./drivers.json", orient="records")


def insert_drivers_into_db():
    with open("./drivers.json", "r") as drivers_file:
        drivers = json.loads(drivers_file.read())
    with con as pg_con:
        teams_table = Table("drivers", MetaData(), autoload_with=postgres)
        for driver in drivers:
            try:
                pg_con.execute(
                    insert(table=teams_table)
                    .values(driver)
                    .on_conflict_do_nothing(constraint="drivers_pkey")
                )
                pg_con.commit()
            except:
                logger.logger.error(f"Unable to insert {driver}")


def insert_driver_team_changes(season: int):
    schedule = fastf1.get_event_schedule(year=season, include_testing=False)
    driver_team_changes_table = Table(
        "driver_team_changes", MetaData(), autoload_with=postgres
    )
    sessions = product(schedule["RoundNumber"].values, range(1, 6))

    previous_row = None
    with con as pg_con:
        teams_table = Table("teams", MetaData(), autoload_with=postgres)
        previous_date = None
        for curr in sessions:
            session = fastf1.get_session(year=season, identifier=curr[1], gp=curr[0])
            session.load(laps=False, telemetry=False, weather=False, messages=False)
            results = session.results
            for result in results.itertuples():
                driver = result.BroadcastName
                team = result.TeamName
                date = session.date

                previous_row = pg_con.execute(
                    select(driver_team_changes_table)
                    .where(
                        driver_team_changes_table.c.driver_id == driver,
                        driver_team_changes_table.c.timestamp_end == None,
                    )
                    .order_by(driver_team_changes_table.c.timestamp_start.desc())
                ).fetchone()

                team_id = (
                    pg_con.execute(
                        select(teams_table).where(
                            teams_table.c.team_display_name == team
                        )
                    )
                    .fetchone()
                    .id
                )
                if not previous_row:
                    pg_con.execute(
                        insert(driver_team_changes_table).values(
                            {
                                "driver_id": driver,
                                "timestamp_start": date,
                                "timestamp_end": None,
                                "team_id": team_id,
                            }
                        )
                    )
                    pg_con.commit()
                    continue

                elif previous_row.team_id == team_id:
                    continue

                pg_con.execute(
                    update(driver_team_changes_table)
                    .values({"timestamp_end": previous_date})
                    .where(
                        driver_team_changes_table.c.driver_id == driver,
                        driver_team_changes_table.c.team_id == previous_row.team_id,
                    )
                )
                pg_con.execute(
                    insert(driver_team_changes_table).values(
                        {
                            "driver_id": driver,
                            "timestamp_start": date,
                            "timestamp_end": None,
                            "team_id": team_id,
                        }
                    )
                )
                pg_con.commit()
                previous_date = date
    
def insert_driver_numbers(season: int):
    schedule = fastf1.get_event_schedule(year=season, include_testing=False)

    with con as pg_con:
        driver_numbers_table = Table(
            "driver_numbers", MetaData(), autoload_with=postgres
        )
        for round_number in schedule["RoundNumber"].values:
            for identifier in range(1, 4):
                session = fastf1.get_session(
                    year=season, gp=round_number, identifier=identifier
                )
                session.load(laps=True, weather=False, messages=False, telemetry=False)
                results = session.results[["DriverNumber", "BroadcastName"]]
                for result in results.itertuples():
                    pg_con.execute(
                        insert(driver_numbers_table)
                        .values(
                            {
                                "driver_id": result.BroadcastName,
                                "season_year": season,
                                "driver_number": result.DriverNumber,
                            }
                        )
                        .on_conflict_do_nothing()
                    )
        pg_con.commit()