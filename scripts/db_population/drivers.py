import json
from fastapi import logger
import pandas as pd
import fastf1
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.dialects.postgresql import insert

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
    postgres = create_engine(
        "postgresql://germanbulavkin:postgres@127.0.0.1:5432/postgres"
    )
    with open("./drivers.json", "r") as drivers_file:
        drivers = json.loads(drivers_file.read())
        with postgres.connect() as pg_con:
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
