from fastapi import Depends
from models.session.Identifier import SessionIdentifier
from services.laps_data.laps import LapData
from fastf1.core import Telemetry


class TelemetryData:

    _FILTER_COLUMNS = [
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

    def __init__(self, laps_service: LapData = Depends(LapData)) -> None:
        self._laps_service = laps_service

    def _resolve_telemetry_data(self, telemetry: Telemetry):
        filtered = telemetry[self._FILTER_COLUMNS]

    def get_lap_telemetry(
        self,
        year: int,
        session_identifier: SessionIdentifier,
        grand_prix: str,
        driver_number: int,
        lap_number: int,
    ):
        laps = self._laps_service.get_laps(
            year=year, session_identifier=session_identifier, grand_prix=grand_prix
        )
        driver_telemetry = (
            laps.pick_driver(driver_number).pick_lap(lap_number).get_telemetry()
        )
