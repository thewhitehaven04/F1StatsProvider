from dataclasses import dataclass
from models.session.Identifier import SessionIdentifier


@dataclass
class SessionQueryRequest: 
    year: int
    grand_prix: str
    session_identifier: SessionIdentifier