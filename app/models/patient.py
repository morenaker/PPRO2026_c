from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Patient(Base):
    """Pacient. Nikdy se nemaže (historie musí být doložitelná)."""

    __tablename__ = "patient"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100), index=True)
    birth_year: Mapped[int]
    phone: Mapped[str] = mapped_column(String(30), index=True)
    # Identifikátor pojištěnce určuje pacienta jednoznačně (README, rozhodnutí D4).
    insurance_number: Mapped[str] = mapped_column(String(20), unique=True)
    insurer: Mapped[str] = mapped_column(String(100))
    is_demo: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
