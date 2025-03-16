from math import pi
from typing import Sequence 

from numpy import (
    concatenate,
    cos,
    interp,
    array,
    matmul,
    sin,
    min as np_min,
    max as np_max,
    stack,
)
from core.models.queries import SessionIdentifier, TelemetryRequest
from services.session.session import SessionLoader, get_loader
from pandas import DataFrame, Series, concat
from fastf1.core import Telemetry, Laps

from utils.get_driver_color import get_driver_style


def _pick_laps_telemetry(
    laps: Laps, lap_filter: Sequence[int] | int | str, driver: str
) -> Telemetry:
    lap_filter = int(lap_filter) if isinstance(lap_filter, str) else lap_filter
    return laps.pick_drivers(driver).pick_laps(lap_filter).get_telemetry()


async def generate_circuit_data(
    loader: SessionLoader,
    reference_telemetry: Telemetry,
    reference_driver: str,
    laps: Laps,
    comparison_laps: Sequence[DataFrame],
):
    circuit_data = await loader.circuit_info
    rotation_rad = circuit_data.rotation / 180 * pi
    rotated_coordinates = matmul(
        reference_telemetry.loc[:, ("X", "Y")].to_numpy(),
        array(
            [
                [cos(rotation_rad), sin(rotation_rad)],
                [-sin(rotation_rad), cos(rotation_rad)],
            ]
        ),
    )

    reference_telemetry["X"] = rotated_coordinates[:, 0] - np_min(
        rotated_coordinates[:, 0]
    )
    reference_telemetry["Y"] = rotated_coordinates[:, 1] - np_min(
        rotated_coordinates[:, 1]
    )

    driver_speed_interp_data = []

    for cmp_lap in comparison_laps.iterrows():
        comp = _pick_laps_telemetry(laps, cmp_lap[1]["LapNumber"], cmp_lap[1]["Driver"])
        driver_speed_interp_data.append(
            {
                "speed": interp(
                    x=reference_telemetry["RelativeDistance"],
                    xp=comp["RelativeDistance"],
                    fp=comp["Speed"],
                ),
                "driver": cmp_lap[1]["Driver"],
            }
        )

    driver_speed_interp_data.append(
        {
            "driver": reference_driver,
            "speed": reference_telemetry["Speed"].to_numpy(),
        }
    )
    fastest_driver_series = []

    for i in range(len(driver_speed_interp_data[0]["speed"])):
        speeds = stack([item["speed"] for item in driver_speed_interp_data], axis=-1)
        for driver_speeds in speeds:
            max_speed = np_max(driver_speeds)
            for data in driver_speed_interp_data:
                if data["speed"][i] == max_speed:
                    fastest_driver_series.append(data["driver"])
                    break

    reference_telemetry["FastestDriver"] = Series(fastest_driver_series)

    reference_telemetry[["AlternativeStyle", "Color"]] = reference_telemetry[
        "FastestDriver"
    ].transform(
        {
            "AlternativeStyle": lambda drv: get_driver_style(drv, loader._session)["IsDashed"],
            "Color": lambda drv: get_driver_style(drv, loader._session)["Color"],
        }
    )
    return {
        "position_data": reference_telemetry[
            [
                "Distance",
                "RelativeDistance",
                "X",
                "Y",
                "FastestDriver",
                "Color",
                "AlternativeStyle",
            ]
        ].to_dict(orient="records"),
        "rotation": circuit_data.rotation,
    }


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
    driver_name = reference_lap["Driver"].iloc[0]
    reference_telemetry = _pick_laps_telemetry(
        laps, reference_lap["LapNumber"].iloc[0], driver_name
    )
    circuit_data = await generate_circuit_data(
        loader, reference_telemetry, driver_name, laps, comparison_laps
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
        driver_style = get_driver_style(driver, loader._session)
        telemetries.append(
            {
                "driver": driver,
                "color": driver_style["Color"],
                "alternative_style": driver_style["IsDashed"],
                "comparison": {
                    "gap": delta.tolist(),
                    "distance": lattice_distance.tolist(),
                },
            }
        )
    return {
        "telemetries": telemetries,
        "reference": reference_lap["Driver"].iloc[0],
        "circuit_data": circuit_data,
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
    driver_style = get_driver_style(driver, loader._session)
    return {
        "driver": driver,
        "color": driver_style["Color"],
        "alternative_style": driver_style["IsDashed"],
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
