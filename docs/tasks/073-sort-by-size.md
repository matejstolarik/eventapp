# 073: Zoradenie akcií podľa veľkosti podniku

## Zadanie

**Schválené Matejom 2026-11-19 01:19** („veľkosť it is“). **Záväzné:** nič nevymýšľaj, drž štýl appky; mení sa **len** to, čo je nižšie. Čo nie je jasné, spýtaj sa.

**Čítaj:** `docs/venue-capacity.md` (prieskum kapacít so zdrojmi); `docs/design.md` časť 4 (odsek **Zoradenie** a bloky „Zmena 2026-11-19“); `docs/data-model.md` riadok `capacity`; `data/venues.json` (`capacity`, `notes`); v kóde zoradenie v `web/src/pages/EventsPage.tsx` (`grep -n -i sort`), `web/src/core/types.ts` (`capacity`), `web/src/i18n/*.ts`.

Kontext: pole `capacity` už existuje (úlohy 013, 019; „len overené číslo“) a appka ho má v type `Venue`. Nové pole netreba.

### 1. Kapacity vo `venues.json` (dáta)
- `forum-karlin`: **3800 → 3000**. Do `notes` zdroj: prague.eu/cs/objevujte/forum-karlin/ („s kapacitou až 3000 osob“) a vyjadrenie prevádzkovateľa Bestsport (prazsky.denik.cz, „kapacitou asi 3000 osob“); 3800 bolo z Cvent (sekundárny zdroj).
- `kasarna-karlin`: **null → 300** (Garáže, 300 stánie / 150 sedenie; zdroj: projekt Kasárna Karlín pre MHMP na eud-vis.praha.eu – presný odkaz je v `docs/venue-capacity.md`). Do `notes`: „najväčší vnútorný priestor so zdrojom; dvor bez čísla“.
- `cross-club`: kapacita ostáva 250, do `notes` doplň „kapacita podľa Mateja (úloha 013), bez zdroja“.
- Ostatné bez zmeny. `citarna-unijazz` ostáva `null`. **Žiadne odhady.**
- Ak pri tom na **oficiálnom webe** podniku s `null` (Unijazz) alebo bez zdroja (Cross Club, EPIC) nájdeš kapacitu jedným-dvomi požiadavkami, zapíš ju so zdrojom a uveď v reporte. Inak nič.

### 2. Zoradenie „Veľkosť“ v Akciách
- V ponuke **Zoradiť** pribudne tretia položka **veľkosť** (cs **velikost**, en **size**), za „vzdialenosť“. **Presne ako ostatné zoradenia** (Matej 01:27): malé písmená ako `dátum`/`čas`/`vzdialenosť`, nový kľúč `sortSize` vedľa `sortDate`/`sortTime`/`sortDistance` v `i18n/*.ts`, rovnaký vzhľad položky, v riadku pod lištou „Zoradiť: veľkosť ▾“, ťuk zavrie ponuku, Späť ju zatvorí. Žiadny nový prvok, ikona ani vysvetlivka.
- Poradie: `capacity` podniku **zostupne**; pri rovnakej kapacite podľa dátumu a času začiatku (ako zoradenie podľa času); podniky s `capacity = null` **na konci**, medzi sebou podľa času.
- Bez nadpisov a bez zobrazenia čísla kapacity v riadku. Voľba sa pamätá ako ostatné zoradenia.

### 3. ~~Najviac 4 štítky bez rozplynutia aj na karte na mape a v programe podniku~~
> **ZRUŠENÉ – NEROBIŤ (Matej 2026-11-19 01:29).** Hlavný chat si zle vyložil Matejovo „jo“. Karta na mape a program podniku ostávajú bez zmeny.

- Matej 01:27 („jo“ na otázku zo 072): pravidlo z 072 pre riadok Akcií (najviac 4 pilulky vrátane ikony typu, bez rozplynutia, nezmestený štítok sa nezobrazí) platí aj na **karte na mape** a v **programe podniku**. Použi to isté riešenie ako v 072 (`BadgeTagRow` alebo jeho logiku); vzhľad štítkov v programe podniku (farby, veľkosť) bez zmeny.

### 4. Pipeline
- Úloha mení dáta (`venues.json`) → podľa `CLAUDE.md` **jeden beh na konci**, raz počkaj. Over v publikovanom `events.json`, že `forum-karlin` má 3000 a `kasarna-karlin` 300.

## Overenie a report
- `npm test` (test zoradenia: rôzne kapacity, rovnaká kapacita → čas, `null` na konci), `npm run build`, `pytest -q`; číslo behu a nasadenia.
- Snímky JPEG 390 × 844 do `docs/tasks/073/`: `akcie-velkost.jpg` (obdobie Najbližších 7 dní, zoradenie veľkosť), `zoradit-ponuka.jpg` (otvorená ponuka s tromi položkami).
- Report: zmenené kapacity so zdrojmi, čo sa našlo na oficiálnych weboch, otvorené body.

## Report

