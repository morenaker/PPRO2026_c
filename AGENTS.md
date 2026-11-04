# AGENTS.md – pravidla pro AI asistenta

Tento soubor říká, co je to za projekt a jak se v něm má asistent chovat. Čti ho na začátku každé práce.

## Co je to za projekt

Semestrální projekt z předmětu **Pokročilé programování (PPRO), ZS 2026/2027**, zadání **A: Rezervace v ordinaci**
(klientka MUDr. Jana Hrubá, Ordinace Na Vyhlídce). Webová aplikace pro recepci: pacienti, lékaři a ordinační hodiny,
rezervace, záznam návštěv s výkony, rušení, přehled volných termínů, měsíční výkaz.

Repozitář: https://github.com/morenaker/PPRO2026_c.git (větev `main`).
Zadání (PDF) leží mimo repozitář; jeho obsah je shrnut v `README.md`.

## Zdroj pravdy

**`README.md` je jediný zdroj pravdy**: zadání, technická dokumentace i seznam rozhodnutí. Z toho plyne:

- Každá změna chování, modelu, architektury, příkazů nebo rozhodnutí se **ve stejném kroku** propíše do `README.md`.
- Nové rozhodnutí = nový řádek v sekci *Rozhodnutí* (otevřený bod, varianta, proč). Změněné rozhodnutí se nepřepisuje potichu: původní řádek se označí jako nahrazený a odkáže na nový.
- Když kód a README nesedí, je to chyba – oprav to nebo se zeptej, co platí.
- `AGENTS.md` popisuje, **jak pracovat**; `README.md` popisuje, **co a proč se staví**.

## Technologie (pevně dané)

Python 3.12, FastAPI, Jinja2 šablony na serveru (bez JS frameworku), PostgreSQL 16, SQLAlchemy 2 + Alembic, pytest,
Docker Compose. Novou závislost přidávej jen s důvodem a zapiš ji do README.

## Architektura

Tři vrstvy, závislosti **jedním směrem**: `web → services → repositories → models`.

| Vrstva | Složka | Smí | Nesmí |
|---|---|---|---|
| Web | `app/web/` | parsovat požadavek, volat service, vykreslit šablonu | SQL, obchodní pravidla |
| Service | `app/services/` | obchodní pravidla, transakce (`commit`) | znát FastAPI/HTTP, psát SQL dotazy |
| Repository | `app/repositories/` | dotazy na DB | pravidla, commit |
| Models | `app/models/` | schéma a omezení | logika |

- Pravidla, na kterých klient trvá, se vynucují **v databázi** (constraint), ne jen v aplikaci. Service je navíc překládá na srozumitelnou chybu (`DomainError`).
- Kód má být připravený na změnu: nová sekce = nový router + service + repository + položka v `NAV_ITEMS`. Nic se nekopíruje.
- Historie se nemaže (pacienti, rezervace, návštěvy, výkony): žádné `DELETE` endpointy, FK `ON DELETE RESTRICT`.

## Postup práce

1. Změna schématu = **nová Alembic migrace** (`alembic/versions/`), nikdy úprava již pushnuté migrace.
2. Ke každému pravidlu klienta existuje test. Nejdřív test, pak kód, kde to dává smysl.
3. Před dokončením úkolu: `docker compose up` musí fungovat a `pytest` musí projít. Pokud jsem to nespustil, řeknu to.
4. Malé, ucelené commity s česky psanou zprávou v rozkazovacím způsobu. Commit/push jen na pokyn uživatele.
5. Otevřený bod ze zadání: **rozhodni, zapiš do README**, jdi dál. Klient na cvičení může názor změnit, proto
   navrhuj tak, aby změna nebyla přepisem (izoluj rozhodnutí do jedné service/konstanty).

## Data a bezpečnost

- Jen **syntetická data**. Žádné reálné osobní údaje, nic z práce ani ze stáže.
- Žádná hesla, tokeny ani přihlašovací údaje v repozitáři. Konfigurace přes proměnné prostředí; `.env` je v `.gitignore`.
- Ukázkové účty (`admin`, `recepce`) a jejich demo hesla jsou vědomá výjimka (README D12); nikdy sem nedávej reálná hesla.
- Výchozí vývojové hodnoty v `docker-compose.yml` (`ordinace_dev`) nejsou tajemství a nikdy se nepoužijí mimo lokální vývoj.

## Vzhled (UI)

Cíl: pocit produktu od Applu, ale jako klidný pracovní nástroj, ne šablona (README D14). Řiď se skilly `ios-hig-design`,
`frontend-design`, `web-design-guidelines`, `impeccable`, `emil-design-eng` a `better-typography`.

- Systémový font (SF Pro přes `-apple-system`), velké čisté titulky, hodně bílého místa, zaoblení 12–18 px.
- Světlý i tmavý režim (`prefers-color-scheme`), průsvitná navigace, jedna akcentní barva (`--accent`).
- Všechny barvy, zaoblení a stíny jen přes CSS proměnné v `app/web/static/css/app.css`. Žádné inline barvy.
- Přístupnost: kontrast, `:focus-visible`, popisky polí, respektovat `prefers-reduced-motion`. Funguje na tabletu.
- Rychlost: server-side render, žádné těžké knihovny. Recepční nesmí čekat, až se „to načte“.
- Obsluhuje to nezkušená uživatelka: málo kroků, srozumitelné české hlášky, žádný žargon.

## Jazyk

Komunikace s uživatelem, UI texty, README a commity: **česky**. Identifikátory v kódu a názvy tabulek: **anglicky**.

## Dostupné skilly (`.claude/skills/`)

`fastapi`, `python-testing-patterns`, `docker-patterns`, `sqlalchemy-alembic-expert-best-practices-code-review`,
`frontend-design`, `web-design-guidelines`, `ios-hig-design`, `impeccable`, `emil-design-eng`, `better-typography`,
`design-taste-frontend`. Použij je tam, kde se hodí; nevymýšlej, co už skill řeší.

## Když si nejsem jistý

Zeptám se. Otázky o tom, co klient chtěl, patří uživateli (studentovi); otázky „jak to technicky“ řeším sám a zapíšu.
