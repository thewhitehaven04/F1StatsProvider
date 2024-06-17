
from typing import NamedTuple
from models.session.Identifier import SessionIdentifier

SessionCacheKey = NamedTuple(
    'SessionCacheKey',
    year=int,
    grand_prix=str, 
    identifier=SessionIdentifier
)