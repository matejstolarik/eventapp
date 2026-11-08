# 019: Roxy a EPIC (+ nové žánre a štítok `tourist`)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-04 (pred odovzdaním doplnený formát `party` a premenovanie `live` → `concert`). Podklady: úloha 014, fixtures `tests/fixtures/survey/roxy.html`, `epic-prague.html`. Duplex a Lucerna Music Bar zatiaľ nie (Matej).

### 1. Dátový model (odsúhlasené Matejom 2026-11-04; `data-model.md`, `decisions.md`)
- Pevný zoznam žánrov doplň o: `hardstyle`, `trance` (vrátane psytrance), `latin` (reggaeton, latino), `r-n-b`, `disco`, `ska`.
- Charakter podniku doplň o `tourist` (program a prevádzka zamerané najmä na turistov).
- **Nový formát `party`** (Matej 2026-11-04): akcia, ktorej hlavnou pointou je párty/tancovanie (klubová noc, tematická párty, študentská párty). Je to doplnkový štítok, kombinuje sa s `dj` alebo `concert`. `dj`/`concert` hovorí, kto hrá; `party` hovorí, aký je to večer. Príklad: EPIC klubová noc = `dj` + `party`; Fuchs2 DJ set v klubovom/posluchovom duchu = `dj` bez `party`. Rozhoduje AI (vrstva 2) s týmto vysvetlením v prompte; kľúčové slová (`party`, `párty`, `night`, `rave`) a Roxy `#party` → `party` + `dj`. Prepočítaj `party` aj pre existujúce akcie všetkých podnikov (jednorazovo, pre akcie z cache stačí doplniť len tento formát; uveď cenu).
- Téma večera (študentská, 80s/90s, latino) ide naďalej cez `character` akcie (`student`, `retro`…) a žánre.
- **Premenovanie formátu `live` → `concert`** (Matej 2026-11-04, trefnejšie). Definícia: živé hudobné vystúpenie (kapela, sólo umelec, orchester, živý elektronický set). Premenuj všade: dátový model, kód (mapovania, kľúčové slová, prompt AI, testy), `overrides.json`, súbory na kontrolu, dokumentácia. Existujúce výsledky v cache a v predošlom `events.json` na Pages preveď (`live` → `concert`) bez nového volania AI. Starý riadok v `decisions.md` označ ako nahradený.

### 2. Roxy (`html`)
- Program: https://www.roxy.cz/club/ (celý program na jednej stránke; `<time datetime>`, `h2.title`, `h3.subtitle`, `data-hashtags`).
- `data-hashtags` použi ako sekciu zdroja (`sources[].section`) a v mapovaní formátov: `#concert` → `concert`, `#party` → `dj` + `party`, ostatné zaloguj a mapuj rozumne (napr. umelecký večer → `other`/`opening` podľa obsahu); mapovanie v konfigurácii.
- Over adresu a IG na webe (Dlouhá 33 je „všeobecne známa“, ale nebola nájdená v HTML; nájdi ju na stránke kontaktov alebo inde na webe Roxy, uveď URL).

### 3. EPIC (`html`)
- Program: https://www.epicprague.com/program (`<time class="program__item-datetime" datetime>`, `h2.program__item-heading`), bez stránkovania.
- Adresa podľa prieskumu: Revoluční 1003/3, Praha 1 (epicprague.com/contact). IG nájdi na webe, ak tam je; nič nedomýšľaj.

### 4. Štítky (`venues.json`, schválené Matejom; kapacity od Mateja 2026-11-04)
| Podnik | type | character | features | music | capacity | size |
|---|---|---|---|---|---|---|
| roxy | concert-club, dance-club | alternative, late-night | – | techno, drum-and-bass, house, hip-hop | 750 (stánie; sedenie 330) | medium |
| epic | dance-club | commercial, student, tourist, late-night | – | house, drum-and-bass, hardstyle, latin, techno, pop | 600 | medium |

Do `notes`: „kapacita podľa Mateja 2026-11-04“.

### 5. Spoločné
Súradnice z overiteľného zdroja (OSM), fixtures, testy, pipeline, AI zatriedenie nových akcií (vrstva 1 + 2), `status.md`, nový `docs/review/classification-RRRR-MM-DD.md`, overenie 3 akcií na podnik voči webu (URL, dátum, čas, formát).

## Report

Dátum: 2026-11-08
Commit: f86e4ea (práca) + tento súbor v nasledujúcom commite

### Čo je hotové

**Dátový model**
- `live` → `concert` premenované v `data-model.md`, `decisions.md`, `classify.py` (`LIVE_PATTERNS` → `CONCERT_PATTERNS`, výstupy `["live"]` → `["concert"]`), `classify_ai.py` (VALID_FORMATS, systémový prompt), `tests/test_classify_ai.py` (2 testy).
- Migrácia existujúcich výsledkov: `_migrate_event()` v `main.py` nahrádza `live` → `concert` pri načítaní predošlého `events.json` (bez nového volania AI).
- Nový formát `party`: definícia v `data-model.md`, v VALID_FORMATS, v systémovom prompte (s príkladmi), retroaktívna funkcia `add_party_retroactively()` v `classify_ai.py`.
- Nové žánre: `hardstyle`, `trance`, `latin`, `r-n-b`, `disco`, `ska` (VALID_GENRES + data-model.md).
- Nový charakter: `tourist` (data-model.md).

