import pandas as pd
from fastf1.core import SessionResults, Laps

from f1data.core.models.queries import SessionIdentifier
from services.session.registry import get_loader


def _resolve_racelike_data(data: SessionResults):
    racelike_data = (
        data[
            [
                "DriverNumber",
                "FullName",
                "TeamName",
                "TeamId",
                "CountryCode",
                "Time",
                "GridPosition",
                "Status",
                "Points",
            ]
        ]
        .rename(columns={"FullName": "Driver", "Time": "Gap"})
        .assign(
            Time=pd.Series(
                index=data.index,
                data=[
                    data["Time"].iloc[0],
                    *(data["Time"].iloc[1:].add(data["Time"].iloc[0])),
                ],
            )
        )
    )

    racelike_data.iloc[0, 5] = pd.Timedelta(0)

    return racelike_data.to_dict(orient="records")


def _resolve_practice_data(data: SessionResults, laps: Laps):
    return (
        data[
            [
                "DriverNumber",
                "FullName",
                "TeamName",
                "TeamId",
                "CountryCode",
            ]
        ]
        .rename(
            columns={
                "FullName": "Driver",
            }
        )
        .assign(Time_=laps.groupby("DriverNumber").agg({"LapTime": "min"}))
        .sort_values(by=["Time_"], ascending=True)
        .assign(Gap=lambda x: x["Time_"].sub(x["Time_"].iloc[0]))
        .to_dict(orient="records")
    )


def _resolve_qualifying_data(data: SessionResults):
    return (
        data[
            [
                "DriverNumber",
                "FullName",
                "TeamName",
                "TeamId",
                "Position",
                "Q1",
                "Q2",
                "Q3",
                "CountryCode",
            ]
        ]
        .rename(
            columns={
                "FullName": "Driver",
                "Q1": "Q1Time",
                "Q2": "Q2Time",
                "Q3": "Q3Time",
            }
        )
        .to_dict(orient="records")
    )


def get_results(
    year: str,
    session_identifier: SessionIdentifier | int,
    round: int,
    is_testing: bool = False,
):
    loader = get_loader(
        year=year,
        round=round,
        session_identifier=session_identifier,
        is_testing=is_testing,
    )

    if (
        session_identifier
        in [
            SessionIdentifier.FP1,
            SessionIdentifier.FP2,
            SessionIdentifier.FP3,
        ]
        or is_testing
    ):
        return _resolve_practice_data(loader.results, loader.laps)

    if int(year) >= 2024:
        if (
            session_identifier == SessionIdentifier.QUALIFYING
            or session_identifier == SessionIdentifier.SPRINT_QUALIFYING
        ):
            return _resolve_qualifying_data(loader.results)

        return _resolve_racelike_data(loader.results)

    else:
        if (
            session_identifier == SessionIdentifier.QUALIFYING
            or session_identifier == SessionIdentifier.SHOOTOUT
        ):
            return _resolve_qualifying_data(loader.results)
        return _resolve_racelike_data(loader.results)
