# 053: Pravidlá párty / DJ / koncert, komerčné kluby, kolo označovania s Matejom

## Zadanie

**Robí sa po 052** (rovnaký kód `classify_ai.py`). **Schválené Matejom 2026-11-17** vrátane zmien dátového modelu nižšie.

**Čítaj:** `docs/data-model.md` – riadok s `formats` (`grep -n "formats" docs/data-model.md`) a pravidlo „Typ akcie pre farbu a ikonu“ v `docs/design.md` časť 1; `docs/decisions.md` – `grep -n "party\|classify" docs/decisions.md`; kód `pipeline/classify.py`, `pipeline/classify_ai.py` (prompt), `web/src/core/eventType.ts` (`eventType`, poradie typov).

Každá časť vlastný commit. Rozhodnutia zapíš do `docs/decisions.md`.

### 1. Nové definície (data-model.md + prompt AI)
- **`party`:** veľká komerčná/mainstreamová párty, kam ľudia idú kvôli atmosfére, nie kvôli konkrétnej hudbe či interpretovi (komerčné kluby, Erasmus/študentské, hity 80./90., open bar, mainstreamové tematické večery). Klubová noc zameraná na hudbu/DJ-ov je `dj`, nie `party`. Mimo komerčných klubov len pri jasnom signáli; AI uvedie dôvod (krátky text v `classification`).
- **`concert` vs. `dj`:** rozhoduje **hlavný interpret**. Koncert s DJ afterparty = `concert` (afterparty môže ostať ako druhý formát, ale typ akcie je koncert). Klubová noc s kapelami aj DJ-mi, kde hlavný interpret nie je jasný → `dj`. Rap/hip-hop naživo = `concert`. DJ set hudobníka = `dj`. Jam session, open mic = `concert` (dočasne, viď časť 4).
- **Elektronický live set:** zatiaľ **bez pevného pravidla** – rozhodne sa podľa kola označovania (časť 3). Do vtedy ponechaj dnešné správanie.

### 2. Typ akcie podľa hlavnej časti + komerčné kluby
- `eventType` (web) a rovnaké pravidlo v pipeline, ak existuje: dnes poradie `party` → `dj` → `concert`. Zmeň tak, aby pri akcii s `concert` aj `dj` rozhodol **hlavný interpret**: AI vráti aj `primary_format` (`concert` | `dj` | `party` | …); `eventType` ho použije, ak existuje, inak dnešné poradie. Pole `primary_format` doplň do `data-model.md`.
- **Nové pole podniku `commercial_club: true`** vo `venues.json` + `data-model.md`. V takom podniku je **každá** hudobná akcia `party` (pravidlo vo vrstve 1, bez AI). Nastav pre `epic`.
- Testy (web aj pytest).

### 3. Kolo označovania s Matejom
- Exportuj **50 hudobných akcií** z aktuálnych dát do `docs/tasks/053/labels.csv`: stĺpce `id`, `venue`, `date`, `title`, `url`, `current_formats`, `ai_reason` (ak je), prázdny `matej` (Matej vyplní `party` / `dj` / `concert`) a prázdny `note`.
- Výber: rôzne podniky (Cross Club, Fuchs2, Bike Jesus, Roxy, EPIC, Akropolis, Forum Karlín, Archa+, MeetFactory), aspoň **15 akcií s elektronickým live setom** alebo sporných medzi `dj` a `concert`, aspoň 10 dnes označených `party` mimo EPIC.
- Po vyplnení (ďalšia úloha) sa z neho spravia príklady do promptu a zmeria sa presnosť. **V tejto úlohe len export** a v reporte zoznam, ako je výber rozložený.

### 4. Počty zriedkavých typov
Spočítaj v aktuálnych dátach (a ak sa dá, v histórii) akcie, ktoré sú jam session, open mic, karaoke (podľa názvu/popisu, aj CZ: „jam“, „open mic“, „karaoke“, „otevřené pódium“). Počty a príklady (názov, podnik, dátum, URL) do reportu. Podľa toho Matej rozhodne o samostatných kategóriách s vlastnými ikonami. **Nič nové nezavádzaj.**

## Overenie
- `pytest -q`, `npm test` (`--reporter=dot`), build OK.
- Denný beh po zmene (ručne): počty akcií podľa typu pred a po (`party`, `dj`, `concert`) z `site/events.json` s príkazom; zoznam akcií, ktoré zmenili typ (aspoň 20 riadkov: názov, podnik, pred → po).
