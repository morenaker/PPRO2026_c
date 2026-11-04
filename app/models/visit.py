from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.appointment import Appointment


class Procedure(Base):
    """Číselník výkonů: kód, název, bodové ohodnocení."""

    __tablename__ = "procedure"
    __table_args__ = (CheckConstraint("points >= 0", name="points_non_negative"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    points: Mapped[int]
    # U některých výkonů (např. aplikace) se zapisuje počet.
    requires_quantity: Mapped[bool] = mapped_column(default=False)
    is_demo: Mapped[bool] = mapped_column(default=False, server_default="false")


class Visit(Base):
    """Záznam o návštěvě – vzniká jen k rezervaci, která proběhla (1:1)."""

    __tablename__ = "visit"

    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointment.id", ondelete="RESTRICT"), unique=True
    )
    note: Mapped[str] = mapped_column(String(1000), default="")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    appointment: Mapped[Appointment] = relationship()
    procedures: Mapped[list["VisitProcedure"]] = relationship(back_populates="visit")


class VisitProcedure(Base):
    """Vazba M:N návštěva ↔ výkon, s počtem provedení."""

    __tablename__ = "visit_procedure"
    __table_args__ = (CheckConstraint("quantity >= 1", name="quantity_positive"),)

    visit_id: Mapped[int] = mapped_column(ForeignKey("visit.id", ondelete="RESTRICT"), primary_key=True)
    procedure_id: Mapped[int] = mapped_column(
        ForeignKey("procedure.id", ondelete="RESTRICT"), primary_key=True
    )
    quantity: Mapped[int] = mapped_column(default=1)

    visit: Mapped[Visit] = relationship(back_populates="procedures")
    procedure: Mapped[Procedure] = relationship()
