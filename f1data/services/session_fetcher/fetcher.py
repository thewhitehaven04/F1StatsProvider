from fastapi import Depends
from models.session.Identifier import SessionIdentifier
from services.session_cache.key import SessionCacheKey
from services.session_cache.session_cache import SessionCache
from fastf1 import get_session
from fastf1.core import Session

class SessionFetcher:

    def __init__(self, cache: SessionCache = Depends(SessionCache)) -> None:
        self._session_cache = cache

    def load_session_data(
        self, year: int, session_identifier: SessionIdentifier, grand_prix: str
    ) -> Session:
        cache_key = SessionCacheKey(year, session_identifier, grand_prix)
        cached_session = self._session_cache.get(cache_key)

        if not cached_session:
            session = get_session(
                year=year, identifier=session_identifier, gp=grand_prix
            )
            session.load()
            self._session_cache.store(key=cache_key, session=session)

            return session 

        return cached_session 

