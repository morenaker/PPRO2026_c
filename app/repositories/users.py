from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AppUser


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_username(self, username: str) -> AppUser | None:
        return self.session.scalar(select(AppUser).where(AppUser.username == username))

    def add(self, user: AppUser) -> AppUser:
        self.session.add(user)
        self.session.flush()
        return user
