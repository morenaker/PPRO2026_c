# Ordinace Na Vyhlídce – rezervační systém

Semestrální projekt PPRO (ZS 2026/2027), **zadání A: Rezervace v ordinaci**.
Tento soubor je **jediný zdroj pravdy**: zadání, technická dokumentace a rozhodnutí. Udržuje se průběžně spolu s kódem (viz [AGENTS.md](AGENTS.md)).

Stav: **kostra** (vrstvy, databáze s migracemi, docker, testy, přihlášení, správa testovacích dat, řez „Pacienti“, přehled lékařů a diáře). Ostatní funkce jsou v [plánu](#plán-a-stav).

## Dokumentace

- [docs/dokumentace.pdf](docs/dokumentace.pdf) – technická dokumentace podle zadání (oddíl 5); zdroj ve Wordu [docs/dokumentace.docx](docs/dokumentace.docx).
- [docs/ZMENY.md](docs/ZMENY.md) – seznam změn a požadavků.
- [docs/img/](docs/img/) – ER diagram a snímky obrazovek.

## Spuštění

```bash
docker compose up --build     # aplikace na http://localhost:8000 (migrace se spustí samy)
docker compose exec app pytest   # testy (běží proti samostatné DB ordinace_test)
```

### Přihlášení (ukázkové účty)

Aplikace vyžaduje přihlášení. Při startu se založí dva **ukázkové** účty (zobrazené i na přihlašovací stránce):

| Uživatel | Heslo | Role | Smí |
|---|---|---|---|
| `recepce` | `recepce-demo` | recepce | vše kromě Nastavení |
| `admin` | `admin-demo` | správce | vše + Nastavení (testovací data) |

Hesla jdou změnit proměnnými `DEMO_RECEPTION_PASSWORD` / `DEMO_ADMIN_PASSWORD`, podpis cookie přes `SECRET_KEY`.

### Testovací data

*Nastavení → Testovací data* (jen správce): **Přidat** vytvoří 30 pacientů, 3 lékaře s hodinami (vč. ordinace na jiné adrese bez objednávání), 10 výkonů a ~120 rezervací kolem dneška (proběhlé s návštěvami a výkony, nadcházející, zrušené; dva pacienti ruší opakovaně). **Odebrat** smaže jen záznamy s příznakem `is_demo` a vše, co se jich dotýká; reálná data zůstanou. Přidání podruhé je odmítnuto, dokud se data neodeberou.

Vývojové přihlašovací údaje DB jsou výchozí hodnoty v `docker-compose.yml` (jen lokálně, syntetická data). Přepsat jde přes `.env` (viz `.env.example`).

## Zadání (shrnutí)

**Klient:** MUDr. Jana Hrubá, Ordinace Na Vyhlídce. Soukromá praxe, tři lékaři na částečné úvazky a paní Věra na recepci, cca 900 pacientů.
Dnes: papírový diář, na konci měsíce ruční přepis výkonů pro pojišťovnu. Dvakrát za rok dva lidé na stejný čas.

### Co klient chce (musí být hotové)

1. Pacienti v evidenci: jméno, příjmení, rok narození, telefon, identifikátor pojištěnce, pojišťovna. Hledání podle příjmení nebo telefonu.
2. Lékaři a jejich ordinační hodiny (každý jiné dny a časy; jeden ordinuje v úterý odpoledne na jiné adrese – tam se objednávat nedá).
3. Rezervace na konkrétní termín u konkrétního lékaře, zakládá recepce, s poznámkou, proč pacient přichází.
4. Záznam o návštěvě: provedené výkony z číselníku (kód, název, body). Na návštěvě jich proběhne víc, výkon se opakuje; u některých se zapisuje počet.
5. Zrušení rezervace + přehled lidí, kteří ruší opakovaně.
6. Přehled volných termínů pro lékaře a týden (nejpoužívanější funkce).
7. Měsíční výkaz: za měsíc a lékaře seznam provedených výkonů a součet bodů.

### Na čem klient trvá (vynucuje aplikace)

- Dvě rezervace na stejný termín u stejného lékaře nejdou založit (ani omylem, ani ručně).
- Rezervaci nelze založit mimo ordinační hodiny lékaře.
- Výkon nelze zapsat k návštěvě, která se ještě neuskutečnila.
- Historie pacienta se nemaže.

### Mimochodem (zvážit, nemusí se splnit)

Zvládne to paní Věra (jednoduché UI) · rychlé načítání při zvonícím telefonu · tablet (nespěchá) · online objednávání pacientů (klient se bojí).

### Společné minimum projektu

Tři vrstvy se závislostmi jedním směrem · relační DB v Dockeru s migracemi · ≥ 5 entit a ≥ 1 vazba M:N · testy · spuštění `docker compose up` · technická dokumentace. Jen syntetická data, žádné přihlašovací údaje v repozitáři.

## Rozhodnutí

Otevřené body ze zadání. Konkrétní varianta + proč. Klient může na cvičení změnit názor – proto je každé rozhodnutí izolované (viz sloupec *Kde je zakotveno*).

| # | Otevřený bod | Rozhodnutí | Proč | Kde je zakotveno |
|---|---|---|---|---|
| D1 | Délka termínu | **Rezervace má vlastní délku** (`starts_at`–`ends_at`). Výchozí délka 15 min (`DEFAULT_APPOINTMENT_MINUTES`), jde zvolit jinou. | Klient říká „podle toho, co se dělá“; pevná mřížka by to neunesla. Rozsahy jdou snadno kontrolovat na překryv. | `appointment.starts_at/ends_at`, `config.py` |
| D2 | Kdo zakládá rezervaci | **Zatím jen recepce.** Sloupec `created_via` (`reception`) nechává otevřenou cestu k online objednávání. | Klient se online objednávání bojí; jednodušší a bezpečnější. Změna = nový router, ne přepis modelu. | `appointment.created_via` |
| D3 | Zrušená rezervace | **Zůstává v DB** se stavem `cancelled` (+ `cancelled_at`, `cancel_reason`); z diáře a z přehledu volných termínů zmizí, uvolní termín. Statistika ruší z těchto záznamů. | Řeší rozpor „ať zmizí z diáře“ × „chci statistiku“: zmizí z pohledu, ne z dat. | `appointment.status`, exclusion constraint (`status <> 'cancelled'`) |
| D4 | Totožnost pacienta | **Pacienta určuje číslo pojištěnce** (unikátní). Pokus o duplicitu je odmítnut srozumitelnou hláškou a odkazem na existujícího pacienta. | Jméno se opakuje („paní Nováková třikrát“), číslo pojištěnce ne. | `patient.insurance_number` UNIQUE, `DuplicatePatientError` |
| D5 | Nemoc lékaře | **Rezervace se nemažou ani nepřesouvají automaticky**; systém je jen označí k přeobjednání a nechá obvolání na recepci. | Přesun na jiného lékaře je lékařské rozhodnutí; automatika by pacienty překvapila. Je to nejmenší riziko. | *Plánováno* (zatím neimplementováno) |
| D6 | Ordinace na jiné adrese | Ordinační hodiny mají příznak `bookable`; v hodinách s `bookable = false` se rezervace nezakládá. | Klient: „tam se objednávat nedá“. | `office_hours.bookable` |
| D7 | Jak se hlídá překryv | **Exclusion constraint v PostgreSQL** (`btree_gist`, `tstzrange`) na (lékař, rozsah času), jen pro nezrušené rezervace. | Klient trvá na „ani omylem“; kontrola v aplikaci by měla souběh. DB to zaručí vždy. | migrace `0001`, `no_overlap_per_doctor` |
| D8 | Mazání | Žádné `DELETE`; cizí klíče `ON DELETE RESTRICT`. | „Historie pacienta se nemaže.“ | modely, migrace |
| D9 | Časová zóna | Čas se ukládá jako `timestamptz`, zobrazuje se v `Europe/Prague`. | Správné chování kolem změny času. | `config.py` |
| D10 | Technologie | FastAPI + Jinja2 (SSR, bez JS frameworku), PostgreSQL 16, SQLAlchemy 2 + Alembic, pytest, Docker Compose. | Zadáno uživatelem: co nejjednodušší a zdarma; SSR je rychlé i na slabším zařízení. | `requirements.txt`, `Dockerfile` |
| D12 | Přihlášení | **Jen ukázkové účty** (role recepce/správce), hesla uložená jako PBKDF2 hash, session v podepsané cookie. Hesla jsou vývojové výchozí hodnoty z konfigurace, ne tajemství. | Zadání zakazuje přihlašovací údaje v repozitáři, a přitom se má dát aplikace ukázat. Výchozí demo hesla jsou veřejná a syntetická; ostré nasazení by je přepsalo přes env. Plnohodnotná správa uživatelů je mimo rozsah. | `services/auth.py`, `app_user`, `config.py` |
| D13 | Testovací data | Řádky mají příznak `is_demo`; odebrání maže jen je (a závislé rezervace/návštěvy). **Je to jediné místo, kde se data mažou** – výjimka z D8, jen pro syntetická data. | Dá se ukázat prázdná i naplněná aplikace, bez rizika pro reálná data. | `services/demo_data.py`, sloupce `is_demo` |
| D11 | Návštěva | `Visit` vzniká jen k existující rezervaci (1:1) a jen když má stav `completed`. | Pravidlo „výkon nelze zapsat k neuskutečněné návštěvě“. | `visit.appointment_id` UNIQUE, pravidlo ve service *(plánováno)* |
| D14 | Vzhled a úvodní stránka | **Klidný pracovní nástroj místo „ukázkové“ šablony.** Systémové písmo s pevnou škálou, teplé neutrální plochy, jedna tlumená borovicová akcentní barva (`--accent`), světlý i tmavý režim. Úvod je **„Dnes“**: dnešní objednaní a kdo dnes ordinuje, místo dlaždic s čísly. Diář je seskupený po dnech, pacienti v tabulce, časy v tabulkových číslicích. | Recepce potřebuje na první pohled vidět dnešek, ne statistiky; dlaždice s velkými čísly a obří titulky působily jako generovaná šablona. Celý vzhled je v CSS proměnných, takže změna barvy nebo hustoty je úprava jednoho souboru. | `app/web/static/css/app.css`, `templates/home.html`, `OverviewService.todays_appointments` |

## Architektura

```
web (FastAPI routery + Jinja2)  →  services (pravidla, transakce)  →  repositories (SQL)  →  models (schéma)
```

Závislosti jdou jen doprava. Podrobná pravidla v [AGENTS.md](AGENTS.md).

```
app/
  main.py            vstupní bod, registrace routerů
  config.py          nastavení z proměnných prostředí
  db.py              engine, session, závislost get_session
  models/            SQLAlchemy modely (schéma + omezení)
  repositories/      dotazy na DB
  services/          obchodní pravidla, DomainError
  web/               routery, šablony (templates/), statika (static/css/app.css)
alembic/versions/    migrace
tests/               pytest (proti skutečnému PostgreSQL)
```

**Jak přidat novou sekci:** model (+ migrace) → repository → service → router v `app/web/routers/` → `include_router` v `main.py` → položka v `NAV_ITEMS` → šablony → test → řádek do tohoto README.

## Datový model

```
patient 1───* appointment *───1 doctor 1───* office_hours
                   1
                   │ 1:1
                 visit 1───* visit_procedure *───1 procedure   (M:N s počtem)
```

| Tabulka | Účel | Klíčová omezení |
|---|---|---|
| `patient` | pacient | `insurance_number` UNIQUE |
| `doctor` | lékař | – |
| `office_hours` | ordinační hodiny lékaře (den v týdnu, od–do, místo) | `weekday` 0–6, `end_time > start_time`, `bookable` |
| `appointment` | rezervace | `ends_at > starts_at`, stav ∈ {booked, cancelled, completed}, **exclusion** `no_overlap_per_doctor` |
| `procedure` | číselník výkonů (kód, název, body) | `code` UNIQUE, `points ≥ 0`, `requires_quantity` |
| `visit` | záznam návštěvy | 1:1 s `appointment` |
| `visit_procedure` | M:N návštěva ↔ výkon | PK (`visit_id`, `procedure_id`), `quantity ≥ 1` |
| `app_user` | ukázkové účty (jméno, role, hash hesla) | `username` UNIQUE, role ∈ {admin, reception} |

Tabulky `patient`, `doctor`, `procedure`, `appointment` mají navíc `is_demo` (viz D13).

## Testy

`pytest` běží proti skutečnému PostgreSQL (kvůli exclusion constraintu), v databázi `ordinace_test` vytvořené z migrací. Každý test běží v transakci, která se vrací zpět.

Pokryto: směr závislostí mezi vrstvami (`test_architecture.py`), hledání a duplicita pacienta, zákaz překryvu rezervací v DB, uvolnění termínu po zrušení, přihlášení/odhlášení/přesměrování, oprávnění (recepce nesmí do Nastavení), přidání a odebrání testovacích dat (reálná data zůstanou), vykreslení stránek.

## Plán a stav

| Funkce | Stav |
|---|---|
| Kostra, docker, migrace, testy, Apple-like UI shell | hotovo |
| Přihlášení (ukázkové účty, role), Nastavení → testovací data | hotovo |
| Úvod „Dnes“ (dnešní rezervace, kdo ordinuje), seznam lékařů s hodinami, diář po dnech (jen čtení) | hotovo |
| 1 Pacienti (evidence, hledání, duplicita) | hotovo (vertikální řez) |
| 2 Lékaři a ordinační hodiny | čtení hotové, zakládání/úprava chybí |
| 3 Rezervace (vč. kontroly ordinačních hodin) | model + DB pravidlo hotové, service/UI chybí |
| 4 Záznam návštěvy a výkony | model hotový, service/UI chybí |
| 5 Zrušení + statistika rušících | model hotový, service/UI chybí |
| 6 Přehled volných termínů (týden × lékař) | chybí |
| 7 Měsíční výkaz | chybí |
| Seed syntetických dat (číselník výkonů, lékaři) | hotovo (viz Testovací data) |

## Otevřené otázky na klienta (cvičení)

Zapisovat sem, na co jsme se ptali a co klient odpověděl; podle odpovědi aktualizovat tabulku rozhodnutí.

- *(zatím nic)*

## Skilly a nástroje pro AI

Nainstalováno v `.claude/skills/` (viz `skills-lock.json`): `fastapi`, `python-testing-patterns`, `docker-patterns`, `sqlalchemy-alembic-expert-best-practices-code-review`, `frontend-design`, `web-design-guidelines`, `ios-hig-design`, a pro vzhled (D14) `impeccable`, `emil-design-eng`, `better-typography`, `design-taste-frontend`.
