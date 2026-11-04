from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session
from app.services.auth import DEMO_ACCOUNTS, AuthService
from app.web.templating import templates

router = APIRouter()


def _demo_accounts() -> list[dict]:
    return [
        {"username": u, "name": n, "role": r, "password": getattr(settings, attr)}
        for u, n, r, attr in DEMO_ACCOUNTS
    ]


@router.get("/prihlaseni")
def login_form(request: Request):
    if request.session.get("user"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request, "auth/login.html", {"error": None, "accounts": _demo_accounts(), "username": ""}
    )


@router.post("/prihlaseni")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    user = AuthService(session).authenticate(username, password)
    if user is None:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"error": "Nesprávné jméno nebo heslo.", "accounts": _demo_accounts(), "username": username},
            status_code=401,
        )
    request.session.clear()
    request.session["user"] = {
        "id": user.id,
        "username": user.username,
        "name": user.display_name,
        "role": user.role,
    }
    return RedirectResponse("/", status_code=303)


@router.post("/odhlasit")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/prihlaseni", status_code=303)
