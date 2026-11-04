import pytest
from sqlalchemy import func, select

from app.models import Appointment, Patient
from app.services.demo_data import DemoDataService
from app.services.errors import DomainError
from app.services.patients import PatientService


def test_add_creates_data_and_second_add_is_refused(session):
    service = DemoDataService(session)
    status = service.add()
    assert status.patients == 30 and status.doctors == 3 and status.procedures == 10
    assert status.appointments > 0
    with pytest.raises(DomainError):
        service.add()


def test_remove_deletes_only_demo_data(session):
    real = PatientService(session).register(
        first_name="Skutečný", last_name="Pacient", birth_year=1970, phone="1",
        insurance_number="REAL1", insurer="111",
    )
    service = DemoDataService(session)
    service.add()
    status = service.remove()

    assert not status.present
    assert session.scalar(select(func.count()).select_from(Appointment)) == 0
    assert [p.id for p in session.scalars(select(Patient))] == [real.id]


def test_settings_buttons_add_and_remove(admin_client, session):
    admin_client.post("/nastaveni/testovaci-data/pridat")
    assert DemoDataService(session).status().present
    assert "DEMO" not in admin_client.get("/pacienti").text  # čísla pojištěnců se v seznamu nezobrazují
    assert "+420 777 000" in admin_client.get("/pacienti").text

    admin_client.post("/nastaveni/testovaci-data/odebrat")
    assert not DemoDataService(session).status().present
