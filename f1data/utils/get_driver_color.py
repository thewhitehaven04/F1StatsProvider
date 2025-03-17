from typing import TypedDict
from fastf1.plotting import get_driver_style as ff1_get_driver_style
from fastf1.core import Session

DriverStyle = TypedDict("DriverStyle", {"IsDashed": bool, "Color": str})

STYLE_PRESET = [
    {"color": "auto", "linestyle": "solid"},
    {"color": "auto", "linestyle": "dashed"},
]


def get_driver_style(driver: str, session: Session) -> DriverStyle:
    style = ff1_get_driver_style(driver, STYLE_PRESET, session)
    return {"Color": style["color"], "IsDashed": style["linestyle"] == "dashed"}