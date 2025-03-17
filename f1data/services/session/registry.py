from collections import namedtuple
from threading import Lock

from core.models.queries import SessionIdentifier
from services.session.session import SessionLoader

RegistryKey = namedtuple(
    "registry_key", ["year", "round", "session_identifier", "is_testing"]
)

session_registry: dict[RegistryKey, SessionLoader] = {}

lock = Lock()


def get_loader(
    year: str,
    round: int,
    session_identifier: SessionIdentifier | int,
    is_testing: bool = False,
) -> SessionLoader:
    with lock:
        key = RegistryKey(year, round, session_identifier, is_testing)
        if session_registry.get(key) is not None:
            return session_registry[key]

        loader = SessionLoader(year, round, session_identifier, is_testing)
        session_registry[key] = loader
        return loader
