# 056: Pravidlá typu akcie podľa Matejových označení, podtyp `performance`, presnosť AI

## Zadanie

**Robí sa po 054** (nadväzuje na AI s hľadaním z 054). **Schválené Matejom 2026-11-17** vrátane zmien nižšie.

**Čítaj:** `docs/tasks/056/labels-matej.csv` (50 akcií, `expected_primary` = Matejov hlavný typ, `expected_secondary`, `note` = jeho zdôvodnenie – **prečítaj všetky poznámky**); `docs/data-model.md` riadok `formats`; prompt v `pipeline/classify_ai.py` a v AI doplnení z 054; `apply_commercial_clubs()` v `pipeline/classify.py`; `web/src/core/eventType.ts`; `web/src/i18n/*` (štítok `talk`).

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`.

### 1. Zmena dohody o zdrojoch (decisions.md)
AI pri hľadaní **smie čítať verejné stránky udalostí na Facebooku** (veľa podnikov, napr. Bike Jesus, má popisy a program primárne tam). Pipeline z Facebooku sama nič nesťahuje (žiadny scraping, žiadne API); hodnota z Facebooku sa uloží len so `source_url`. **Instagram ostáva mimo** (rozhodnutie 2026-11-02 platí). Zapíš ako nový riadok, ktorý čiastočne nahrádza pravidlo o zdrojoch.

### 2. Pravidlá do promptu (typ a hlavný typ)
Doslova podľa Matejových označení:
1. **Jeden hlavný typ** (`primary_format`) na akciu; ďalší formát len ako doplnkový (ostáva vo `formats`).
2. **Postup:** určiť **každého interpreta zvlášť** a zistiť, **ako sa prezentuje** (bio: „DJ/producer“ vs. kapela/živý projekt/spevák) – web podniku, Facebook udalosť, stránky interpreta, Spotify; nie podľa názvu akcie.
3. **Štruktúra programu:** časový harmonogram kapiel („20:00 X, 21:00 Y“) → `concert`; veľa mien oddelených ☆/+, noc do rána, prezentácia ako DJ-i → `dj`.
4. **Elektronický interpret naživo** (live set, „LIVE“/„(live)“ pri hlavnom interpretovi, živá kapela, spev, nástroje, „namiesto DJ setov živá kapela“) → `concert` (Bonobo, Tinlicker, Modeselektor LIVE, Amphibian Quadrophonic Soundsystem, CREDIT 00 (live), Asta Hiroki + Fthmlss + Catch92).
5. **Žánrová klubová noc bez headlinera** s viacerými DJ/live sety → `dj` (DRUMSTATION). Označenie „party“ od podniku sa nepreberá.
6. **Spevák/kapela a po nich DJ** → `concert`, `dj` doplnkový.
7. **Sound system** (napr. Bashment) → `dj`.
8. **Hudobný workshop** (aj o DJ-ovaní/produkcii) → `workshop`.
9. **Krst knihy s čítaním**, večer piesní + poézie + prózy → `talk` (hudba len doplnok).
10. **Komerčný klub (`commercial_club`):** generická noc bez menovaného DJ-a → `party`; **známy menovaný DJ ako headliner** (napr. SLVL v EPIC) → `primary_format: dj`, `party` doplnkový. Uprav `apply_commercial_clubs()` (party sa pridá vždy, `primary_format` určí AI podľa tohto pravidla).
- Do promptu daj 8–12 Matejových príkladov s krátkym zdôvodnením (vyber pestro z CSV, najmä sporné: Amphibian, Tinlicker, Modeselektor, CREDIT 00, DRUMSTATION, Family Therapy, SLVL, Student Wednesday, Bashment, Set and Play, Kavárna křest, High Speed Fairytales). **Tie isté akcie potom v meraní vyznač** (meranie na nich je skreslené).

### 3. Nový podtyp kultúry `performance`
- `formats` + `data-model.md`: `performance` (performance, performatívne umenie, živé pásmo na pomedzí divadla a výtvarného umenia). Typ kultúra, ikona masky (ako `culture`). i18n štítok: SK „performance“, CZ „performance“, EN „performance“.
- Štítok `talk` premenuj v appke: SK „čítanie a diskusia“, CZ „čtení a diskuse“, EN „talk & reading“ (kód `talk` ostáva).

### 4. Meranie presnosti
- Spusti klasifikáciu (s hľadaním, poskytovateľ z 054) na 50 akciách z CSV. Porovnaj `primary_format` s `expected_primary` a doplnkový s `expected_secondary`.
- Report: tabuľka akcia → očakávané → AI → zdroj (URL) → OK/chyba; presnosť spolu a **zvlášť bez akcií použitých ako príklady v prompte**; pri každej chybe prečo (čo AI našla). Cena merania.
- Ak presnosť bez príkladov < 85 %, navrhni úpravu pravidiel (nezavádzaj), Matej rozhodne.

## Overenie
- `pytest -q`, `npm test` (`--reporter=dot`), build OK; denný beh po zmene: počty typov pred/po s príkazom (`site/events.json`), zoznam zmien typu.