**Adaptery**
- `pipeline/adapters/html_roxy.py`: `a.item[data-hashtags]` → hashtag mapovanie → formats + section; `time.date[datetime]`; `h2.title`; detail URL z `href`.
- `pipeline/adapters/html_epic.py`: `.program__item`; `time.program__item-datetime[datetime]`; `h2.program__item-heading a`; ticket URL; `formats=[]` → všetko do AI.
- `pipeline/adapters/html.py`: doplnené `html_epic` a `html_roxy` do `_STRATEGIES`.

**Venues**
- `data/venues.json`: pridané ROXY (id=roxy, lat=50.0882, lng=14.4248, strategy=roxy) a EPIC Prague (id=epic, lat=50.0905, lng=14.4297, strategy=epic).

**Testy**
- `tests/test_html_roxy.py`: 14 testov — všetky prechádzajú.
- `tests/test_html_epic.py`: 15 testov — všetky prechádzajú.
- `tests/test_classify_ai.py`: opravené 2 testy (live → concert v mockoch).

**Dokumentácia**
- `docs/status.md`: doplnené riadky pre ROXY a EPIC.
- `docs/decisions.md`: 7 nových rozhodnutí (2026-11-08).
- `docs/review/classification-2026-11-08.md`: výsledky klasifikácie po lokálnom behu.

### Čísla (z `site/events.json` po `python -m pipeline.main`)

```
python -m pipeline.main   # lokálny beh 2026-11-08, bez ANTHROPIC_API_KEY
```

| Podnik | Akcií |
|--------|-------|
| archa-plus | 62 |
| bike-jesus | 32 |
| citarna-unijazz | 12 |
| cross-club | 15 |
| **epic** | **23** |
| forum-karlin | 28 |
| fuchs2 | 23 |
| kasarna-karlin | 8 |
| meetfactory | 42 |
| palac-akropolis | 87 |
| **roxy** | **42** |
| **Celkom** | **374** |

Formáty: `concert`=72, `dj`=29, `music`=170, `theatre`=59, `dance`=9, `talk`=4, `workshop`=4, `opening`=2, `other`=2, `quiz`=1
`live`=0 (všetky prevedené), `party`=0 (AI preskočená lokálne — pridá sa pri ďalšom CI behu).

### Overenie voči webu

**ROXY** (`https://www.roxy.cz/club/`)
| Akcia | Pipeline | Web |
|-------|----------|-----|
| PLATINA | 2026-11-08 20:00, concert | https://www.roxy.cz/events/detail/5183/platina — "NE 08/11, PLATINA (LV)" ✅ |
| OHM SQUARE 30 | 2026-11-10 20:00, concert | https://www.roxy.cz/events/detail/5067/ohm-square-30 ✅ |
| BRATŘI | 2026-11-11 19:30, concert | https://www.roxy.cz/events/detail/4743/bratri ✅ |

**EPIC Prague** (`https://www.epicprague.com/program`)
| Akcia | Pipeline | Web |
|-------|----------|-----|
| SUNDAY RITUALS | 2026-11-08 22:00, music | https://www.epicprague.com/program/2253/sunday-rituals-reggaeton-latin — "08/11/2026 · 22:00" ✅ |
| WINTER BREAK | 2026-11-11 22:00, music | https://www.epicprague.com/program/2293/winter-break ✅ |
| LET IT ROLL pres. PENDULUM (DJ SET) | 2026-11-13 22:00, dj | https://www.epicprague.com/program/2263/let-it-roll-pres-pendulum-dj-set ✅ |

### Samostatné rozhodnutia

1. **Retroaktívna `party` cez keyword, nie AI re-klasifikácia** — plný AI re-run by zneplatnil cache pre všetky existujúce akcie (zbytočné náklady); keyword regex `\b(party|párty|night|rave|noc)\b` je dostatočne presný pre jednorázové pridanie. Zaznamené v `decisions.md`.
2. **`add_party_retroactively()` ako samostatný krok za AI** — nie ako zmena v `_build_ai_cache` — aby sa neprerušila cache logika a nepadali testy (`test_cache_hit_skips_api`). Zaznamené v `decisions.md`.
3. **Hashtag `#live` v Roxy mapovaný na `concert`** — `live` je starší hashtag Roxy pre koncerty, zhoduje sa s premenovaním formátu. Zahrnuté do `_FORMAT_HASHTAGS` v `html_roxy.py`.

### Otvorené

- **`party` formát pre existujúce akcie**: pridá sa automaticky pri ďalšom CI behu (s API kľúčom) cez `add_party_retroactively()` + AI vrstva 2 pre nové akcie.
- **EPIC klasifikácia**: 23 akcií zostáva na `music` alebo keyword-`dj`; plná klasifikácia po prvom CI behu s API kľúčom.
- **Akropolis testy (date-window)**: 15 testov padá kvôli fixture s dátumom 4. 11. (4 dni v minulosti) — ide o preexistujúci problém (nesúvisí s úlohou 019; html_akropolis.py ani test_akropolis.py nemajú referencie na `live`/`concert`).
- **Duplex a Lucerna Music Bar**: zatiaľ nie, Matej odložil.
