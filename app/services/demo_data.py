"""Ukázková (syntetická) data na jedno kliknutí – přidat i kompletně odebrat.

Vše, co tu vznikne, má `is_demo = true`. Odebrání maže jen tyto řádky (a vše, co se jich dotýká,
např. rezervaci reálného pacienta u ukázkového lékaře), reálná data zůstávají.
"""
import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Appointment, Doctor, OfficeHours, Patient, Procedure, Visit, VisitProcedure
from app.repositories.demo_data import DemoDataRepository
from app.services.errors import DomainError

PROCEDURES = [
    ("D-01", "Vstupní vyšetření", 100, False),
    ("D-02", "Kontrolní vyšetření", 60, False),
    ("D-03", "Aplikace injekce", 25, True),
    ("D-04", "Odběr krve", 30, False),
    ("D-05", "EKG", 90, False),
    ("D-06", "Očkování", 45, True),
    ("D-07", "Preventivní prohlídka", 150, False),
    ("D-08", "Ošetření rány", 55, True),
    ("D-09", "Měření tlaku", 10, False),
    ("D-10", "Vystavení potvrzení", 20, False),
]

# (jméno, [(den v týdnu 0=po, od hodin, do hodin, místo, lze objednávat)])
MAIN = "Ordinace Na Vyhlídce"
DOCTORS = [
    ("MUDr. Alena Vzorová", [(0, 8, 12, MAIN, True), (2, 8, 12, MAIN, True), (4, 8, 12, MAIN, True)]),
    ("MUDr. Karel Ukázka", [(d, 13, 17, MAIN, True) for d in range(0, 4)]),
    (
        "MUDr. Hana Příkladová",
        [(1, 8, 12, MAIN, True), (1, 13, 17, "Pobočka Horní 5", False), (3, 8, 12, MAIN, True)],
    ),
]

FIRST = ["Jan", "Petr", "Tomáš", "Lukáš", "Martin", "Jana", "Eva", "Anna", "Marie", "Lenka", "Kateřina", "Hana"]
LAST = ["Novák", "Svoboda", "Dvořák", "Černý", "Procházka", "Kučera", "Veselý", "Horák", "Němec", "Marek", "Pospíšil", "Král"]
INSURERS = ["111", "201", "205", "207", "211"]
REASONS = ["Kontrola", "Bolest zad", "Recept", "Očkování", "Preventivní prohlídka", "Kašel", "Odběr krve", "Potvrzení"]


@dataclass
class DemoStatus:
    patients: int
    doctors: int
    procedures: int
    appointments: int

    @property
    def present(self) -> bool:
        return bool(self.patients or self.doctors or self.procedures or self.appointments)


class DemoDataService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = DemoDataRepository(session)

    def _count(self, model) -> int:
        return self.repo.count_demo(model)

    def status(self) -> DemoStatus:
        return DemoStatus(
            patients=self._count(Patient),
            doctors=self._count(Doctor),
            procedures=self._count(Procedure),
            appointments=self._count(Appointment),
        )

    def add(self) -> DemoStatus:
        if self.status().present:
            raise DomainError("Testovací data už jsou přidána. Nejdřív je odeberte.")
        rng = random.Random(2026)
        tz = ZoneInfo(settings.timezone)
        now = datetime.now(tz)

        procedures = [
            Procedure(code=c, name=n, points=p, requires_quantity=q, is_demo=True) for c, n, p, q in PROCEDURES
        ]
        patients = [
            Patient(
                first_name=rng.choice(FIRST),
                last_name=rng.choice(LAST),
                birth_year=rng.randint(1940, 2015),
                phone=f"+420 777 000 {i:03d}",
                insurance_number=f"DEMO{i:06d}",
                insurer=rng.choice(INSURERS),
                is_demo=True,
            )
            for i in range(1, 31)
        ]
        doctors = []
        for name, hours in DOCTORS:
            doctor = Doctor(full_name=name, is_demo=True)
            doctor.office_hours = [
                OfficeHours(weekday=d, start_time=time(a), end_time=time(b), location=loc, bookable=ok)
                for d, a, b, loc, ok in hours
            ]
            doctors.append(doctor)
        self.repo.add_all(procedures + patients + doctors)

        # Dva pacienti ruší pořád (kvůli ukázce statistiky rušících).
        serial_cancellers = patients[:2]
        today = date.today()
        for doctor in doctors:
            for offset in range(-14, 8):
                day = today + timedelta(days=offset)
                for oh in doctor.office_hours:
                    if oh.weekday != day.weekday() or not oh.bookable:
                        continue
                    slot = datetime.combine(day, oh.start_time, tzinfo=tz)
                    end = datetime.combine(day, oh.end_time, tzinfo=tz)
                    while slot + timedelta(minutes=settings.default_appointment_minutes) <= end:
                        if rng.random() < 0.3:
                            self._add_appointment(rng, doctor, patients, serial_cancellers, procedures, slot, now)
                        slot += timedelta(minutes=settings.default_appointment_minutes)
        self.session.commit()
        return self.status()

    def _add_appointment(self, rng, doctor, patients, cancellers, procedures, start, now) -> None:
        cancelled = rng.random() < 0.12
        patient = rng.choice(cancellers if cancelled else patients)
        status = "cancelled" if cancelled else ("completed" if start < now else "booked")
        appt = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            starts_at=start,
            ends_at=start + timedelta(minutes=settings.default_appointment_minutes),
            reason=rng.choice(REASONS),
            status=status,
            is_demo=True,
            cancelled_at=start - timedelta(days=1) if cancelled else None,
            cancel_reason="Pacient se omluvil" if cancelled else None,
        )
        self.repo.add(appt)
        if status == "completed":
            self.repo.flush()
            visit = Visit(appointment_id=appt.id, note="Ukázkový záznam")
            self.repo.add(visit)
            self.repo.flush()
            for proc in rng.sample(procedures, rng.randint(1, 3)):
                qty = rng.randint(1, 3) if proc.requires_quantity else 1
                self.repo.add(VisitProcedure(visit_id=visit.id, procedure_id=proc.id, quantity=qty))

    def remove(self) -> DemoStatus:
        self.repo.delete_all_demo()
        self.session.commit()
        return self.status()
