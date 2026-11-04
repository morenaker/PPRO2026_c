from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_session
from app.services.demo_data import DemoDataService
from app.services.errors import DomainError
from app.web.deps import flash, require_admin
from app.web.templating import templates

router = APIRouter(prefix="/nastaveni", dependencies=[Depends(require_admin)])


@router.get("")
def settings_page(request: Request, session: Session = Depends(get_session)):
    status = DemoDataService(session).status()
    return templates.TemplateResponse(request, "settings/index.html", {"active": "settings", "demo": status})


@router.post("/testovaci-data/pridat")
def add_demo_data(request: Request, session: Session = Depends(get_session)):
    try:
        st = DemoDataService(session).add()
        flash(request, f"Přidáno: {st.patients} pacientů, {st.doctors} lékařů, {st.appointments} rezervací.")
    except DomainError as exc:
        flash(request, str(exc), "error")
    return RedirectResponse("/nastaveni", status_code=303)


@router.post("/testovaci-data/odebrat")
def remove_demo_data(request: Request, session: Session = Depends(get_session)):
    DemoDataService(session).remove()
    flash(request, "Testovací data byla odebrána. Ostatní data zůstala beze změny.")
    return RedirectResponse("/nastaveni", status_code=303)
