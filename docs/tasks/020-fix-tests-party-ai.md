# 020: Denný beh nefunguje od 5. 11. + `party` cez AI

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-08. **Urgentné.**

### 1. Denný beh padá 4 dni po sebe
Plánované behy 2026-11-05, 06, 07 a 08 (napr. 42475236384) skončili **failure** za ~20 s: testy padajú, workflow preto nič nezverejní. Zverejnené dáta sú zo 4. 11. Príčina: testy závisia od dnešného dátumu. Fixtures obsahujú akcie s pevnými dátumami a keď tie dátumy prejdú do minulosti, okno „od včera“ ich vyhodí (`test_akropolis.py` 15 testov, `test_archa.py`, `test_forum_karlin.py`, `test_jsonld.py`). Report 019 to označil ako „preexistujúci problém, nesúvisí“, ale je to dôvod, prečo pipeline 4 dni nebeží.
- Testy nesmú závisieť od skutočného dnešného dátumu: „dnes“ má byť v testoch pevný (parameter / injektovaný dátum alebo `freezegun`), pre všetky adaptéry a testy s oknom.
- Over, že celá sada prechádza aj pri simulovanom dátume o 1 a o 6 mesiacov neskôr.
- Zváž, či je správne, že padnutý test zastaví zverejnenie úplne. Navrhni a zdôvodni (napr. testy zastavia zverejnenie, ale musí o tom vedieť Matej; GitHub posiela e-mail pri zlyhaní plánovaného behu – over, komu a či je to zapnuté, a popíš to v `status.md`).

### 2. `party` pre existujúce akcie cez AI, nie kľúčové slová
V 019 sa `party` pre existujúce akcie doplnilo regexom `party|párty|night|rave|noc`. Matej chcel, aby o `party` rozhodovala AI (rozdiel EPIC klubová noc vs. Fuchs2 DJ set nie je v názve) a kvalita má prednosť pred cenou (ide o centy). Regex `night`/`noc` navyše trafí aj nehudobné akcie (napr. „Noc …“).
- Odstráň regexové dopĺňanie `party`. Kľúčové slová ostávajú len ako istá vrstva 1 pre jasné prípady (Roxy `#party`, `party`/`párty` v názve), nie `night`/`noc`.
- Jednorazovo nechaj AI posúdiť `party` pre všetky existujúce akcie (stačí otázka len na `party`, ostatné z cache; alebo celé prezatriedenie, ak je to jednoduchšie). Uveď cenu.

### 3. Overenie v CI
Po oprave spusti ručný beh workflow (`workflow_dispatch`) a over: testy prechádzajú, AI beží (cache hits aj nové akcie, `party`), dáta sa zverejnia. Odkaz na beh, počty podľa podniku a formátu zo zverejneného súboru, cena AI.
Nový `docs/review/classification-RRRR-MM-DD.md` zo **zverejneného** `events.json` (s AI), nie z lokálneho behu bez kľúča.

## Report
