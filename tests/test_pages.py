"""Smoke testy obrazovek: každá stránka se vykreslí s daty i bez nich."""
from datetime import timedelta

import pytest

from app.services.demo_data import DemoDataService
from app.services.overview import OverviewService, start_of_today

PAGES = ["/", "/rezervace", "/pacienti", "/pacienti/novy", "/lekari", "/nastaveni"]


@pytest.mark.parametrize("path", PAGES)
def test_page_renders_empty(admin_client, path):
    assert admin_client.get(path).status_code == 200


@pytest.mark.parametrize("path", PAGES)
def test_page_renders_with_demo_data(admin_client, session, path):
    DemoDataService(session).add()
    assert admin_client.get(path).status_code == 200


def test_home_lists_only_todays_appointments(admin_client, session):
    DemoDataService(session).add()
    today = OverviewService(session).todays_appointments()
    start = start_of_today()
    assert all(start <= a.starts_at < start + timedelta(days=1) for a in today)

    page = admin_client.get("/").text
    assert "Dnes objednaní" in page
    for a in today:
        assert a.patient.last_name in page


def test_empty_search_explains_what_to_do(reception_client):
    page = reception_client.get("/pacienti", params={"q": "Neexistující"}).text
    assert "Nikoho jsme nenašli" in page
