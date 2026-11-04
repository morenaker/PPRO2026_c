from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Doctor


class DoctorRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_with_hours(self) -> list[Doctor]:
        stmt = select(Doctor).options(selectinload(Doctor.office_hours)).order_by(Doctor.full_name)
        return list(self.session.scalars(stmt))
