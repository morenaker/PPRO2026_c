from sqlalchemy.orm import Session

from app.models import Patient
from app.repositories.patients import PatientRepository
from app.services.errors import DuplicatePatientError


class PatientService:
    """Obchodní pravidla kolem pacientů. Zná repozitář, nezná web."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = PatientRepository(session)

    def register(
        self,
        *,
        first_name: str,
        last_name: str,
        birth_year: int,
        phone: str,
        insurance_number: str,
        insurer: str,
    ) -> Patient:
        insurance_number = insurance_number.strip()
        existing = self.repo.get_by_insurance_number(insurance_number)
        if existing is not None:
            raise DuplicatePatientError(existing.id)
        patient = self.repo.add(
            Patient(
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                birth_year=birth_year,
                phone=phone.strip(),
                insurance_number=insurance_number,
                insurer=insurer.strip(),
            )
        )
        self.session.commit()
        return patient

    def search(self, query: str = "") -> list[Patient]:
        return self.repo.search(query)
