from datetime import time

from sqlalchemy import CheckConstraint, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Doctor(Base):
    __tablename__ = "doctor"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150))
    active: Mapped[bool] = mapped_column(default=True)
    is_demo: Mapped[bool] = mapped_column(default=False, server_default="false")

    office_hours: Mapped[list["OfficeHours"]] = relationship(back_populates="doctor")


class OfficeHours(Base):
    """Ordinační hodiny lékaře v konkrétní den v týdnu (0 = pondělí)."""

    __tablename__ = "office_hours"
    __table_args__ = (
        CheckConstraint("weekday BETWEEN 0 AND 6", name="weekday_range"),
        CheckConstraint("end_time > start_time", name="time_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.id"), index=True)
    weekday: Mapped[int]
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    location: Mapped[str] = mapped_column(String(200), default="Ordinace Na Vyhlídce")
    # False = ordinace na jiné adrese, kde se objednávat nedá.
    bookable: Mapped[bool] = mapped_column(default=True)

    doctor: Mapped[Doctor] = relationship(back_populates="office_hours")
