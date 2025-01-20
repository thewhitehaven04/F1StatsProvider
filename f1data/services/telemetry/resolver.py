from datetime import timedelta

from core.models.queries import SessionIdentifier, TelemetryRequest
from services.laps.loader import SessionLoader
from pandas import DataFrame, timedelta_range, concat
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
        reference_telemetry: DataFrame = (
            telemetry.pick_driver(reference_lap["Driver"].iloc[0])
            .pick_laps(reference_lap["LapNumber"].iloc[0])
            .get_telemetry()
        )
        reference_telemetry.set_index("Time", inplace=True)
        max_index = reference_telemetry.index.max()
        sampling_rate = "125ms"
        reindexed_reference_telemetry = reference_telemetry.reindex(
            timedelta_range(
                start=timedelta(seconds=0), end=max_index, freq=sampling_rate
            )
        )

        interpolate_cols = ["Distance", "Speed"]
        reindexed_reference_telemetry[interpolate_cols] = (
            reference_telemetry.resample(sampling_rate)["Distance", "Speed"]
            .mean()
            .bfill()
        )

        # interpolate comparison data
        for cmp_lap in comparison_laps.iterrows():
            driver_telemetry = (
                await self._pick_laps_telemetry(
                    cmp_lap[1]["LapNumber"], cmp_lap[1]["Driver"]
                )
            )[
                [
                    "Speed",
                    "Distance",
                    "Time",
                ]
            ]

            driver_telemetry.set_index("Time", inplace=True)
            max_index = driver_telemetry.index.max()
            reindexed_driver_telemetry = driver_telemetry.reindex(
                timedelta_range(
                    start=timedelta(seconds=0), end=max_index, freq=sampling_rate
                )
            )

            reindexed_driver_telemetry[["Distance", "Speed"]] = (
                driver_telemetry.resample(sampling_rate)["Distance", "Speed"]
                .mean()
                .bfill()
            )

            reindexed_driver_telemetry["Gap"] = (
                reindexed_reference_telemetry["Distance"]
                .sub(reindexed_driver_telemetry["Distance"])
                .div(reindexed_driver_telemetry["Speed"] / 3600 * 1000)
            )

            driver = cmp_lap[1]["Driver"]
            response.append(
                {
                    "driver": driver,
                    "color": get_driver_color(driver, self._session_loader.session),
                    "gap_to": reference_lap["Driver"].iloc[0],
                    "telemetry": reindexed_driver_telemetry.reset_index().to_dict(
                        orient="list"
                    ),
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