**Dátum:** 2026-11-19. **Commity:** `82a0c66` (zoradenie, kapacity, docs), report v nasledujúcom commite.

**Hotovo**
- **Zoradenie „veľkosť“** (cs `velikost`, en `size`, kľúč `sortSize` v `web/src/i18n/*.ts`): tretia položka v ponuke Zoradiť za vzdialenosťou, rovnaký vzhľad aj správanie (ťuk zavrie, Späť zavrie, riadok „Zoradiť: veľkosť ▾“). `sortEvents` v `web/src/core/period.ts` má mód `size`: `capacity` zostupne → pri zhode dátum a čas (`compareDatetime`) → `null` a neznámy podnik na konci podľa času. Kapacita sa v riadku nezobrazuje. Bez nadpisov.
- **Kapacity vo `data/venues.json`** (číslo + zdroj v `notes`):
  - `forum-karlin` 3800 → **3000** (prague.eu/cs/objevujte/forum-karlin/; Bestsport cez prazsky.denik.cz; 3800 bolo z Cvent).
  - `kasarna-karlin` null → **300** (Garáže, 300 stánie / 150 sedenie, projekt Kasárna Karlín pre MHMP na eud-vis.praha.eu; najväčší vnútorný priestor so zdrojom, dvor bez čísla).
  - `cross-club` 250 bez zmeny, `notes`: „Kapacita podľa Mateja (úloha 013), bez zdroja.“
  - `citarna-unijazz` null → **70** – nájdené na oficiálnom webe (pozri nižšie).
- Testy: 3 nové v `web/src/core/period.test.ts` (rôzne kapacity, rovnaká kapacita → čas, `null`/neznámy podnik na konci).
- `docs/decisions.md` (nový riadok 073), `docs/venue-capacity.md` (riadok Unijazz).

**Rozhodnuté samostatne**
- Veľkosť je v ponuke **pri každom období** (zadanie neobmedzuje ako pri vzdialenosti).
- „Pamätá sa ako ostatné zoradenia“: ostatné zoradenia sa dnes držia v stave stránky (`useState`), nie v `localStorage` – veľkosť rovnako, nič nové.
- Unijazz 70: oficiálny web podniku, podľa bodu 1 zadania zapísané so zdrojom.

**Oficiálne weby (po 2 požiadavkách)**
- Čítárna Unijazz: https://citarna.unijazz.cz/pronajem-prostor/ – „sál s barem pro cca 70 lidí“ (salonek 10–15) → **70**.
- Cross Club: https://www.crossclub.cz, https://www.crossclub.cz/cs/kontakt/ – kapacita neuvedená → bez zmeny.
- EPIC: https://www.epicprague.com, https://www.epicprague.com/o-klubu – len „Plocha 2 500 m2 … na třech patrech“, kapacita neuvedená → 600 bez zmeny.

**Overenie**
- `npx vitest run --reporter=dot`: 14 súborov, 208 testov OK. `npm run build` OK. `python -m pytest -q`: 642 passed.
- Pipeline `daily.yml` beh **44430061971** – success (zostavil aj appku). `deploy-app.yml` po pushi beh 44430060283 – success.
- Publikovaný `events.json` (generated_at 2026-11-19T01:42:54+01:00): forum-karlin 3000, kasarna-karlin 300, citarna-unijazz 70; žiadny podnik nemá `capacity = null`.

**Čísla** (z publikovaného `events.json` posledného behu; príkaz: `curl -s https://matejstolarik.github.io/eventapp/events.json -o site_pub.json` a Python: akcie `status == scheduled`, `2026-11-19 <= date <= 2026-11-25`, počet podľa `venue_id`, zoradené podľa `capacity`):
- 372 akcií celkom, 56 v Najbližších 7 dňoch. Poradie pri „veľkosť“: Forum Karlín 3000 (1), Archa+ 1200 (6), MeetFactory 750 (5), ROXY 750 (5), Akropolis 700 (8), Fuchs2 650 (2), EPIC 600 (5), Kasárna Karlín 300 (6), Bike Jesus 280 (7), Cross Club 250 (8), Čítárna Unijazz 70 (3).

**Snímky** (`tests/playwright/screenshots-073.spec.ts`, dáta z Pages, čas 19. 11. 17:00, obdobie 7 dní, spustené z `web/` s `NODE_PATH=web/node_modules`) → `docs/tasks/073/`: `zoradit-ponuka.jpg`, `akcie-velkost.jpg`. Snímky som neposudzoval.

**Otvorené**
- Pre Kasárna Karlín zadanie odkazuje na „presný odkaz v `docs/venue-capacity.md`“, ale ten dokument uvádza len „eud-vis.praha.eu (Podrobný popis projektu Kasárna Karlín)“ bez plnej URL – v `notes` je rovnaký opis, URL som nevymýšľal.
- Cross Club a EPIC ostávajú bez oficiálneho zdroja kapacity.
- Bod 3 zrušený Matejom – nerobené.
