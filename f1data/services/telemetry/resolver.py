from datetime import timedelta

from core.models.queries import SessionIdentifier, TelemetryRequest
from services.laps.loader import SessionLoader
from pandas import timedelta_range
from fastf1.plotting import get_driver_color


class TelemetryResolver:

    def __init__(
        self, year: str, session_identifier: SessionIdentifier, grand_prix: str
    ) -> None:
        self._session_loader = SessionLoader(year, session_identifier, grand_prix)

    async def _pick_laps_telemetry(self, laps: list[int], driver: str):
        telemetry = await self._session_loader.lap_telemetry
        return telemetry.pick_driver(driver).pick_laps(laps).get_telemetry()

    async def _pick_lap_telemetry(self, lap: str, driver: str):
        return (
            (await self._session_loader.lap_telemetry)
            .pick_driver(driver)
            .pick_lap(int(lap))
            .get_telemetry()
        )

    async def get_interpolated_telemetry_comparison(
        self, comparison: list[TelemetryRequest]
    ):
        response = []
        for instance in comparison:
            driver_telemetry = (
                await self._pick_laps_telemetry(instance.lap_filter, instance.driver)
            )[
                [
                    "Throttle",
                    "nGear",
                    "Speed",
                    "RPM",
                    "RelativeDistance",
                    "Distance",
                    "Time",
                ]
            ]

            time_based_driver_telemetry = driver_telemetry.set_index("Time")
            max_index = time_based_driver_telemetry.index.max()
            new_index = timedelta_range(timedelta(seconds=0), max_index, freq="125ms")
            time_based_driver_telemetry.reindex(new_index)

            for col in ["RelativeDistance", "Distance", "Speed", "Throttle"]:
                time_based_driver_telemetry[col] = time_based_driver_telemetry[
                    col
                ].interpolate("quadratic")

            time_based_driver_telemetry["nGear"] = time_based_driver_telemetry[
                "nGear"
            ].interpolate("nearest")

            response.append(
                {
                    "driver": instance.driver,
                    "color": get_driver_color(
                        instance.driver, self._session_loader.session
                    ),
                    "telemetry": time_based_driver_telemetry.rename(
                        columns={"nGear": "Gear"}
                    )
                    .reset_index()
                    .to_dict(orient="list", index=True),
                }
            )

        return response

    async def get_telemetry_comparison(self, comparison: list[TelemetryRequest]):
        return [
            {
                "driver": req.driver,
                "color": get_driver_color(req.driver, self._session_loader.session),
                "telemetry": (
                    await self._pick_laps_telemetry(req.lap_filter, req.driver)
                )[
                    [
                        "Throttle",
                        "nGear",
                        "Speed",
                        "RPM",
                        "RelativeDistance",
                        "Distance",
                        "Time",
                    ]
                ]
                .rename(columns={"nGear": "Gear"})
                .to_dict(orient="list"),
            }
            for req in comparison
        ]

    async def get_telemetry(self, driver: str, lap: str):
        telemetry = await self._pick_lap_telemetry(lap, driver)
        return {
            "driver": driver,
            "color": get_driver_color(driver, self._session_loader.session),
            "telemetry": telemetry[
                [
                    "Throttle",
                    "nGear",
                    "Speed",
                    "RPM",
                    "RelativeDistance",
                    "Distance",
                    "Time",
                ]
            ]
            .rename(columns={"nGear": "Gear"})
            .to_dict(orient="list"),
        }
