from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.db import SessionLocal
from app.services.auth import AuthService
from app.web.deps import LoginRequired
from app.web.routers import appointments, auth, doctors, home, patients, settings as settings_router
from app.web.templating import BASE_DIR


@asynccontextmanager
async def lifespan(_: FastAPI):
    with SessionLocal() as session:
        AuthService(session).ensure_demo_users()
    yield


app = FastAPI(title="Ordinace Na Vyhlídce", lifespan=lifespan)

# Cookie je podepsaná, HttpOnly a SameSite=Lax (základní ochrana proti CSRF).
app.add_middleware(
    SessionMiddleware, secret_key=settings.secret_key, same_site="lax", https_only=False, max_age=60 * 60 * 12
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.exception_handler(LoginRequired)
async def _login_required(_: Request, __: LoginRequired):
    return RedirectResponse("/prihlaseni", status_code=303)


# Nová sekce aplikace = nový router zde + položka v NAV_ITEMS.
app.include_router(auth.router)
app.include_router(home.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(settings_router.router)
