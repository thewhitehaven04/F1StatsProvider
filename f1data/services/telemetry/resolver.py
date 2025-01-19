from datetime import timedelta

from core.models.queries import SessionIdentifier, TelemetryRequest
from services.laps.loader import SessionLoader
from pandas import timedelta_range, concat
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
        telemetry = await self._session_loader.lap_telemetry
        laps = concat(
            [
                telemetry.pick_drivers(req.driver).pick_laps(req.lap_filter)
                for req in comparison
            ]
        )
        reference_laptime = laps["LapTime"].min()

        reference_lap = laps.loc[laps["LapTime"] == reference_laptime]
        comparison_laps = laps.loc[laps["LapTime"] != reference_laptime]

        # interpolate reference data
        reference_telemetry = telemetry.pick_driver(
            reference_lap["Driver"]
        ).get_telemetry()
        reference_telemetry = reference_telemetry.set_index("Time")
        max_index = reference_telemetry.index.max()
        reference_telemetry.reindex(
            timedelta_range(timedelta(seconds=0), max_index, freq="200ms")
        )

        for col in ["RelativeDistance", "Distance", "Speed"]:
            reference_telemetry[col] = reference_telemetry[col].interpolate("quadratic")

        # interpolate comparison data
        for cmp_lap in comparison_laps:
            driver_telemetry = (
                await self._pick_laps_telemetry(cmp_lap.lap_filter, cmp_lap.driver)
            )[
                [
                    "Speed",
                    "RelativeDistance",
                    "Distance",
                    "Time",
                ]
            ]

            time_based_driver_telemetry = driver_telemetry.set_index("Time")
            max_index = time_based_driver_telemetry.index.max()
            new_index = timedelta_range(timedelta(seconds=0), max_index, freq="200ms")
            time_based_driver_telemetry.reindex(new_index)

            for col in ["RelativeDistance", "Distance", "Speed", "Throttle"]:
                time_based_driver_telemetry[col] = time_based_driver_telemetry[
                    col
                ].interpolate("quadratic")

            time_based_driver_telemetry["nGear"] = time_based_driver_telemetry[
                "nGear"
            ].interpolate("nearest")
            time_based_driver_telemetry["Gap"] = (
                reference_telemetry["Distance"]
                - time_based_driver_telemetry["Distance"]
            ) * time_based_driver_telemetry["Speed"].rolling(2).mean()

            response.append(
                {
                    "driver": cmp_lap.driver,
                    "color": get_driver_color(
                        cmp_lap.driver, self._session_loader.session
                    ),
                    .reset_index()
                    .to_dict(orient="list", index=True),
                }
            )

        return response

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
