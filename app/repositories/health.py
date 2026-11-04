from sqlalchemy import text
from sqlalchemy.orm import Session


class HealthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def ping(self) -> None:
        """Ověří spojení s databází (vyhodí výjimku, když DB neodpovídá)."""
        self.session.execute(text("SELECT 1"))
