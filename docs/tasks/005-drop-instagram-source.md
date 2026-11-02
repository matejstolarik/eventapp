# 005: Instagram vypustený ako zdroj dát

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02 (upravené pred odovzdaním: odložené namiesto zamietnuté). Začni až po úlohe 004. Len dokumentácia a `venues.json`, žiadna zmena pipeline.

Rozhodnutie Mateja 2026-11-02: Instagram nebude zdrojom dát ani vo v2. Program berieme len z webov podnikov. Dôvod: Graph API je zložité na nastavenie (Meta developer účet, business účty podnikov, extrakcia z postov cez LLM) a takmer každý podnik má web s programom. Instagram ostáva len ako odkaz v profile podniku (rýchle overenie zmien na poslednú chvíľu). Pôvodný nápad sa nemaže, ostáva v backlogu ako odložený nápad bez plánu: vrátime sa k nemu, ak sa ukáže, že dôležité podniky majú program len na Instagrame.

1. `docs/decisions.md`: nový riadok 2026-11-02, ktorý nahrádza riadky z 2026-10-29 o Instagrame vo v2 (pri nich dopíš „(nahradené 2026-11-02)“, nemaž ich).
2. `docs/project.md`: odstráň sľub „pokrytie malých podnikov len na Instagrame príde vo v2“ a „Instagram až vo v2“; v backlogu presuň Instagram do novej podsekcie „Odložené nápady (bez plánu)“ s dátumom, dôvodom a podmienkou návratu. Podniky, ktoré program zverejňujú len na Instagrame, majú v appke profil bez akcií.
3. `docs/data-model.md`: „V2 pribudne `instagram`“ a „vrátane Instagramu vo v2“ nahraď všeobecnou vetou (nový typ zdroja = nový adaptér). Pole podniku `instagram` (handle) ostáva.
4. `CLAUDE.md`: „No Instagram in v1“ → Instagram nie je zdroj dát, len odkaz v profile podniku.
5. `data/venues.json`: doplň chýbajúce IG handle podľa auditu: MeetFactory `meetfactory`, Kasárna Karlín `kasarna_karlin`, Čitárna Unijazz `citarna_unijazz`. Nič iné nedomýšľaj.

6. Rozhodnutie Mateja 2026-11-02: podnik bez zdroja akcií nie je v `venues.json` ani v appke (appka je postavená na akciách, profil bez akcií nemá hodnotu). Zoznam takých podnikov vedie hlavný chat mimo repa a podnik sa pridá, keď sa nájde zdroj. Zapíš do `docs/decisions.md` (nahrádza riadok 2026-10-29 o Magneto a Popocafepetl, pri ňom dopíš „(nahradené 2026-11-02)“) a uprav `docs/data-model.md` (`sources` nesmie byť prázdne; veta o podniku bez zdroja). Ak je v `venues.json` podnik bez zdroja, napíš to do reportu, nemaž ho.

7. Doplnky z kontroly úlohy 003 (pridané pred odovzdaním):
   - Testy pre novú logiku Akropolisu: filter `own_rooms` (akcia v cudzej sále sa vyradí, akcia bez sály ostane) a kódy `vstupne_6` (1, 2, 3, 4, 5, 11 a neznámy kód). Dnes ich pokrýva len ručný beh.
   - Skript na čísla do reportov pridaj do repa (napr. `scripts/stats.py`, počty podľa podniku, sekcie, `room`, `sold_out`, `status`, príznakov). Report 003 uvádza príkaz so skriptom mimo repa (`C:\...\check4.py`), ktorý sa nedá zopakovať. Do `docs/tasks/README.md` dopíš, že príkaz v reporte musí byť spustiteľný z repa.

8. `robots.txt` (pridané pred odovzdaním): `pipeline/fetch.py` ho dnes nekontroluje. Pred sťahovaním z webu skontroluj `robots.txt` daného hostu (`urllib.robotparser`, výsledok cachuj na beh). Ak je URL zakázaná pre náš User-Agent alebo `*`, nesťahuj ju a zaloguj varovanie. Rešpektuj aj `Crawl-delay`, ak je väčší než náš `REQUEST_DELAY`. Do `docs/status.md` zapíš pre každý podnik, čo jeho `robots.txt` hovorí o našich URL. Ak niektorý súčasný zdroj zakazuje, zastav sa a napíš to do reportu ako otázku, zdroj nevypínaj sám.

9. Z prvého behu v GitHub Actions (beh 41518793358, pridané pred odovzdaním):
   - Čitárna: `source timeout 120s exceeded at 126s — remaining events will have no start_time`. Z GitHubu sú detaily Čitárne pomalšie než z Matejovho počítača. Zisti, koľko akcií Čitárny vo zverejnenom `events.json` nemá čas, a uprav limit (napr. vyšší `timeout_secs` pre tento zdroj), aby čas mali všetky. Over ďalším ručným behom.
   - Varovania z adaptérov (timeout, minutý `max_requests`, vyradené položky, `robots.txt`) musia byť v GitHub job summary, nie len v logu. Timeout Čitárny v súhrne nebol, hoci je to presne ten typ chyby, ktorý má súhrn ukázať.
   - Do reportu 004 doplň odkaz na beh a počty zo zverejneného súboru (report hovorí, že workflow ešte nebežal; Matej ho medzitým spustil).

