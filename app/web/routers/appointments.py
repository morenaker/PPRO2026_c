from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_session
from app.services.overview import OverviewService
from app.web.deps import current_user
from app.web.templating import templates

router = APIRouter(prefix="/rezervace", dependencies=[Depends(current_user)])


@router.get("")
def list_appointments(request: Request, doctor_id: int | None = None, session: Session = Depends(get_session)):
    overview = OverviewService(session)
    return templates.TemplateResponse(
        request,
        "appointments/list.html",
        {
            "active": "appointments",
            "appointments": overview.upcoming_appointments(doctor_id),
            "doctors": overview.doctors_with_hours(),
            "doctor_id": doctor_id,
        },
    )
