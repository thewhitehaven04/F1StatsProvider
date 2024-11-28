import fastf1
import numpy as np
from pandas import DataFrame, isna
from fastf1.core import Laps, DataNotLoadedError

from core.models.queries import SessionIdentifier
from services.laps.models.laps import DriverLapDataOut
from utils import transformers
from utils.retry import Retry


class LapDataResolver:
    _INDEX = [
        "Driver",
        "Team",
    ]

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

    @staticmethod
    def _fix_floating_point_precision(laps: DataFrame):
        laps["LapTime"].round(3)
        laps["Sector1Time"].round(3)
        laps["Sector2Time"].round(3)
        laps["Sector3Time"].round(3)

    def _resolve_lap_data(self, laps: Laps) -> list[DriverLapDataOut]:
        formatted_laps = laps[
            [
                "Driver",
                "Team",
                "LapNumber",
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

        return [
            DriverLapDataOut(
                driver=unique_index[0],
                team=unique_index[1],
                data=indexed_data.loc[unique_index]
                .transform(
                    {
                        "LapTime": transformers.laptime_to_seconds,
                        "Sector1Time": transformers.laptime_to_seconds,
                        "Sector2Time": transformers.laptime_to_seconds,
                        "Sector3Time": transformers.laptime_to_seconds,
                        "ST1": transformers.int_or_null,
                        "ST2": transformers.int_or_null,
                        "ST3": transformers.int_or_null,
                        "LapNumber": transformers.int_or_null,
                        "Stint": transformers.int_or_null,
                        "TyreLife": transformers.int_or_null,
                        "Position": transformers.int_or_null,
                        "Compound": transformers.identity,
                        "IsOutlap": transformers.identity,
                        "IsInlap": transformers.identity,
                    }
                )
                .replace(np.nan, None),
            )
            for unique_index in indexed_data.index.unique()
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
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ) -> list[DriverLapDataOut]:
        laps = self._get_laps(
            year=year,
            session_identifier=session_identifier,
            grand_prix=grand_prix,
        )
        res = await Retry(
            polling_interval_seconds=0.2,
            timeout_seconds=30,
            ignored_exceptions=(DataNotLoadedError,),
        )(self._resolve_lap_data, laps)
        return res
