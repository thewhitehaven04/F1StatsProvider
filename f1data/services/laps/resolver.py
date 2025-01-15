import fastf1
from pandas import DataFrame, Series, isna, concat
from fastf1.core import Laps, DataNotLoadedError

from core.models.queries import SessionIdentifier, SessionQuery
from services.laps.models.laps import DriverLapData
from utils.retry import Retry


class LapDataResolver:
    def __init__(self) -> None:
        self.poll = Retry(
            polling_interval_seconds=0.2,
            timeout_seconds=30,
            ignored_exceptions=(DataNotLoadedError,),
        )

    @staticmethod
    def _populate_with_data(laps: DataFrame):
        return laps.assign(
            IsOutlap=isna(laps["Sector1Time"]),
            IsInlap=isna(laps["Sector3Time"]),
        )

    @staticmethod
    def _rename_sector_columns(laps: DataFrame):
        laps.rename(
            columns={"SpeedI1": "ST1", "SpeedI2": "ST2", "SpeedFL": "ST3"}, inplace=True
        )
        return laps

    @staticmethod
    def _fix_floating_point_precision(laps: DataFrame):
        laps["LapTime"].round(3)
        laps["Sector1Time"].round(3)
        laps["Sector2Time"].round(3)
        laps["Sector3Time"].round(3)

    @staticmethod
    def _set_purple_sectors(laps: DataFrame):
        purple_s1 = laps["Sector1Time"].min()
        purple_s2 = laps["Sector2Time"].min()
        purple_s3 = laps["Sector3Time"].min()

        return laps.assign(
            IsBestS1=lambda x: (purple_s1 == x["Sector1Time"]),
            IsBestS2=lambda x: (purple_s2 == x["Sector2Time"]),
            IsBestS3=lambda x: (purple_s3 == x["Sector3Time"]),
        )

    @staticmethod
    def _set_purple_speedtraps(laps: DataFrame):
        st1_max = laps["ST1"].max()
        st2_max = laps["ST2"].max()
        st3_max = laps["ST3"].max()

        return laps.assign(
            IsBestST1=lambda x: (st1_max == x["ST1"]),
            IsBestST2=lambda x: (st2_max == x["ST2"]),
            IsBestST3=lambda x: (st3_max == x["ST3"]),
        )

    @staticmethod
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

    @staticmethod
    def _set_is_personal_best(laps: DataFrame):
        # this personal best returns actual personal best laptime across
        # the whole session, unlike the built in `IsPersonalBest` attribute
        # that returns "rolling" personal best, i.e. the personal best at that point in time
        # which means that there are multiple personal bests in the same session
        personal_best_laps = laps.groupby("Driver")["LapTime"].min()
        for driver, laptime in personal_best_laps.items():
            current_driver_laptimes = laps[laps["Driver"] == driver]["LapTime"]
            laps.loc[laps["Driver"] == driver, "IsPB"] = (
                laptime == current_driver_laptimes
            )

        return laps

    @staticmethod
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
        self, laps: Laps, queries: list[SessionQuery]
    ) -> list[DriverLapData]:
        filtered_laps = self._filter_session(laps, queries)
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
        self._rename_sector_columns(formatted_laps)
        populated_laps = self._populate_with_data(formatted_laps)

        self._fix_floating_point_precision(populated_laps)
        self._set_is_personal_best_sector(populated_laps)
        pb_laps = self._set_is_personal_best(populated_laps)
        purple_sector_laps = self._set_purple_sectors(pb_laps)
        data = self._set_purple_speedtraps(purple_sector_laps)

        data.set_index(["Driver", "Team"], inplace=True)

        return [
            DriverLapData(
                driver=index[0],
                team=index[1],
                data=(
                    [data.loc[index].to_dict()]
                    if isinstance(data.loc[index], Series)
                    else data.loc[index].to_dict(orient="records")
                ),
            )
            for index in data.index.unique()
        ]

    def get_laps(
        self, year: str, session_identifier: SessionIdentifier, grand_prix: str
    ) -> Laps:
        session = fastf1.get_session(
            year=int(year), identifier=session_identifier, gp=grand_prix
        )
        session.load(laps=True, telemetry=False, weather=False, messages=False)

        return session.laps

    async def get_laptimes(
        self,
        year: str,
        session_identifier: SessionIdentifier,
        grand_prix: str,
        queries: list[SessionQuery],
    ) -> list[DriverLapData]:
        laps = self.get_laps(
            year=year,
            session_identifier=session_identifier,
            grand_prix=grand_prix,
        )
        return await self.poll(self._resolve_lap_data, laps, queries)
