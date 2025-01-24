from core.models.queries import SessionIdentifier, TelemetryRequest
from services.session.session import SessionLoader
from pandas import concat
from fastf1.plotting import get_driver_color


class TelemetryResolver:
    def __init__(
        self, year: str, session_identifier: SessionIdentifier, grand_prix: str
    ) -> None:
        self._session_loader = SessionLoader(year, session_identifier, grand_prix)

    async def _pick_laps_telemetry(self, laps: list[int], driver: str):
        return (
            (await self._session_loader.telemetry)
            .pick_driver(driver)
            .pick_laps(laps)
            .get_telemetry()
        )

    async def _pick_lap_telemetry(self, lap: str, driver: str):
        return (
            (await self._session_loader.telemetry)
            .pick_driver(driver)
            .pick_lap(int(lap))
            .get_telemetry()
        )

    async def get_interpolated_telemetry_comparison(
        self, comparison: list[TelemetryRequest]
    ):
        telemetries = []
        telemetry = await self._session_loader.telemetry
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
        reference_telemetry = (
            telemetry.pick_driver(reference_lap["Driver"].iloc[0])
            .pick_laps(reference_lap["LapNumber"].iloc[0])
            .get_telemetry()
        )
        sampling_rate = "100ms"
        reference_telemetry.resample_channels(rule=sampling_rate)

        # interpolate comparison data
        for cmp_lap in comparison_laps.iterrows():
            driver_telemetry = await self._pick_laps_telemetry(
                cmp_lap[1]["LapNumber"], cmp_lap[1]["Driver"]
            )

            driver_telemetry.resample_channels(rule=sampling_rate)

            driver_speed_ms = driver_telemetry["Speed"] * 1000 / 3600
            driver_telemetry["Gap"] = (
                reference_telemetry["Distance"] - driver_telemetry["Distance"]
            ) / (driver_speed_ms)

            driver = cmp_lap[1]["Driver"]
            telemetries.append(
                {
                    "driver": driver,
                    "color": get_driver_color(driver, self._session_loader.session),
                    "comparison": driver_telemetry.to_dict(orient="list"),
                }
            )

        return {
            "telemetries": telemetries,
            "reference": reference_lap["Driver"].iloc[0],
        }

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
