import time
import fastf1
import numpy as np
from pandas import DataFrame, isna
from models.session.Identifier import SessionIdentifier
from services.laps_data.model import DriverLapDataOut
from services.data_transformation import core, integers, laptime
from utils.Retry import Retry
from fastf1.core import Laps, DataNotLoadedError


class LapDataResolver:
    _LAP_COLUMNS_FILTER = [
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

    _COLUMN_TRANSFORM_MAP = {
        "LapTime": laptime.laptime_to_seconds,
        "Sector1Time": laptime.laptime_to_seconds,
        "Sector2Time": laptime.laptime_to_seconds,
        "Sector3Time": laptime.laptime_to_seconds,
        "ST1": integers.int_or_null,
        "ST2": integers.int_or_null,
        "ST3": integers.int_or_null,
        "LapNumber": integers.int_or_null,
        "Stint": integers.int_or_null,
        "TyreLife": integers.int_or_null,
        "Position": integers.int_or_null,
        "Compound": core.identity,
        "IsOutlap": core.identity,
        "IsInlap": core.identity,
    }

    _INDEX = [
        "Driver",
        "Team",
    ]

    @staticmethod
    def _populate_with_data(laps: DataFrame):
        laps.loc[:, "IsOutlap"] = isna(laps["Sector1Time"])
        laps.loc[:, "IsInlap"] = isna(laps["Sector3Time"])
        return laps

    @staticmethod
    def _rename_sector_columns(laps: DataFrame):
        laps.rename(
            columns={"SpeedI1": "ST1", "SpeedI2": "ST2", "SpeedFL": "ST3"}, inplace=True
        )

    @staticmethod
    def _fix_floating_point_precision(laps: DataFrame):
        laps.loc[:, "LapTime"] = laps["LapTime"].round(3)
        laps.loc[:, "Sector1Time"] = laps["Sector1Time"].round(3)
        laps.loc[:, "Sector2Time"] = laps["Sector2Time"].round(3)
        laps.loc[:, "Sector3Time"] = laps["Sector3Time"].round(3)

    def _resolve_lap_data(self, laps: Laps) -> list[DriverLapDataOut]:
        t_resolve_start = time.time()
        formatted_laps = laps[self._LAP_COLUMNS_FILTER]
        self._rename_sector_columns(formatted_laps)
        populated_laps = self._populate_with_data(formatted_laps)

        self._fix_floating_point_precision(populated_laps)

        indexed_data = populated_laps.set_index(self._INDEX)
        indexed_data.sort_index(inplace=True)

        print(f"\n\n-------Laps resolved in {time.time() - t_resolve_start} seconds-------\n\n")
        return [
            DriverLapDataOut(
                driver=unique_index[0],
                team=unique_index[1],
                data=indexed_data.loc[unique_index]
                .transform(self._COLUMN_TRANSFORM_MAP)
                .replace(np.nan, None)
                .to_dict(orient="records"),
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
        t_loading_start = time.time()
        laps = self._get_laps(
            year=year,
            session_identifier=session_identifier,
            grand_prix=grand_prix,
        )
        res = await Retry(
            polling_interval_seconds=0.2,
            timeout_seconds=30,
            ignored_exceptions=(DataNotLoadedError,),
        ).call(self._resolve_lap_data, laps)
        print(f"\n\n-------Laps loaded in {time.time() - t_loading_start} seconds-------\n\n")
        return res

    # def calculate_delta(
    #     self,
    #     year: int,
    #     session_identifier: SessionIdentifier,
    #     grand_prix: str,
    #     lap_identifiers: list[LapIdentifier],
    # ):
    #     laps = self.get_laps(
    #         year=year, session_identifier=session_identifier, grand_prix=grand_prix
    #     )
    #     telemetries = list(
    #         map(
    #             lambda lap_identifier: laps.pick_driver(lap_identifier.driver).pick_lap(
    #                 lap_identifier.lap
    #             ),
    #             lap_identifiers,
    #         )
    #     )

    #     base_telemetry, *compared_telemetries = telemetries

    #     space = base_telemetry["RelativeDistance"]

    #     deltas = []
    #     for index, telemetry in enumerate(compared_telemetries):
    #         interpolated_value = telemetry["Time"].dt.total_seconds()
    #         xp = telemetry["RelativeDistance"]

    #         deltas.append(
    #             {
    #                 "driver": lap_identifiers[index].driver,
    #                 "values": np.interp(x=space, xp=xp, fp=interpolated_value),
    #             }
    #         )

    #     return telemetries
