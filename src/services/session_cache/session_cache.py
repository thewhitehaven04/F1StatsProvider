from typing import MutableMapping
from services.session_cache.key import SessionCacheKey
from fastf1.core import Session


class SessionCache:

    def __new__(cls):
        if not hasattr(cls, '_instance'): 
           cls._instance = super().__new__(cls)  

        return cls._instance

    def __init__(self) -> None:
        self._cache: MutableMapping[SessionCacheKey, Session] = {}

    def get(self, key):
        return self._cache.get(key)

    def store(self, key, session):
        self._cache[key] = session
