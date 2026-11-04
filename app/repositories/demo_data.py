"""Dotazy nad ukázkovými (is_demo) řádky: počty a hromadné odebrání."""
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from app.models import Appointment, Doctor, OfficeHours, Patient, Procedure, Visit, VisitProcedure


class DemoDataRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_demo(self, model) -> int:
        return self.session.scalar(select(func.count()).select_from(model).where(model.is_demo.is_(True))) or 0

    def add_all(self, objects: list) -> None:
        self.session.add_all(objects)
        self.session.flush()

    def add(self, obj) -> None:
        self.session.add(obj)

    def flush(self) -> None:
        self.session.flush()

    def delete_all_demo(self) -> None:
        """Smaže ukázkové řádky a vše, co se jich dotýká, ve správném pořadí kvůli FK RESTRICT."""
        demo_patients = select(Patient.id).where(Patient.is_demo.is_(True))
        demo_doctors = select(Doctor.id).where(Doctor.is_demo.is_(True))
        appts = select(Appointment.id).where(
            or_(
                Appointment.is_demo.is_(True),
                Appointment.patient_id.in_(demo_patients),
                Appointment.doctor_id.in_(demo_doctors),
            )
        )
        visits = select(Visit.id).where(Visit.appointment_id.in_(appts))
        demo_procedures = select(Procedure.id).where(Procedure.is_demo.is_(True))

        s = self.session
        s.execute(
            delete(VisitProcedure).where(
                or_(VisitProcedure.visit_id.in_(visits), VisitProcedure.procedure_id.in_(demo_procedures))
            )
        )
        s.execute(delete(Visit).where(Visit.appointment_id.in_(appts)))
        s.execute(delete(Appointment).where(Appointment.id.in_(appts)))
        s.execute(delete(OfficeHours).where(OfficeHours.doctor_id.in_(demo_doctors)))
        s.execute(delete(Patient).where(Patient.is_demo.is_(True)))
        s.execute(delete(Doctor).where(Doctor.is_demo.is_(True)))
        s.execute(delete(Procedure).where(Procedure.is_demo.is_(True)))
