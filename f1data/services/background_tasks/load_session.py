from core.models.queries import SessionIdentifier
from services.session.session import SessionLoader

def load_session(year: str, event: str, session_identifier: SessionIdentifier):
    loader = SessionLoader(
        year=year, event=event, session_identifier=session_identifier
    )
    loader.load_all()
