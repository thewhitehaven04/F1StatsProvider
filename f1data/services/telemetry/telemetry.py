from fastapi import Depends
from fastf1.core import Telemetry

from core.models.queries import SessionIdentifier
from services.laps.resolver import LapDataResolver


class TelemetryData:

    def __init__(
        self, laps_service: LapDataResolver = Depends(LapDataResolver)
    ) -> None:
        self._laps_service = laps_service

    def _resolve_telemetry_data(self, telemetry: Telemetry):
        return telemetry[
            [
                "RPM",
                "Speed",
                "SessionTime",
                "Time",
                "nGear",
                "Throttle",
                "Brake",
                "Distance",
                "RelativeDistance",
            ]
        ]

    def get_lap_telemetry(
        self,
        year: int,
        session_identifier: SessionIdentifier,
        grand_prix: str,
        driver_number: int,
        lap_number: int,
    ):
        laps = self._laps_service._get_laps(
            year=year, session_identifier=session_identifier, grand_prix=grand_prix
        )
        driver_telemetry = (
            laps.pick_driver(driver_number).pick_lap(lap_number).get_telemetry()
        )
