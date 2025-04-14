import fastf1
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.dialects.postgresql import insert
import pandas as pd
import json
from fastapi import logger


def store_practice_telemetry(season: int):
    telemetries = []
    schedule = fastf1.get_event_schedule(year=season, include_testing=False)
    postgres = create_engine(
        "postgresql://germanbulavkin:postgres@127.0.0.1:5432/postgres"
    )
    laps_table = Table("laps", MetaData(), autoload_with=postgres)

    with postgres.connect() as pg_con:
        for round_number in schedule["RoundNumber"].values:
            max_range = (
                4
                if schedule[schedule["RoundNumber"] == round_number][
                    "EventFormat"
                ].iloc[0]
                == "conventional"
                else 2
            )
            for identifier in range(1, max_range):
                session = fastf1.get_session(
                    year=season, gp=round_number, identifier=identifier
                )
                # uncomment if previously loaded
                session.load(laps=True, telemetry=True, weather=False, messages=False)
                drivers = session.results[["BroadcastName", "DriverNumber"]].values
                for driver in drivers:
                    driver_laps = session.laps.pick_drivers(driver[1])
                    lap_numbers = driver_laps["LapNumber"].values
                    for lap_number in lap_numbers:
                        lap = driver_laps.pick_laps(lap_number)
                        try:
                            telemetry = (
                                lap.get_car_data()[
                                    [
                                        "Speed",
                                        "RPM",
                                        "nGear",
                                        "Throttle",
                                        "Brake",
                                        "Time",
                                    ]
                                ]
                                .add_distance()
                                .rename(
                                    {
                                        "Speed": "speed",
                                        "RPM": "rpm",
                                        "Throttle": "throttle",
                                        "Distance": "distance",
                                        "Brake": "brake",
                                        "nGear": "gear",
                                        "Time": "laptime_at",
                                    }
                                )
                            )
                            lap_id = (
                                pg_con.execute(
                                    select(laps_table).where(
                                        laps_table.c.lap_number == int(lap_number),
                                        laps_table.c.driver_id == driver[0],
                                        laps_table.c.season_year == season,
                                        laps_table.c.session_type_id
                                        == f"Practice {identifier}",
                                        laps_table.c.event_name
                                        == session.event.EventName,
                                    )
                                )
                                .fetchone()
                                ._tuple()[0]
                            )
                            telemetry[["lap_id"]] = lap_id
                            telemetry.Time = telemetry.Time.transform(
                                lambda x: x.total_seconds() if pd.notna(x) else None
                            )
                            telemetries.extend(telemetry.to_dict(orient="records"))
                        except:
                            logger.logger.warning(
                                "Unable to load session: %s %s %s",
                                identifier,
                                driver,
                                lap_number,
                            )
                            continue

    with open(f"telemetry_practice_{season}.json", "w") as file:
        file.write(json.dumps(telemetries))


def insert_practice_telemetry(season: int):
    postgres = create_engine(
        "postgresql://germanbulavkin:postgres@127.0.0.1:5432/postgres"
    )
    with open(f"telemetry_practice_{season}.json", "r") as file:
        file_read = json.loads(file.read())

    telemetry_table = Table(
        "telemetry_measurements", MetaData(), autoload_with=postgres
    )
    with postgres.connect() as pg_con:
        pg_con.execute(insert(table=telemetry_table).values(file_read))
        pg_con.commit()
