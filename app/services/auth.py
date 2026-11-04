"""Přihlašování. Zatím jen ukázkové účty (README D12); hesla jsou uložena jen jako PBKDF2 hash."""
import hashlib
import hmac
import secrets

from sqlalchemy.orm import Session

from app.config import settings
from app.models import AppUser
from app.models.user import ROLE_ADMIN, ROLE_RECEPTION
from app.repositories.users import UserRepository

_ITERATIONS = 200_000

# (uživatelské jméno, zobrazované jméno, role, název položky v settings s heslem)
DEMO_ACCOUNTS = [
    ("recepce", "Věra (recepce)", ROLE_RECEPTION, "demo_reception_password"),
    ("admin", "Správce", ROLE_ADMIN, "demo_admin_password"),
]


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITERATIONS).hex()
    return f"pbkdf2_sha256${_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iterations, salt, digest = stored.split("$")
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations)).hex()
    except ValueError:
        return False
    return hmac.compare_digest(candidate, digest)


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = UserRepository(session)

    def ensure_demo_users(self) -> None:
        """Idempotentně založí ukázkové účty (voláno při startu aplikace)."""
        for username, display_name, role, password_attr in DEMO_ACCOUNTS:
            if self.repo.get_by_username(username) is None:
                self.repo.add(
                    AppUser(
                        username=username,
                        display_name=display_name,
                        role=role,
                        password_hash=hash_password(getattr(settings, password_attr)),
                    )
                )
        self.session.commit()

    def authenticate(self, username: str, password: str) -> AppUser | None:
        user = self.repo.get_by_username(username.strip().lower())
        # Hash se počítá i pro neexistujícího uživatele, aby odpověď nešlo rozlišit podle času.
        stored = user.password_hash if user else hash_password("x")
        ok = verify_password(password, stored)
        return user if (user and ok) else None
