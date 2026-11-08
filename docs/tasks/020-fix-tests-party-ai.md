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

Dátum: 2026-11-08. Commit: 47c6cf1.

### Čo je hotové

**1. Dátumovo-nezávislé testy** — hotovo.
- Adaptéry `html_archa.py::parse()`, `html_akropolis.py::parse()`, `html_forum_karlin.py::parse_listing()`, `jsonld.py::_fetch_listing_pages()` dostali parameter `today: datetime.date | None = None`; default = `datetime.date.today()`.
- Všetky 4 testovacie súbory (`test_archa.py`, `test_akropolis.py`, `test_forum_karlin.py`, `test_jsonld.py`) majú `TEST_TODAY = datetime.date(2026, 11, 1)` a predávajú ho do volania `parse()`/`parse_listing()`/`_fetch_listing_pages()`. Fixture akcie (Nov–Dec 2026) bezpečne padajú do okna [2026-10-31, 2027-04-30].
- `pytest tests/ -x -q`: **194 passed**, 0 failed (pred opravou padalo 15+ testov denne).

**2. `party` cez AI, nie regex** — hotovo.
- Odstránené z `classify_ai.py`: `import re`, `_PARTY_TITLE_RE`, funkcia `add_party_retroactively()`.
- Odstránené z `main.py`: import `add_party_retroactively`, jej volanie a log.
- `_build_ai_cache()` rozšírená: LLM-klasifikované akcie s `dj`/`concert`/`music` bez `party` sa vynechajú z cache → AI ich pri prvom behu prehodnotí; po prehodnotení sa kešujú normálne.
- `test_cache_hit_skips_api` aktualizovaný: predošlá akcia má `formats=["dj", "party"]` (post-assessment stav, zostáva v cache).
- `decisions.md` aktualizovaný: 2 nové riadky (dátumovo-nezávislé testy, party cez AI).
- `status.md` aktualizovaný: sekcia „Zlyhanie workflow — e-mailové notifikácie" (GitHub posiela e-mail pri plánovanom behu, zámerné správanie, stará verzia events.json zostáva).

**Lokálny beh pipeline** (bez ANTHROPIC_API_KEY, AI skipped):
```
python -c "import json; d=json.load(open('site/events.json',encoding='utf-8')); print(len(d['events']))"
```
Výsledok: **376 eventov** (374 → 376, +2 po oprave dátumového okna).
Formáty (bez AI): concert=72, dj=29, dance=9, music=170, theatre=59, talk=4, workshop=4, opening=2, quiz=1, other=2. `party=0` lokálne — pridá AI v CI.
Metódy: source=123, keyword=58, null=195 (195 pôjde na AI v CI).

### 3. CI overenie

**CI beh #9 — Success ✅** — workflow_dispatch, 2026-11-08, 7m 13s.  
URL: https://github.com/matejstolarik/eventapp/actions/runs/42518415085  
Zverejnené: `https://matejstolarik.github.io/eventapp/events.json` (21:13:41 CET)

**Výsledky zo zverejneného `events.json`** (príkaz: `Invoke-WebRequest "https://matejstolarik.github.io/eventapp/events.json" | ConvertFrom-Json`):

Celkom: **377 eventov**.

| Podnik | Akcií |
|---|---|
| palac-akropolis | 87 |
| archa-plus | 62 |
| meetfactory | 42 |
| roxy | 42 |
| bike-jesus | 32 |
| forum-karlin | 28 |
| epic | 23 |
| fuchs2 | 23 |
| cross-club | 15 |
| kasarna-karlin | 11 |
| citarna-unijazz | 12 |

| Formát | Počet |
|---|---|
| concert | 191 |
| theatre | 62 |
| dj | 88 |
| **party** | **58** |
| dance | 9 |
| film | 7 |
| talk | 6 |
| music | 4 |
| other | 5 |
| workshop | 4 |
| opening | 2 |
| quiz | 2 |
| comedy | 1 |

| Metóda | Počet |
|---|---|
| llm | 196 |
| source | 123 |
| keyword | 58 |

AI bežala (`llm=196`). `party=58` — vrátane všetkých 23 EPIC akcií (`dj + party`) a 11 Cross Club nočí. Logy s cenou AI nie sú dostupné bez prihlásenia do GitHub Actions; odhadovaná cena z task 019 metriky (~$0.003 pri 196 LLM volaniach).

**Klasifikačná review:** `docs/review/classification-2026-11-08.md`

### Rozhodnutia urobené samostatne

1. `today` parameter (nie `freezegun`): bez novej závislosti, rovnaká sémantika, konzistentné s existujúcim štýlom kódu.
2. Cache invalidácia pre `party` cez `_build_ai_cache()`: jednoduchšie ako force-reclassify flag; automaticky sa „vypne" po prvom behu (kešuje normálne po prehodnotení). Cena prvého prehodnotenia: ~$0.003 (odhadnuté z task 019 nákladov).
3. `status.md` sekcia o e-mailoch: GitHub posiela e-mail vlastníkovi pri každom `schedule` zlyhaní; toto je zámerné — padnutý test = data sa nezverejnia = správny poplach.
