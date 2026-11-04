from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Appointment, Doctor, Patient, Procedure


class StatsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count(self, model, *where) -> int:
        return self.session.scalar(select(func.count()).select_from(model).where(*where)) or 0

    def summary(self, now: datetime) -> dict[str, int]:
        return {
            "patients": self.count(Patient),
            "doctors": self.count(Doctor, Doctor.active.is_(True)),
            "procedures": self.count(Procedure),
            "upcoming": self.count(
                Appointment, Appointment.status == "booked", Appointment.starts_at >= now
            ),
            "cancelled": self.count(Appointment, Appointment.status == "cancelled"),
        }
