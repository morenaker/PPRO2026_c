from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

ROLE_ADMIN = "admin"
ROLE_RECEPTION = "reception"


class AppUser(Base):
    """Uživatel aplikace. Zatím jen ukázkové účty; heslo se ukládá jen jako hash."""

    __tablename__ = "app_user"
    __table_args__ = (CheckConstraint("role IN ('admin', 'reception')", name="role_values"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    display_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(200))
