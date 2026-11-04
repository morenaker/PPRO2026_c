# Seznam změn

Záznam požadavků a změn v projektu *Ordinace Na Vyhlídce – rezervační systém* (PPRO, zadání A).
Nejnovější nahoře. Rozhodnutí, která z požadavků vyplynula, jsou v [README › Rozhodnutí](../README.md#rozhodnutí).

---

## 4. 11. 2026 – vylepšení UI a dotažení projektu k odevzdání

**Požadavek (Samuel Mader, 4. 11. 2026):** vylepšit vzhled aplikace, aby nepůsobila jako vygenerovaná AI;
k tomu doplnit vše ostatní potřebné k odevzdání – interní/technickou dokumentaci, seznam změn a nahrání
na veřejný GitHub repozitář.

### Uživatelské rozhraní (README D14)

- **Nový vizuální směr:** místo kopie Apple šablony (velké titulky, dlaždice s čísly, „pilulková“ tlačítka,
  typická modrá) klidný pracovní nástroj pro recepci. Teplé neutrální plochy, jedna tlumená borovicová akcentní
  barva, pevná typografická škála, čísla a časy v tabulkových číslicích.
- **Design tokeny** v `app/web/static/css/app.css`: barvy, zaoblení (12–16 px), stíny, typografická škála,
  stavové barvy (úspěch, varování, chyba). Světlý i tmavý režim, `prefers-reduced-motion`, `:focus-visible`,
  barva výběru textu, kurzoru a posuvníků.
- **Úvodní stránka „Dnes“:** v nadpisu dnešní datum česky, seznam dnešních objednaných (čas od–do, pacient,
  důvod, lékař, stav), panel *Dnes ordinuje* (kdo a kde má dnes hodiny) a stručný souhrn evidence.
  Nahradila čtyři dlaždice s velkými čísly.
- **Diář** seskupený po dnech („Dnes, …“, „Zítra, …“), hlavička dne zůstává při posouvání nahoře, stav
  rezervace jako barevný štítek (Objednáno / Proběhlo / Zrušeno), zrušené přeškrtnuté.
- **Pacienti** v tabulce (jméno, rok narození, telefon, pojišťovna), hledací pole s ikonou, prázdné stavy,
  které poradí další krok („Nikoho jsme nenašli… založte ho“).
- **Lékaři:** ordinační hodiny po dnech, dnešní den zvýrazněný, štítek „bez objednávání“ u pobočky.
- **Nový pacient:** formulář ve dvou sloupcích, nápověda u čísla pojištěnce, pole 16 px (iPad nepřibližuje).
- **Přihlášení:** zjednodušené, logo ordinace (vlastní SVG značka), ukázkové účty v přehledné tabulce.
- **Nastavení:** stav testovacích dat štítkem, souhrn v řádcích místo vnořených karet.
- **Navigace:** průsvitná lišta, aktivní položka zvýrazněná, dnešní datum a přihlášený uživatel vpravo.
- **Responzivita:** tablet (skrytí data v liště, diář do dvou řádků), mobil (jeden sloupec).
- **Cache stylopisu:** odkaz na CSS nese otisk obsahu (`app.css?v=…`), prohlížeč tak po změně vzhledu
  nenačte starou verzi.

### Aplikační logika a architektura

- `OverviewService.todays_appointments()` + `AppointmentRepository.list_between()` pro úvodní stránku.
- Filtry šablon pro český zápis data (`středa 4. listopadu`, „Dnes“/„Zítra“) v `app/web/templating.py`.
- **Oprava porušení vrstev** (zadání, povinné minimum bod 1):
  - endpoint `/health` volal SQL přímo v routeru → přesunuto do `HealthRepository` + `HealthService`;
  - `DemoDataService` psal SQL dotazy → přesunuto do nového `DemoDataRepository`;
  - `web/deps.py` importoval konstantu role z modelů → nově přes `services.auth`.

### Testy

- `tests/test_architecture.py` – automaticky hlídá směr závislostí `web → services → repositories → models`
  (čte importy přes AST; ověřeno, že porušení zachytí).
- `tests/test_pages.py` – všechny stránky se vykreslí bez dat i s ukázkovými daty; úvod ukazuje jen dnešní
  rezervace; prázdné hledání radí, co dál.
- Celkem **33 testů** (dříve 15), všechny prochází (`docker compose exec app pytest`).

### Dokumentace a repozitář

- `docs/dokumentace.docx` a `docs/dokumentace.pdf` – technická dokumentace podle oddílu 5 zadání
  (titulní strana, úvod, datový model s ER diagramem, architektura, technologie, spuštění, testy,
  protokol o zacyklení, přiznání práce s AI).
- `docs/img/` – ER diagram a snímky obrazovek.
- `docs/ZMENY.md` – tento seznam změn.
- README: nové rozhodnutí D14, odkaz na dokumentaci; AGENTS.md: rozšířená pravidla vzhledu.
- Nové skilly pro AI asistenta v `.claude/skills/`: `impeccable`, `emil-design-eng`, `better-typography`,
  `design-taste-frontend` (zapsané v `skills-lock.json`).
- Projekt nahrán do repozitáře https://github.com/morenaker/PPRO2026_c.

---

## Do 4. 11. 2026 – kostra aplikace

- Tři vrstvy (web, services, repositories, models), PostgreSQL 16 v Dockeru, migrace Alembic `0001`, `0002`.
- Datový model: pacient, lékař, ordinační hodiny, rezervace, návštěva, výkon, vazba návštěva ↔ výkon (M:N),
  uživatelé. Zákaz překryvu rezervací vynucuje databáze (exclusion constraint).
- Přihlášení s ukázkovými účty (recepce, správce), Nastavení → přidání/odebrání testovacích dat.
- Evidence pacientů s hledáním a kontrolou duplicity, přehled lékařů, diář (jen čtení).
- Testy proti skutečnému PostgreSQL.