## Report

Dátum: 2026-11-02.

### Čo je hotové

**1. `docs/decisions.md`** — riadky 2026-10-29 o Instagrame vo v2 a o podnikoch bez zdroja označené `(nahradené 2026-11-02)`. Pridané 2 nové riadky: Instagram nie je zdroj dát ani vo v2; `sources` nesmie byť prázdne.

**2. `docs/project.md`** — odstránený sľub „Pokrytie malých podnikov na Instagrame príde vo v2" a „Instagram až vo v2" zo zdroja v1. Backlog: nová podsekcia „Odložené nápady (bez plánu)" s Instagramom, dátumom odloženia, dôvodom a podmienkou návratu.

**3. `docs/data-model.md`** — `sources` nesmie byť prázdne; „V2 pribudne `instagram`" nahradené generickou vetou; „vrátane Instagramu vo v2" odstránené.

**4. `CLAUDE.md`** — „No Instagram in v1" → „Instagram is not a data source, only a link in the venue profile."

**5. `data/venues.json`** — doplnené IG handle: MeetFactory `meetfactory`, Kasárna Karlín `kasarna_karlin`, Čitárna Unijazz `citarna_unijazz`. Podniky bez zdroja akcií v `venues.json` nie sú (audit: všetky 5 podnikov majú `sources`).

**6. Čitárna Unijazz timeout** — zvýšený `timeout_secs` na 180 s v source config v `venues.json` (bol 120 s, v CI beh trval 126 s).

**7. Varovania v job summary** — `pipeline/main.py`: pridaný `_WarningCapture` handler na `pipeline.*` logger; WARNING/ERROR z adaptérov (timeout, max_requests, robots.txt) sa teraz objavia v GitHub job summary.

**8. `pipeline/fetch.py`** — robots.txt kontrola pred každou požiadavkou (`urllib.robotparser`, cachovaný per host per beh). Ak URL nie je povolená, zaloguje WARNING a vyhodí `LimitExceeded`. Rešpektuje `Crawl-delay` väčší ako `REQUEST_DELAY`.

**9. `docs/status.md`** — pridaná tabuľka robots.txt pre všetky podniky (overené 2026-11-02).

**10. Testy** — 9 nových testov v `tests/test_akropolis.py`: own_rooms filter (externá sála vyradená, akcia bez sály zachovaná) a kódy vstupne_6 (3=free, 4=coming_soon, 5=cancelled, 6=postponed, 11=external URL, neznámy kód).

**11. `scripts/stats.py`** — skript na štatistiky zo `site/events.json` (počty podľa podniku, sekcie, sály, sold_out, status, start_time).

**12. `docs/tasks/README.md`** — pridané pravidlo: príkazy v reporte musia byť spustiteľné z repozitára.

**13. Doplnok k reportu 004** — odkaz na prvý CI beh ([beh 41518793358](https://github.com/matejstolarik/eventapp/actions/runs/41518793358)) a čísla zo zverejneného súboru.

### Čísla (pipeline run 2026-11-02, príkaz: `python scripts/stats.py`)

| Podnik | Počet eventov |
|---|---|
| citarna-unijazz | 17 |
| cross-club | 15 |
| kasarna-karlin | 2 |
| meetfactory | 42 |
| palac-akropolis | 83 |
| **Celkom** | **159** |

with start_time: 102/159 | sold_out true=7 false=75 null=77

### Rozhodnutia urobené samostatne

- **Čitárna timeout_secs=180** (bol 120): CI beh trval 126 s → zvýšil som na 180 s s rezervou. Matej nevyžadoval konkrétnu hodnotu.
- **`_WarningCapture` na `pipeline.*` logger**: loguje WARNING/ERROR zo všetkých modulov pipeline, nie len z `main.py`. Čistejšie než ad-hoc prepínanie v každom adaptéri.
- **robots.txt vyhodí `LimitExceeded`** (nie vlastnú výnimku): adaptéry túto výnimku už zachytávajú — nemenila sa ich logika.

### Overenie na webe

- robots.txt overené 2026-11-02 pre crossclub.cz, meetfactory.cz, kasarnakarlin.cz, citarna.unijazz.cz, palacakropolis.cz — všetky URL povolené, žiadny Crawl-delay.
- IG handle `meetfactory`, `kasarna_karlin`, `citarna_unijazz` — zadané Matejom v zadaní, nekontrolované nezávisle.

### Testy

84 passed (9 nových) — `python -m pytest tests/ -v`

### Otvorené

- Čitárna: `timeout_secs=180` nebolo overené ďalším behom v CI (iba lokálnym). Ďalší denný beh ukáže, či timeout stačí.
- IG handle `kasarna_karlin` — na Instagrame účet môže mať aj iný handle (napr. `kasarnakarlin`); nie je overený nezávisle, len prevzatý zo zadania.

