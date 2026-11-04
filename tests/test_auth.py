from app.config import settings
from app.services.auth import hash_password, verify_password


def test_password_hash_roundtrip():
    stored = hash_password("tajne")
    assert stored != "tajne"
    assert verify_password("tajne", stored)
    assert not verify_password("jine", stored)


def test_anonymous_is_redirected_to_login(client):
    response = client.get("/pacienti", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/prihlaseni"


def test_login_with_wrong_password_fails(client):
    response = client.post("/prihlaseni", data={"username": "admin", "password": "spatne"})
    assert response.status_code == 401
    assert "Nesprávné" in response.text


def test_login_and_logout(client):
    response = client.post(
        "/prihlaseni",
        data={"username": "recepce", "password": settings.demo_reception_password},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert client.get("/pacienti").status_code == 200

    client.post("/odhlasit")
    assert client.get("/pacienti", follow_redirects=False).status_code == 303


def test_reception_cannot_open_settings(reception_client):
    assert reception_client.get("/nastaveni").status_code == 403
    assert reception_client.post("/nastaveni/testovaci-data/pridat").status_code == 403


def test_admin_can_open_settings(admin_client):
    assert admin_client.get("/nastaveni").status_code == 200
