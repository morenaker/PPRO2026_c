from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_session
from app.services.errors import DuplicatePatientError
from app.services.patients import PatientService
from app.web.deps import current_user, flash
from app.web.templating import templates

router = APIRouter(prefix="/pacienti", dependencies=[Depends(current_user)])


@router.get("")
def list_patients(request: Request, q: str = "", session: Session = Depends(get_session)):
    patients = PatientService(session).search(q)
    return templates.TemplateResponse(
        request, "patients/list.html", {"active": "patients", "patients": patients, "q": q}
    )


@router.get("/novy")
def new_patient_form(request: Request):
    return templates.TemplateResponse(
        request, "patients/form.html", {"active": "patients", "error": None, "values": {}}
    )


@router.post("/novy")
def create_patient(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    birth_year: int = Form(...),
    phone: str = Form(...),
    insurance_number: str = Form(...),
    insurer: str = Form(...),
    session: Session = Depends(get_session),
):
    values = dict(
        first_name=first_name,
        last_name=last_name,
        birth_year=birth_year,
        phone=phone,
        insurance_number=insurance_number,
        insurer=insurer,
    )
    try:
        PatientService(session).register(**values)
    except DuplicatePatientError as exc:
        return templates.TemplateResponse(
            request,
            "patients/form.html",
            {"active": "patients", "error": str(exc), "values": values},
            status_code=409,
        )
    flash(request, "Pacient byl uložen.")
    return RedirectResponse("/pacienti", status_code=303)
