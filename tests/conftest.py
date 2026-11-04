import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.config import settings

TEST_DB_NAME = "ordinace_test"


def _test_url() -> str:
    return make_url(settings.database_url).set(database=TEST_DB_NAME).render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def engine():
    """Samostatná databáze pro testy, schéma vzniká stejnými migracemi jako v produkci."""
    admin = create_engine(
        make_url(settings.database_url).set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    with admin.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME} WITH (FORCE)"))
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
    admin.dispose()

    url = _test_url()
    # alembic/env.py čte settings.database_url; pro migraci ho přepíšeme na testovací DB.
    original = settings.database_url
    settings.database_url = url
    command.upgrade(Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini")), "head")
    settings.database_url = original

    eng = create_engine(url)
    yield eng
    eng.dispose()


@pytest.fixture()
def session(engine):
    """Každý test běží v transakci, která se na konci zahodí."""
    connection = engine.connect()
    transaction = connection.begin()
    sess = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
    yield sess
    sess.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(session):
    """Nepřihlášený klient; ukázkové účty jsou založené."""
    from fastapi.testclient import TestClient

    from app.db import get_session
    from app.main import app
    from app.services.auth import AuthService

    AuthService(session).ensure_demo_users()
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


def _login(client, username, password):
    response = client.post("/prihlaseni", data={"username": username, "password": password})
    assert response.status_code in (200, 303)
    return client


@pytest.fixture()
def admin_client(client):
    from app.config import settings

    return _login(client, "admin", settings.demo_admin_password)


@pytest.fixture()
def reception_client(client):
    from app.config import settings

    return _login(client, "recepce", settings.demo_reception_password)
