from pandas import DataFrame, NamedAgg, isna, concat
from fastf1.core import Laps, Session 
from fastf1.plotting import get_driver_color

from core.models.queries import SessionIdentifier, SessionQuery
from services.laps.models.laps import DriverLapData, LapSelectionData, StintData
from services.session.session import get_loader


def _populate_with_data(laps: DataFrame):
    return laps.assign(
        IsOutlap=isna(laps["Sector1Time"]),
        IsInlap=isna(laps["Sector3Time"]),
        IsFlyingLap=(laps["PitInTime"].isna() & laps["PitOutTime"].isna()),
    )


def _rename_sector_columns(laps: DataFrame):
    laps.rename(
        columns={"SpeedI1": "ST1", "SpeedI2": "ST2", "SpeedFL": "ST3"}, inplace=True
    )
    return laps


def _fix_floating_point_precision(laps: DataFrame):
    laps[["LapTime", "Sector1Time", "Sector2Time", "Sector3Time"]].round(3)


def _set_purple_sectors(laps: DataFrame):
    purple_s1 = laps["Sector1Time"].min()
    purple_s2 = laps["Sector2Time"].min()
    purple_s3 = laps["Sector3Time"].min()

    laps["IsBestS1"] = laps["Sector1Time"] == purple_s1
    laps["IsBestS2"] = laps["Sector2Time"] == purple_s2
    laps["IsBestS3"] = laps["Sector3Time"] == purple_s3


def _set_purple_speedtraps(laps: DataFrame):
    st1_max = laps["ST1"].max()
    st2_max = laps["ST2"].max()
    st3_max = laps["ST3"].max()

    laps["IsBestST1"] = laps["ST1"] == st1_max
    laps["IsBestST2"] = laps["ST2"] == st2_max
    laps["IsBestST3"] = laps["ST3"] == st3_max


def _set_is_personal_best_sector(laps: DataFrame):
    pb_s1 = laps.groupby("Driver")["Sector1Time"].min()
    pb_s2 = laps.groupby("Driver")["Sector2Time"].min()
    pb_s3 = laps.groupby("Driver")["Sector3Time"].min()

    for driver, laptime in pb_s1.items():
        sector_times = laps[laps["Driver"] == driver]["Sector1Time"]
        laps.loc[laps["Driver"] == driver, "IsPBS1"] = sector_times == laptime

    for driver, laptime in pb_s2.items():
        sector_times = laps[laps["Driver"] == driver]["Sector2Time"]
        laps.loc[laps["Driver"] == driver, "IsPBS2"] = sector_times == laptime

    for driver, laptime in pb_s3.items():
        sector_times = laps[laps["Driver"] == driver]["Sector3Time"]
        laps.loc[laps["Driver"] == driver, "IsPBS3"] = sector_times == laptime


def _set_is_personal_best(laps: DataFrame):
    # this personal best returns actual personal best laptime across
    # the whole session, unlike the built in `IsPersonalBest` attribute
    # that returns "rolling" personal best, i.e. the personal best at that point in time
    # which means that there are multiple personal bests in the same session
    personal_best_laps = laps.groupby("Driver")["LapTime"].min()
    for driver, laptime in personal_best_laps.items():
        current_driver_laptimes = laps[laps["Driver"] == driver]["LapTime"]
        laps.loc[laps["Driver"] == driver, "IsPB"] = laptime == current_driver_laptimes

    return laps


def _filter_session(laps: Laps, queries: list[SessionQuery]) -> Laps:
    return concat(
        [
            (
                laps.pick_driver(query.driver).pick_laps(query.lap_filter)
                if query.lap_filter
                else laps.pick_driver(query.driver)
            )
            for query in queries
        ]
    )  # type: ignore


def _resolve_lap_data(
    session: Session, current_driver_laps: Laps, queries: list[SessionQuery]
) -> LapSelectionData:
    filtered_laps = _filter_session(current_driver_laps, queries)
    formatted_laps = filtered_laps[
        [
            "Driver",
            "Team",
            "LapTime",
            "Sector1Time",
            "Sector2Time",
            "Sector3Time",
            "SpeedI1",
            "SpeedI2",
            "SpeedFL",
            "Stint",
            "TyreLife",
            "Position",
            "Compound",
            "PitInTime",
            "PitOutTime",
        ]
    ]
    _rename_sector_columns(formatted_laps)
    populated_laps = _populate_with_data(formatted_laps)

    _fix_floating_point_precision(populated_laps)
    _set_is_personal_best_sector(populated_laps)
    _set_is_personal_best(populated_laps)
    _set_purple_sectors(populated_laps)
    _set_purple_speedtraps(populated_laps)

    populated_laps.set_index(["Driver", "Team"], inplace=True)
    lap_data = []
    for index in populated_laps.index.unique():
        current_driver_laps = populated_laps.loc[[index]]
        flying_laps = current_driver_laps[current_driver_laps["IsFlyingLap"]]
        stint_groups = flying_laps.groupby("Stint")
        filtered_stint_groups = stint_groups.agg(
            avg_time=NamedAgg(column="LapTime", aggfunc="mean"),
            min_time=NamedAgg(column="LapTime", aggfunc="min"),
            max_time=NamedAgg(column="LapTime", aggfunc="max"),
            low_quartile=NamedAgg(column="LapTime", aggfunc=lambda x: x.quantile(0.25)),
            high_quartile=NamedAgg(
                column="LapTime", aggfunc=lambda x: x.quantile(0.75)
            ),
            median=NamedAgg(column="LapTime", aggfunc=lambda x: x.median()),
            total_laps=NamedAgg(column="LapTime", aggfunc="count"),
        )

        lap_data.append(
            DriverLapData(
                driver=index[0],
                team=index[1],
                color=get_driver_color(identifier=index[0], session=session),
                stints=filtered_stint_groups.to_dict(orient="records"),
                session_data=StintData(
                    total_laps=len(current_driver_laps),
                    avg_time=(flying_laps["LapTime"].mean()),
                    min_time=(current_driver_laps["LapTime"].min()),
                    max_time=(current_driver_laps["LapTime"].max()),
                    low_quartile=(current_driver_laps["LapTime"].quantile(0.25)),
                    high_quartile=(current_driver_laps["LapTime"].quantile(0.75)),
                    median=(flying_laps["LapTime"].median()),
                ),
                laps=(current_driver_laps.to_dict(orient="records")),
            )
        )

    lap_data.sort(key=lambda x: x.session_data.min_time)
    flying_laps = populated_laps[populated_laps["IsFlyingLap"]]
    return LapSelectionData(
        driver_lap_data=lap_data,
        low_decile=flying_laps["LapTime"].quantile(0.1),  # type: ignore
        high_decile=flying_laps["LapTime"].quantile(0.9),  # type: ignore
        min_time=populated_laps["LapTime"].min(),
        max_time=populated_laps["LapTime"].max(),
    )


def get_resolved_laptime_data(
    year: str,
    event: str,
    session_identifier: SessionIdentifier,
    queries: list[SessionQuery]
) -> LapSelectionData:
    loader = get_loader(year, event, session_identifier)
    return _resolve_lap_data(loader.session, loader.laps, queries)
