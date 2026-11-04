from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Appointment


class AppointmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_from(
        self, since: datetime, doctor_id: int | None = None, limit: int = 100
    ) -> list[Appointment]:
        stmt = (
            select(Appointment)
            .options(joinedload(Appointment.patient), joinedload(Appointment.doctor))
            .where(Appointment.starts_at >= since)
            .order_by(Appointment.starts_at)
            .limit(limit)
        )
        if doctor_id:
            stmt = stmt.where(Appointment.doctor_id == doctor_id)
        return list(self.session.scalars(stmt))

    def list_between(self, since: datetime, until: datetime) -> list[Appointment]:
        stmt = (
            select(Appointment)
            .options(joinedload(Appointment.patient), joinedload(Appointment.doctor))
            .where(Appointment.starts_at >= since, Appointment.starts_at < until)
            .order_by(Appointment.starts_at)
        )
        return list(self.session.scalars(stmt))
