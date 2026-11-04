from fastapi import Depends, HTTPException, Request

from app.services.auth import ROLE_ADMIN


class LoginRequired(Exception):
    """Nepřihlášený uživatel – main.py z toho udělá přesměrování na přihlášení."""


def current_user(request: Request) -> dict:
    user = request.session.get("user")
    if not user:
        raise LoginRequired()
    return user


def require_admin(user: dict = Depends(current_user)) -> dict:
    if user["role"] != ROLE_ADMIN:
        raise HTTPException(status_code=403, detail="Tato sekce je jen pro správce.")
    return user


def flash(request: Request, message: str, kind: str = "success") -> None:
    """Jednorázová zpráva zobrazená na další stránce (kind: success | error)."""
    request.session.setdefault("flash", []).append({"text": message, "kind": kind})
