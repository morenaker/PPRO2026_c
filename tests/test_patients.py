import pytest

from app.services.errors import DuplicatePatientError
from app.services.patients import PatientService

PATIENT = dict(
    first_name="Alena",
    last_name="Testová",
    birth_year=1980,
    phone="600111222",
    insurance_number="8001010001",
    insurer="111",
)


def test_register_and_search_by_surname_and_phone(session):
    service = PatientService(session)
    service.register(**PATIENT)

    assert [p.last_name for p in service.search("Test")] == ["Testová"]
    assert [p.last_name for p in service.search("600111")] == ["Testová"]
    assert service.search("Neexistuje") == []


def test_duplicate_insurance_number_is_rejected(session):
    service = PatientService(session)
    service.register(**PATIENT)

    with pytest.raises(DuplicatePatientError):
        service.register(**{**PATIENT, "first_name": "Jiná"})


def test_pages_render_for_logged_in_user(reception_client):
    for url in ("/", "/pacienti", "/pacienti/novy", "/lekari", "/rezervace"):
        assert reception_client.get(url).status_code == 200, url
    assert reception_client.get("/health").json() == {"status": "ok"}
