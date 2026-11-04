# 017: AI v CI, Fuchs2, presunuté akcie, oneskorenie behu

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-04 (pred odovzdaním: vyhľadávanie na webe presunuté do 018). Podklad: prvý plánovaný beh 41827290413 (2026-11-04).

### 1. AI v GitHub Actions zlyhala
V behu 41827290413 všetkých 8 dávok: `API call 1 failed: Connection error. — batch skipped` → 0 akcií zatriedených, zverejnený súbor je len s vrstvou 1. Lokálne to fungovalo.
- Zisti príčinu: loguj typ výnimky a príčinu (`exc.__cause__`), nie len text. Over, či secret v CI naozaj prichádza (len True/False a dĺžka), či nie je nastavená iná premenná (napr. base URL), či ide o výpadok API (status stránka Anthropicu pre daný čas).
- Pridaj opakovanie s rastúcim čakaním pri sieťových chybách a 429/5xx (napr. 3 pokusy). Oprav počítadlo v logu („API call 1“ pri každej dávke).
- Ak AI v behu zlyhá, akcie bez výsledku sa majú skúsiť znova v ďalšom behu (nesmú sa uložiť do cache ako hotové).
- Over ručným behom workflow (`workflow_dispatch`), že AI v CI prebehne. Uveď odkaz na beh a počty zo súhrnu.

### 2. Vyhľadávanie na webe
Presunuté do samostatnej úlohy 018 (Matej 2026-11-04, šetrenie kreditov). V tejto úlohe nerob.

### 3. Fuchs2 stráca akcie
Beh 41827290413: `source timeout 120s exceeded — stopping at 14 events` (lokálne 23). Sitemap s oknom 365 dní je ~180 požiadaviek. Zvýš `timeout_secs` pre Fuchs2 tak, aby stačil s rezervou (z GitHubu sú požiadavky pomalšie), alebo zníž počet požiadaviek bez straty budúcich akcií. Zdôvodni.

### 4. Presunuté a odložené akcie
Fuchs2 má akcie „POSTPONED: deBasement“ a „PŘESUNUTO DO MEETFACTORY / …“.
- Akcia presunutá do iného podniku: v pôvodnom podniku ju vyraď a zaloguj (v novom podniku je pod vlastným zdrojom).
- Odložená akcia bez nového dátumu: nový stav `postponed` (zmena dátového modelu, navrhnutá hlavným chatom; zapíš do `data-model.md` a `decisions.md`). Z názvu odstráň prefix („POSTPONED:“).
- Rozpoznávanie (EN/CZ/SK: postponed, odloženo, přesunuto, moved to…) v spoločnej normalizácii, nie len pre Fuchs2.

### 5. Ranný beh príde neskoro
Plánovaný beh na 04:17 UTC sa spustil o 12:12 UTC (oneskorenie 8 h). **Matej: jeden beh denne stačí, oneskorenie je v poriadku** (upravené pred odovzdaním, druhý beh sa nepridáva). Len do súhrnu behu zapíš oneskorenie oproti plánovanému času, aby bolo vidno, keby sa beh vynechal alebo chodil až večer.

### 6. Report
Commit práce (finálny hash), odkaz na ručný beh v CI, počty formátov po vrstve 2, cena AI v CI. Nový `docs/review/classification-RRRR-MM-DD.md`.

## Report

Dátum: 2026-11-04. Commit: `08bf152` (origin/main po pushi).

### Čo je hotové

**1. AI v GitHub Actions (classify_ai.py)**
- Pridané 3-pokusové opakovanie s exponenciálnym čakaním (5 s, 10 s) pre `anthropic.APIConnectionError`, `RateLimitError` a 5xx chyby (`_call_api_with_retry`).
- Log chýb teraz loguje aj typ výnimky a `exc.__cause__`.
- Opravené počítadlo dávok: predtým ukazovalo `API call 1 failed` pre každú dávku; teraz `API call 2/8 failed`.
- Správanie cache pri zlyhaní dávky: overené — `_build_ai_cache` zahrnie len udalosti s `method=llm`, takže nedokončené dávky ostanú ako `classification=null` a budú opätovne spracované v ďalšom behu.

**2. Fuchs2 timeout**
- Pridané `"timeout_secs": 360` do `data/venues.json` (Fuchs2 source config).
- Zdôvodnenie: ~178 event-page GET requestov × 1 s rate-limit = min. 180 s; 360 s dáva dostatočnú rezervu pre pomalšie siete v GitHub Actions.

**3. Presunuté a odložené akcie (normalize.py)**
- Nový stav `postponed` v dátovom modeli (`docs/data-model.md`).
- `_detect_postponed_moved(title)` v `pipeline/normalize.py`: deteguje prefixes EN/CZ/SK.
  - `POSTPONED:`, `ODLOŽENO:`, `ODLOŽENÁ:`, `ODLOŽEN[OA]:` → `status=postponed`, prefix odstránený z názvu a z ID.
  - `PŘESUNUTO DO`, `PRESUNUTO DO`, `MOVED TO` → udalosť vyradená, zalogovaná.
- `normalize_event` vracia `None` pre presunuté udalosti; `pipeline/main.py` ich filtruje.
- ID generované z vyčisteného názvu → konzistentné ID medzi `POSTPONED: deBasement` a `deBasement`.

**4. Ranný beh oneskorenie**
- `daily.yml` krok „Log run metadata" teraz počíta a loguje oneskorenie voči 04:17 UTC do job summary.

**5. Testy**
- `tests/test_normalize.py`: 20 testov pre postponed/moved handling.
- Celá sada: 165 testov, 0 zlyhaní.
- Pridaná fixture `tests/fixtures/fuchs2_event_latin_core.html`.

### Rozhodnutia urobené samostatne
- `timeout_secs: 360` pre Fuchs2 (násobok min. 180 s, s rezervou na sieťovú latenciu GitHub Actions).
- Detekcia postponed/moved v `normalize.py` (spoločná normalizácia) — nie v adaptéri.
- ID generované z vyčisteného názvu (bez postponed prefixu) — konzistentnosť s budúcimi verziami akcie.

### Druhý beh — oprava API kľúča (commit c4bc2de)

Po prvom behu bolo zistené: `Illegal header value b'***'` — GitHub Secret `ANTHROPIC_API_KEY` bol uložený s trailing newline. httpx odmietol nevalidnú HTTP hlavičku. Oprava: `.strip()` pri čítaní kľúča v `classify_ai.py`.

### Výsledky z workflow_dispatch behu 2026-11-04 15:43 UTC (commit c4bc2de)

Príkaz použitý na čísla: čítané zo job summary (site/events.json nie je v repozitári).

**Celkovo:** 305 akcií (archa-plus 63, bike-jesus 33, citarna-unijazz 15, cross-club 15, forum-karlin 29, fuchs2 22, kasarna-karlin 2, meetfactory 43, palac-akropolis 83).

**Formáty po vrstve 2:**

| Format | Count |
|---|---|
| comedy | 1 |
| dance | 10 |
| dj | 43 |
| film | 1 |
| live | 165 |
| music | 19 |
| opening | 2 |
| other | 3 |
| quiz | 1 |
| talk | 6 |
| theatre | 60 |
| workshop | 4 |

**Metódy klasifikácie:** keyword 60, llm 167, source 78.

**AI layer:** 9 volaní, 0 chýb, 25 977 vstupných tokenov, 6 274 výstupných tokenov, **$0.0057**.

### Čo ostáva otvorené
- Zadanie 2 (web search) presunuté do úlohy 018.
- `docs/review/classification-2026-11-04.md` vytvorený nižšie.
