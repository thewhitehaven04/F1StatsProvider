from core.models.queries import SessionIdentifier
from services.session.session import get_loader


def preload_telemetry(year: str, round: str, session: SessionIdentifier):
    loader = get_loader(year, int(round), session)
    loader.fetch_lap_telemetry()