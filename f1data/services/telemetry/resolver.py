from typing import Sequence
from core.models.queries import SessionIdentifier, TelemetryRequest
from services.session.session import get_loader
from pandas import concat
from fastf1.plotting import get_driver_color
from fastf1.core import Telemetry, Laps


def _pick_laps_telemetry(
    laps: Laps, lap_filter: Sequence[int] | int | str, driver: str
) -> Telemetry:
    lap_filter = int(lap_filter) if isinstance(lap_filter, str) else lap_filter
    return laps.pick_driver(driver).pick_laps(lap_filter).get_telemetry()


def get_interpolated_telemetry_comparison(
    year: str,
    event: str,
    session_identifier: SessionIdentifier,
    comparison: list[TelemetryRequest],
):
    loader = get_loader(year, event, session_identifier)
    laps = loader.lap_telemetry
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
    reference_distance = reference_telemetry["Distance"].iloc[-1]
    sampling_rate = "250ms"
    reference_telemetry.resample_channels(rule=sampling_rate)

    # interpolate comparison data
    for cmp_lap in comparison_laps.iterrows():
        driver_telemetry = _pick_laps_telemetry(
            laps, cmp_lap[1]["LapNumber"], cmp_lap[1]["Driver"]
        )

        driver_telemetry.resample_channels(rule=sampling_rate)
        driver_telemetry.reindex_like(reference_telemetry)
        rolling_driver_speed_ms = (
            driver_telemetry["Speed"].rolling(window=5, center=True).mean() / 3.6
        )
        driver_telemetry["Gap"] = (
            (
                reference_telemetry["RelativeDistance"]
                - driver_telemetry["RelativeDistance"]
            )
            * reference_distance
            / (rolling_driver_speed_ms)
        )

        driver = cmp_lap[1]["Driver"]
        telemetries.append(
            {
                "driver": driver,
                "color": get_driver_color(driver, loader.session),
                "comparison": driver_telemetry.to_dict(orient="list"),
            }
        )
    return {
        "telemetries": telemetries,
        "reference": reference_lap["Driver"].iloc[0],
    }


def get_telemetry(
    year: str, event: str, session_identifier: SessionIdentifier, driver: str, lap: str
):
    loader = get_loader(year, event, session_identifier)
    telemetry = _pick_laps_telemetry(loader.lap_telemetry, lap, driver)[
        [
            "Throttle",
            "Brake",
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
        "color": get_driver_color(driver, loader.session),
        "telemetry": telemetry.rename(columns={"nGear": "Gear"}).to_dict(orient="list"),
    }


def get_telemetries(
    year: str,
    event: str,
    session_identifier: SessionIdentifier,
    queries: list[TelemetryRequest],
):
    telemetries = []
    for query in queries:
        for lap in query.lap_filter:
            telemetries.append(
                get_telemetry(year, event, session_identifier, query.driver, str(lap))
            )

    return telemetries
