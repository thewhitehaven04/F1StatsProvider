from fastapi import Depends
import numpy as np
from pandas import DataFrame, isna
from models.laps.Identifier import LapIdentifier
from models.session.Identifier import SessionIdentifier
from services.session_fetcher.fetcher import SessionFetcher
from fastf1.core import Laps
from services.data_transformation import core, integers, laptime, speed


class LapData:
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
    ]

    _COLUMN_TRANSFORM_MAP = {
        "LapTime": laptime.laptime_to_seconds,
        "Sector1Time": laptime.laptime_to_seconds,
        "Sector2Time": laptime.laptime_to_seconds,
        "Sector3Time": laptime.laptime_to_seconds,
        "SpeedI1": speed.speed_to_float_or_null,
        "SpeedI2": speed.speed_to_float_or_null,
        "SpeedFL": speed.speed_to_float_or_null,
        "LapNumber": integers.int_or_null,
        "Stint": integers.int_or_null,
        "TyreLife": integers.int_or_null,
        "Position": integers.int_or_null,
        "IsOutlap": core.identity,
        "IsInlap": core.identity,
    }

    _INDEX = [
        "Driver",
        "Team",
    ]

    def __init__(
        self, session_fetcher: SessionFetcher = Depends(SessionFetcher)
    ) -> None:
        self._session_fetcher = session_fetcher

    @staticmethod
    def _populate_with_data(laps: DataFrame): 
        laps["IsOutlap"] = isna(laps["Sector1Time"])
        laps['IsInlap'] = isna(laps['Sector3Time'])
        return laps

    def _resolve_lap_data(self, laps: Laps):
        formatted_laps = laps[self._LAP_COLUMNS_FILTER]
        populated_laps = self._populate_with_data(formatted_laps)

        indexed_data = populated_laps.set_index(self._INDEX)
        return [
            {
                "driver": unique_index[0],
                "team": unique_index[1],
                "data": indexed_data.loc[unique_index]
                .transform(self._COLUMN_TRANSFORM_MAP)
                .replace(np.nan, None)
                .to_dict(orient="records"),
            }
            for unique_index in indexed_data.index.unique()
        ]

    def get_laps(
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ) -> Laps:
        session = self._session_fetcher.load_session_data(
            year=year, session_identifier=session_identifier, grand_prix=grand_prix
        )
        return session.laps

    def get_laptimes(
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ):
        laps = self.get_laps(
            year=year, session_identifier=session_identifier, grand_prix=grand_prix
        )
        return self._resolve_lap_data(laps)

    def calculate_delta(
        self,
        year: int,
        session_identifier: SessionIdentifier,
        grand_prix: str,
        lap_identifiers: list[LapIdentifier],
    ):
        laps = self.get_laps(
            year=year, session_identifier=session_identifier, grand_prix=grand_prix
        )
        telemetries = list(
            map(
                lambda lap_identifier: laps.pick_driver(lap_identifier.driver).pick_lap(
                    lap_identifier.lap
                ),
                lap_identifiers,
            )
        )

        base_telemetry, *compared_telemetries = telemetries

        space = base_telemetry["RelativeDistance"]

        deltas = []
        for index, telemetry in enumerate(compared_telemetries):
            interpolated_value = telemetry["Time"].dt.total_seconds()
            xp = telemetry["RelativeDistance"]

            deltas.append(
                {
                    "driver": lap_identifiers[index].driver,
                    "values": np.interp(x=space, xp=xp, fp=interpolated_value),
                }
            )

        return telemetries