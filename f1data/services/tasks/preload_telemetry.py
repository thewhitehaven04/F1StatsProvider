from core.models.queries import SessionIdentifier
from services.session.session import get_loader


def preload_telemetry(year: str, round: str, session: SessionIdentifier | int, is_testing: bool):
    loader = get_loader(year, int(round), session, is_testing)
    loader.fetch_lap_telemetry()