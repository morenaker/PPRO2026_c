from sqlalchemy.orm import Session

from app.repositories.health import HealthRepository


class HealthService:
    def __init__(self, session: Session) -> None:
        self.repo = HealthRepository(session)

    def check(self) -> dict[str, str]:
        self.repo.ping()
        return {"status": "ok"}
