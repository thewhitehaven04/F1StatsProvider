from core.models.queries import SessionIdentifier
from services.session.registry import get_loader


async def preload_telemetry(year: str, round: str, session: SessionIdentifier | int, is_testing: bool):
    loader = get_loader(year, int(round), session, is_testing)
    await loader.lap_telemetry