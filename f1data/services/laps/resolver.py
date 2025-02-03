from pandas import DataFrame, Series, isna, concat
from fastf1.core import Laps, Session, Lap
from fastf1.plotting import get_driver_color

from core.models.queries import SessionQuery
from services.laps.models.laps import DriverLapData, LapSelectionData
from services.session.session import SessionLoader


def _populate_with_data(laps: DataFrame):
    return laps.assign(
        IsOutlap=isna(laps["Sector1Time"]),
        IsInlap=isna(laps["Sector3Time"]),
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


async def _resolve_lap_data(
    session: Session, laps: Laps, queries: list[SessionQuery]
) -> LapSelectionData:
    filtered_laps = _filter_session(laps, queries)
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

    lap_data = [
        DriverLapData(
            driver=index[0],
            team=index[1],
            color=get_driver_color(identifier=index[0], session=session),
            total_laps=len(populated_laps.loc[index]),
            avg_time=(
                populated_laps.loc[index]["LapTime"]
                if isinstance(populated_laps.loc[index], Lap)
                else populated_laps.loc[index]["LapTime"].mean()
            ),
            min_time=(
                populated_laps.loc[index]["LapTime"]
                if isinstance(populated_laps.loc[index], Lap)
                else populated_laps.loc[index]["LapTime"].min()
            ),
            max_time=(
                populated_laps.loc[index]["LapTime"]
                if isinstance(populated_laps.loc[index], Lap)
                else populated_laps.loc[index]["LapTime"].max()
            ),
            low_quartile=(
                populated_laps.loc[index]["LapTime"]
                if isinstance(populated_laps.loc[index], Lap)
                else populated_laps.loc[index]["LapTime"].quantile(0.25)
            ),
            high_quartile=(
                populated_laps.loc[index]["LapTime"]
                if isinstance(populated_laps.loc[index], Lap)
                else populated_laps.loc[index]["LapTime"].quantile(0.75)
            ),
            median=(
                populated_laps.loc[index]["LapTime"]
                if isinstance(populated_laps.loc[index], Lap)
                else populated_laps.loc[index]["LapTime"].median()
            ),
            data=(
                [populated_laps.loc[index].to_dict()]
                if isinstance(populated_laps.loc[index], Series)
                else populated_laps.loc[index].to_dict(orient="records")
            ),
        )
        for index in populated_laps.index.unique()
    ]
    lap_data.sort(key=lambda x: x.min_time)
    return LapSelectionData(
        driver_lap_data=lap_data,
        low_decile=formatted_laps["LapTime"].quantile(0.1),  # type: ignore
        high_decile=formatted_laps["LapTime"].quantile(0.9),  # type: ignore
        min_time=formatted_laps["LapTime"].min(),
        max_time=formatted_laps["LapTime"].max(),
    )


async def get_resolved_laptime_data(
    loader: SessionLoader, queries: list[SessionQuery]
) -> LapSelectionData:
    return await _resolve_lap_data(loader.session, await loader.laps, queries)
