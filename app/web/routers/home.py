from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_session
from app.services.health import HealthService
from app.services.overview import OverviewService
from app.web.deps import current_user
from app.web.templating import templates

router = APIRouter()


@router.get("/", dependencies=[Depends(current_user)])
def home(request: Request, session: Session = Depends(get_session)):
    overview = OverviewService(session)
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "active": "home",
            "summary": overview.summary(),
            "today": overview.todays_appointments(),
            "doctors": overview.doctors_with_hours(),
        },
    )


@router.get("/health")
def health(session: Session = Depends(get_session)):
    return HealthService(session).check()
