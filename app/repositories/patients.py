from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Patient


class PatientRepository:
    """Jediné místo, které o pacientech mluví s databází. Žádná obchodní pravidla."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, patient: Patient) -> Patient:
        self.session.add(patient)
        self.session.flush()
        return patient

    def get_by_insurance_number(self, insurance_number: str) -> Patient | None:
        return self.session.scalar(
            select(Patient).where(Patient.insurance_number == insurance_number)
        )

    def search(self, query: str = "", limit: int = 50) -> list[Patient]:
        """Hledání podle příjmení nebo telefonu (pacient při telefonátu řekne obojí)."""
        stmt = select(Patient).order_by(Patient.last_name, Patient.first_name).limit(limit)
        query = query.strip()
        if query:
            like = f"%{query}%"
            stmt = stmt.where(or_(Patient.last_name.ilike(like), Patient.phone.like(like)))
        return list(self.session.scalars(stmt))
