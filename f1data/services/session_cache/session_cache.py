from typing import MutableMapping
from services.session_cache.key import SessionCacheKey
from fastf1.core import Session


# this is a cache mock
class SessionCache:

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self) -> None:
        self._cache: MutableMapping[SessionCacheKey, Session] = {}

    def get(self, key: SessionCacheKey):
        return self._cache.get(key)

    def store(self, key: SessionCacheKey, session: Session):
        self._cache[key] = session
