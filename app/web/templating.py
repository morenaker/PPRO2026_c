import hashlib
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.config import settings

BASE_DIR = Path(__file__).resolve().parent

WEEKDAYS = ["pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota", "neděle"]
WEEKDAYS_SHORT = ["po", "út", "st", "čt", "pá", "so", "ne"]
MONTHS_GENITIVE = [
    "ledna", "února", "března", "dubna", "května", "června",
    "července", "srpna", "září", "října", "listopadu", "prosince",
]


def _context(request: Request) -> dict:
    """Kontext dostupný ve všech šablonách: přihlášený uživatel a jednorázové zprávy."""
    session = request.session
    return {"user": session.get("user"), "flashes": session.pop("flash", []), **_today_context()}


templates = Jinja2Templates(directory=BASE_DIR / "templates", context_processors=[_context])


def _local(value: datetime) -> datetime:
    return value.astimezone(ZoneInfo(settings.timezone))


def today_local() -> date:
    return datetime.now(ZoneInfo(settings.timezone)).date()


def local_date(value: datetime) -> date:
    return _local(value).date()


def fmt_day(value: date | datetime) -> str:
    """„středa 4. listopadu“; u dneška a zítřka předřadí „Dnes“ / „Zítra“."""
    d = local_date(value) if isinstance(value, datetime) else value
    label = f"{WEEKDAYS[d.weekday()]} {d.day}. {MONTHS_GENITIVE[d.month - 1]}"
    if d.year != today_local().year:
        label += f" {d.year}"
    if d == today_local():
        return f"Dnes, {label}"
    if d == today_local() + timedelta(days=1):
        return f"Zítra, {label}"
    return label[0].upper() + label[1:]


def fmt_datetime(value: datetime) -> str:
    v = _local(value)
    return f"{WEEKDAYS[v.weekday()][:2]} {v.day}. {v.month}. {v.year} {v:%H:%M}"


def fmt_time(value) -> str:
    if isinstance(value, datetime):
        value = _local(value)
    return f"{value:%H:%M}"


def _today_context() -> dict:
    d = today_local()
    return {"today_date": d, "today_label": fmt_day(d), "today_weekday": d.weekday()}


# Navigace na jednom místě; nová sekce = jeden řádek. `admin_only` položky vidí jen správce.
NAV_ITEMS = [
    {"key": "home", "label": "Přehled", "href": "/", "admin_only": False},
    {"key": "appointments", "label": "Diář", "href": "/rezervace", "admin_only": False},
    {"key": "patients", "label": "Pacienti", "href": "/pacienti", "admin_only": False},
    {"key": "doctors", "label": "Lékaři", "href": "/lekari", "admin_only": False},
    {"key": "settings", "label": "Nastavení", "href": "/nastaveni", "admin_only": True},
]
templates.env.globals["nav_items"] = NAV_ITEMS
# Otisk stylopisu do URL, aby prohlížeč po změně vzhledu nenačítal starou verzi z cache.
templates.env.globals["css_version"] = hashlib.sha1(
    (BASE_DIR / "static" / "css" / "app.css").read_bytes()
).hexdigest()[:10]
templates.env.globals["weekdays"] = WEEKDAYS
templates.env.globals["weekdays_short"] = WEEKDAYS_SHORT
templates.env.filters["day"] = fmt_day
templates.env.filters["local_date"] = local_date
templates.env.filters["dt"] = fmt_datetime
templates.env.filters["hm"] = fmt_time
