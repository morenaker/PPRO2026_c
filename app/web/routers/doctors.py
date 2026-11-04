from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_session
from app.services.overview import OverviewService
from app.web.deps import current_user
from app.web.templating import templates

router = APIRouter(prefix="/lekari", dependencies=[Depends(current_user)])


@router.get("")
def list_doctors(request: Request, session: Session = Depends(get_session)):
    doctors = OverviewService(session).doctors_with_hours()
    return templates.TemplateResponse(request, "doctors/list.html", {"active": "doctors", "doctors": doctors})
