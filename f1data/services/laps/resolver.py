import fastf1
from pandas import DataFrame, isna
from fastf1.core import Laps, DataNotLoadedError

from core.models.queries import SessionIdentifier
from services.laps.models.laps import DriverLapData
from utils.retry import Retry


class LapDataResolver:
    _INDEX = [
        "Driver",
        "Team",
    ]

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
        return laps.assign(
            IsBestS1=lambda x: (laps["Sector1Time"].min() == x["Sector1Time"]),
            IsBestS2=lambda x: (laps["Sector2Time"].min() == x["Sector2Time"]),
            IsBestS3=lambda x: (laps["Sector3Time"].min() == x["Sector3Time"]),
        )

    @staticmethod
    def _set_purple_speedtraps(laps: DataFrame):
        return laps.assign(
            IsBestST1=lambda x: (laps["ST1"].min() == x["ST1"]),
            IsBestST2=lambda x: (laps["ST2"].min() == x["ST2"]),
            IsBestST3=lambda x: (laps["ST3"].min() == x["ST3"]),
        )

    @staticmethod
    def _filter_drivers(laps: Laps, drivers: list[str]):
        if len(drivers) > 0:
            laps = laps.pick_drivers(drivers)
        return laps

    def _resolve_lap_data(self, laps: Laps, drivers: list[str]) -> list[DriverLapData]:
        laps = self._filter_drivers(laps, drivers)
        formatted_laps = laps[
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
                "IsPersonalBest",
                "Stint",
                "TyreLife",
                "Position",
                "Compound",
            ]
        ]
        self._rename_sector_columns(formatted_laps)
        populated_laps = self._populate_with_data(formatted_laps)

        self._fix_floating_point_precision(populated_laps)

        indexed_data = populated_laps.set_index(self._INDEX)
        indexed_data.sort_index(inplace=True)

        purple_sectors_data = self._set_purple_sectors(indexed_data)
        purple_speedtraps_data = self._set_purple_speedtraps(purple_sectors_data)

        return [
            DriverLapData(
                driver=unique_index[0],
                team=unique_index[1],
                data=purple_speedtraps_data.loc[unique_index].to_dict(orient="records"),
            )
            for unique_index in purple_speedtraps_data.index.unique()
        ]

    def _get_laps(
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ) -> Laps:
        session = fastf1.get_session(
            year=year, identifier=session_identifier, gp=grand_prix
        )
        session.load(laps=True, telemetry=False, weather=False, messages=False)

        return session.laps

    async def get_laptimes(
        self,
        year: int,
        session_identifier: SessionIdentifier,
        grand_prix: str,
        drivers: list[str],
    ) -> list[DriverLapData]:
        laps = self._get_laps(
            year=year,
            session_identifier=session_identifier,
            grand_prix=grand_prix,
        )
        return await self.poll(self._resolve_lap_data, laps, drivers)
