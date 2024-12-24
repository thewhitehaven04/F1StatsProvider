from core.models.queries import SessionIdentifier, TelemetryRequest
from services.laps.loader import SessionLoader


class TelemetryResolver:

    def __init__(
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ) -> None:
        self._loader = SessionLoader(year, session_identifier, grand_prix)

    async def _pick_lap_telemetry(self, laps: list[int], driver: str):
        telemetry = await self._loader.lap_telemetry
        return telemetry.pick_driver(driver).pick_laps(laps)

    async def get_interpolated_telemetry_comparison(
        self, comparison: list[TelemetryRequest]
    ):
        response = []
        for c in comparison:
            driver_telemetry = await self._pick_lap_telemetry(c.laps, c.driver)

            time_based_driver_telemetry = driver_telemetry.set_index("Time")
            for col in ["RelativeDistance", "Distance", "Speed", "RPM", "Throttle"]:
                time_based_driver_telemetry[col] = (
                    time_based_driver_telemetry["col"]
                    .resample("0.125s")
                    .mean()
                    .interpolate("quadratic")
                )

            time_based_driver_telemetry["nGear"] = (
                time_based_driver_telemetry["Gear"]
                .resample("0.125s")
                .nearest()
                .interpolate("nearest")
            )

            response.append(
                {
                    "driver": c.driver,
                    "telemetry": time_based_driver_telemetry.rename(
                        columns={"nGear": "Gear"}
                    ).to_dict(orient="list"),
                }
            )

        return response

    async def get_telemetry_comparison(self, comparison: list[TelemetryRequest]):
        return [
            {
                "driver": req.driver,
                "telemetry": (await self._pick_lap_telemetry(req.laps, req.driver))
                .rename(columns={"nGear": "Gear"})
                .to_dict(orient="list"),
            }
            for req in comparison
        ]
