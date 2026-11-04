import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.doctor import Doctor
from app.models.patient import Patient


class AppointmentStatus(enum.StrEnum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Appointment(Base):
    """Rezervace termínu u lékaře.

    Překryv termínů u stejného lékaře hlídá databáze (exclusion constraint),
    ne jen aplikace – klient trvá na tom, že to nesmí jít ani omylem.
    Zrušená rezervace zůstává v tabulce (status=cancelled) kvůli statistice.
    """

    __tablename__ = "appointment"
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="time_order"),
        CheckConstraint("status IN ('booked', 'cancelled', 'completed')", name="status_values"),
        ExcludeConstraint(
            ("doctor_id", "="),
            (func.tstzrange(text("starts_at"), text("ends_at"), "[)"), "&&"),
            where=text("status <> 'cancelled'"),
            using="gist",
            name="no_overlap_per_doctor",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.id", ondelete="RESTRICT"), index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.id", ondelete="RESTRICT"), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reason: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(20), default=AppointmentStatus.BOOKED.value)
    # Kdo rezervaci založil. Dnes jen recepce; sloupec drží otevřenou cestu k online objednávání.
    created_via: Mapped[str] = mapped_column(String(20), default="reception")
    is_demo: Mapped[bool] = mapped_column(default=False, server_default="false")
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancel_reason: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    patient: Mapped[Patient] = relationship()
    doctor: Mapped[Doctor] = relationship()
