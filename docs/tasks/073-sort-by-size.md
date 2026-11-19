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

### 3. Najviac 4 štítky bez rozplynutia aj na karte na mape a v programe podniku
- Matej 01:27 („jo“ na otázku zo 072): pravidlo z 072 pre riadok Akcií (najviac 4 pilulky vrátane ikony typu, bez rozplynutia, nezmestený štítok sa nezobrazí) platí aj na **karte na mape** a v **programe podniku**. Použi to isté riešenie ako v 072 (`BadgeTagRow` alebo jeho logiku); vzhľad štítkov v programe podniku (farby, veľkosť) bez zmeny.

### 4. Pipeline
- Úloha mení dáta (`venues.json`) → podľa `CLAUDE.md` **jeden beh na konci**, raz počkaj. Over v publikovanom `events.json`, že `forum-karlin` má 3000 a `kasarna-karlin` 300.

## Overenie a report
- `npm test` (test zoradenia: rôzne kapacity, rovnaká kapacita → čas, `null` na konci), `npm run build`, `pytest -q`; číslo behu a nasadenia.
- Snímky JPEG 390 × 844 do `docs/tasks/073/`: `akcie-velkost.jpg` (obdobie Najbližších 7 dní, zoradenie veľkosť), `zoradit-ponuka.jpg` (otvorená ponuka s tromi položkami), `mapa-karta.jpg`, `program-podniku.jpg`.
- Report: zmenené kapacity so zdrojmi, čo sa našlo na oficiálnych weboch, otvorené body.
