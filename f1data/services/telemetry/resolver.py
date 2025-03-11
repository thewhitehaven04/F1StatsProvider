from typing import Sequence

from numpy import concatenate, interp
from core.models.queries import SessionIdentifier, TelemetryRequest
from services.session.session import get_loader
from pandas import concat
from fastf1.plotting import get_driver_color
from fastf1.core import Telemetry, Laps


def _pick_laps_telemetry(
    laps: Laps, lap_filter: Sequence[int] | int | str, driver: str
) -> Telemetry:
    lap_filter = int(lap_filter) if isinstance(lap_filter, str) else lap_filter
    return laps.pick_drivers(driver).pick_laps(lap_filter).get_telemetry()


async def get_interpolated_telemetry_comparison(
    year: str,
    round_number: int,
    session_identifier: SessionIdentifier | int,
    comparison: list[TelemetryRequest],
    is_testing: bool,
):
    loader = get_loader(year, round_number, session_identifier, is_testing)
    laps = await loader.lap_telemetry
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
    reference_distance = reference_telemetry["Distance"].iat[-1]

    def interpolate_bounds(channel):
        channel_start = channel[1] - channel[0]
        channel_end = channel[-1] - channel[-2]
        return concatenate(
            [[channel[0] - channel_start], channel, [channel[-1] + channel_end]]
        )

    # interpolate comparison data
    for cmp_lap in comparison_laps.iterrows():
        driver_telemetry = _pick_laps_telemetry(
            laps, cmp_lap[1]["LapNumber"], cmp_lap[1]["Driver"]
        )
        q = driver_telemetry["Distance"].iat[-1] / reference_distance
        lattice_distance = (
            interpolate_bounds(driver_telemetry["Distance"].to_numpy()) * q
        )
        lattice_time = interpolate_bounds(
            driver_telemetry["Time"].dt.total_seconds().to_numpy()
        )
        laptime_seq = interp(
            reference_telemetry["Distance"], lattice_distance, lattice_time
        )
        delta = laptime_seq - reference_telemetry["Time"].dt.total_seconds()
        driver = cmp_lap[1]["Driver"]
        telemetries.append(
            {
                "driver": driver,
                "color": get_driver_color(driver, loader._session),
                "comparison": {"Gap": delta.tolist(), "Distance": lattice_distance.tolist()},
            }
        )
    return {
        "telemetries": telemetries,
        "reference": reference_lap["Driver"].iloc[0],
    }


async def get_telemetry(
    year: str,
    round_number: int,
    session_identifier: SessionIdentifier | int,
    driver: str,
    lap: str,
    is_testing: bool,
):
    loader = get_loader(
        year=year,
        round=round_number,
        session_identifier=session_identifier,
        is_testing=is_testing,
    )
    telemetry = _pick_laps_telemetry(await loader.lap_telemetry, lap, driver)[
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
        "color": get_driver_color(driver, loader._session),
        "telemetry": telemetry.rename(columns={"nGear": "Gear"}).to_dict(orient="list"),
    }


async def get_telemetries(
    year: str,
    round_number: int,
    session_identifier: SessionIdentifier | int,
    is_testing: bool,
    queries: list[TelemetryRequest],
):
    telemetries = []
    for query in queries:
        for lap in query.lap_filter:
            telemetries.append(
                await get_telemetry(
                    year,
                    round_number,
                    session_identifier,
                    query.driver,
                    str(lap),
                    is_testing=is_testing,
                )
            )

    return telemetries
