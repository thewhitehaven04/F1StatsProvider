from core.models.queries import SessionIdentifier
from services.session.session import get_loader


async def preload_telemetry(year: str, round: str, session: SessionIdentifier):
    loader = get_loader(year, int(round), session)
    await loader.fetch_lap_telemetry()