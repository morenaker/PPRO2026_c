"""Čtecí služby pro přehledové stránky (úvod, lékaři, diář)."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Appointment, Doctor
from app.repositories.appointments import AppointmentRepository
from app.repositories.doctors import DoctorRepository
from app.repositories.stats import StatsRepository


def local_now() -> datetime:
    return datetime.now(ZoneInfo(settings.timezone))


def start_of_today() -> datetime:
    return local_now().replace(hour=0, minute=0, second=0, microsecond=0)


class OverviewService:
    def __init__(self, session: Session) -> None:
        self.stats = StatsRepository(session)
        self.doctors = DoctorRepository(session)
        self.appointments = AppointmentRepository(session)

    def summary(self) -> dict[str, int]:
        return self.stats.summary(local_now())

    def doctors_with_hours(self) -> list[Doctor]:
        return self.doctors.list_with_hours()

    def upcoming_appointments(self, doctor_id: int | None = None) -> list[Appointment]:
        return self.appointments.list_from(start_of_today(), doctor_id)

    def todays_appointments(self) -> list[Appointment]:
        """Dnešní rezervace (včetně zrušených) pro úvodní stránku recepce."""
        start = start_of_today()
        return self.appointments.list_between(start, start + timedelta(days=1))
