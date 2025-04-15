import pandas as pd
import fastf1
from sqlalchemy import MetaData, Table, create_engine, select
from sqlalchemy.dialects.postgresql import insert


def insert_teams_into_db():
    years = range(2018, 2026, 1)
    postgres = create_engine(
        "postgresql://germanbulavkin:postgres@127.0.0.1:5432/postgres"
    )
    year_data: list[pd.DataFrame] = []
    for year in years:
        session = fastf1.get_session(year=year, gp=1, identifier="Practice 1")
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        results = session.results
        year_data.append(results[["TeamName"]])

    all_teams = (
        pd.concat(year_data)
        .drop_duplicates()
        .rename(
            columns={
                "TeamName": "team_display_name",
            }
        )
    )
    with postgres.connect() as pg_con:
        teams_table = Table("teams", MetaData(), autoload_with=postgres)
        pg_con.execute(
            insert(table=teams_table).values(all_teams.to_dict(orient="records"))
        )
        pg_con.commit()

    return all_teams


def insert_team_colors_into_db():
    years = range(2019, 2026, 1)
    postgres = create_engine(
        "postgresql://germanbulavkin:postgres@127.0.0.1:5432/postgres"
    )
    for year in years:
        session = fastf1.get_session(year=year, gp=1, identifier="Practice 1")
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        results = session.results[["TeamId", "TeamColor", "TeamName"]].rename(
            columns={
                "TeamId": "team_source_id",
                "TeamColor": "color",
            }
        )
        results[["season_year"]] = year

        with postgres.connect() as pg_con:
            metadata = MetaData()
            teams_table = Table("teams", metadata, autoload_with=postgres)
            teams = pg_con.execute(select(teams_table)).all()
            teams_df = pd.DataFrame(columns=["id", "team_database_name"], data=teams)
            joined = (
                results.set_index("TeamName")
                .join(teams_df.set_index("team_database_name"))
                .rename(
                    columns={
                        "id": "team_id",
                    }
                )[["team_id", "season_year", "color"]]
                .drop_duplicates("team_id")
            )
            team_season_colors_table = Table(
                "team_season_colors", metadata, autoload_with=postgres
            )
            pg_con.execute(
                insert(table=team_season_colors_table).values(
                    joined.to_dict(orient="records")
                )
            )
            pg_con.commit()
