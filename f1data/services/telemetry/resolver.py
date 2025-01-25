from typing import Sequence
from core.models.queries import TelemetryRequest
from services.session.session import SessionLoader
from pandas import concat
from fastf1.plotting import get_driver_color
from fastf1.core import Telemetry, Laps


def _pick_laps_telemetry(
    laps: Laps, lap_filter: Sequence[int] | int | str, driver: str
) -> Telemetry:
    lap_filter = int(lap_filter) if isinstance(lap_filter, str) else lap_filter
    return laps.pick_driver(driver).pick_laps(lap_filter).get_telemetry()


async def get_interpolated_telemetry_comparison(
    session_loader: SessionLoader,
    comparison: list[TelemetryRequest],
):
    laps = await session_loader.lap_telemetry
    telemetries = []
    concat_laps = concat(
        [laps.pick_drivers(req.driver).pick_laps(req.lap_filter) for req in comparison]
    )
    reference_laptime = concat_laps["LapTime"].min()

    reference_lap = concat_laps.loc[concat_laps["LapTime"] == reference_laptime]
    comparison_laps = concat_laps.loc[concat_laps["LapTime"] != reference_laptime]

    # interpolate reference data
    reference_telemetry = _pick_laps_telemetry(
        laps, reference_lap["LapNumber"].iloc[0], reference_lap["Driver"].iloc[0]
    )
    sampling_rate = "100ms"
    reference_telemetry.resample_channels(rule=sampling_rate)

    # interpolate comparison data
    for cmp_lap in comparison_laps.iterrows():
        driver_telemetry = _pick_laps_telemetry(
            laps, cmp_lap[1]["LapNumber"], cmp_lap[1]["Driver"]
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
                "color": get_driver_color(driver, session_loader.session),
                "comparison": driver_telemetry.to_dict(orient="list"),
            }
        )

    return {
        "telemetries": telemetries,
        "reference": reference_lap["Driver"].iloc[0],
    }


async def get_telemetry(session_loader: SessionLoader, driver: str, lap: str):
    session = session_loader.session
    telemetry = _pick_laps_telemetry(await session_loader.lap_telemetry, lap, driver)[
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
    return {
        "driver": driver,
        "color": get_driver_color(driver, session),
        "telemetry": telemetry.rename(columns={"nGear": "Gear"}).to_dict(orient="list"),
    }
