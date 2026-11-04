# 013: Štítky podnikov, pevný zoznam žánrov a zatriedenie akcií (vrstva 1)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-04 (upravené pred odovzdaním: bez nových vlastností, rozlíšenie live/dj, kontrola Matejom). Podmienka pred PWA: bez formátov je predvolený pohľad (`live` + `dj`) prázdny a bez štítkov nefungujú filtre. Bez LLM (to je vrstva 2, neskôr).

### 1. Zmeny dátového modelu (odsúhlasené Matejom 2026-11-04; zapíš do `docs/data-model.md` a `docs/decisions.md`)
**character** (podnik), pridať: `queer-friendly`, `late-night`, `community`, `diy`, `art-space`, `english-friendly`, `cozy`, `hangout`, `family-friendly`. Definície:
- `queer-friendly`: doložený queer program alebo spolupráca (queer kolektívy, Prague Pride, queer debaty). Len s doloženým zdrojom (do `notes` podniku), nikdy jediný štítok charakteru; nezistené neznamená „nie je“. (`queer` ostáva pre podniky, ktoré sú queer ako také.)
- `late-night`: program bežne do rána; `community`: komunitne vedené; `diy`: svojpomocné, nezávislé; `art-space`: galéria/rezidencie popri hudbe; `english-friendly`: program výslovne prístupný v angličtine; `cozy`: komorný priestor; `hangout`: hlavne posedenie, akcie doplnok; `family-friendly`: aj pre deti.

**features**: bez zmeny (Matej: záhrada, voda, nádvorie nie sú vlastnosti, podľa ktorých sa filtruje).

**formats** akcie, pridať: `music` = hudobná akcia, pri ktorej sa nedá rozlíšiť `live` vs. `dj`. Predvolený pohľad v appke: `live` + `dj` + `music`. (Lepšie ako prázdne formáty alebo hádať live/dj.)

### 2. Štítky podnikov do `data/venues.json` (podľa Matejovho schválenia)
| Podnik | type | character | features | music | capacity | size |
|---|---|---|---|---|---|---|
| cross-club | (bez zmeny) concert-club, dance-club | alternative, underground, late-night | open-air (bez zmeny) | (bez zmeny) | 250 | small |
| fuchs2 | dance-club, concert-club | alternative, underground, queer-friendly, late-night | – | techno, electro, ebm, post-punk, indie | 650 | medium |
| bike-jesus | concert-club, dance-club, bar | underground, alternative, community, diy, queer-friendly | – | techno, house, post-punk, indie, shoegaze | 280 | small |
| palac-akropolis | concert-club, culture-center | alternative | – | indie, rock, world, jazz, punk | 700 | medium |
| archa-plus | culture-center, concert-hall | alternative, experimental, queer-friendly, english-friendly | – | indie, electronic, metal, experimental | 1200 | medium |
| meetfactory | culture-center, concert-club | alternative, experimental, art-space | – | indie, electronic, experimental, metal, hip-hop, jazz | 750 | medium |
| forum-karlin | concert-hall | commercial | – | rock, pop, metal, hip-hop, electronic | 3800 | large |
| citarna-unijazz | cafe, culture-center | alternative, experimental, community, cozy | – | jazz, experimental | null | small |
| kasarna-karlin | culture-center, bar, cinema | alternative, hangout, community, family-friendly | open-air, seasonal | indie | null | null |

Zdroje kapacít a `queer-friendly` zapíš do `notes` podniku:
- kapacita: Fuchs2 selection.cz/en/venues/fuchs2; Bike Jesus kdykam.com/en/venue/bike-jesus-praha-165; Akropolis liveurope.eu/palac-akropolis (700 veľký sál, 80 malý); Archa+ archatheatre.cz/en/spaces-and-technical.html (200–350 sedenie, do 1 200 stánie); MeetFactory meetfactory.cz/en/informace-pro-kapely; Forum Karlín Cvent (3 800 stánie, 1 800 sedenie).
- queer-friendly: Fuchs2 – séria FEMXCORE (easterndaze.net/?p=2082) a lokalita Prague Pride Festival (festival.praguepride.com/en/lokace/fuchs2-bike-jesus/); Bike Jesus – lokalita Prague Pride Festival (tá istá stránka); Archa+ – queer program na webe (debaty „Jste queer?“, „God Save the Drama Queen“).

### 3. Pevný zoznam žánrov (`docs/data-model.md`)
Zostav ho nad reálnymi dátami: zjednotenie `music` všetkých podnikov + žánre, ktoré zdroje samy uvádzajú (sekcie, tagy). Malé písmená, pomlčky, anglicky, cca 20–30 položiek, bez zbytočne jemného delenia. Ak niektorý hudobný štítok z tabuľky nesedí do zoznamu, namapuj ho a uveď v reporte. Zoznam je návrh na schválenie Matejom (uveď ho v reporte celý).

### 4. Zatriedenie akcií – vrstva 1 (deterministické, `pipeline/classify.py`)
Poradie pravidiel, každé len keď je isté; inak `formats` ostanú prázdne a `classification = null`:
1. **Sekcia/tag zo zdroja** → formát: napr. divadlo → `theatre`, film → `film`, kvíz → `quiz`, vernisáž → `opening`, hudba → `music`; tanec, debata, přednáška, workshop → `other`. Mapovanie pre každý zdroj zvlášť v konfigurácii, nie natvrdo v kóde.
2. **Kľúčové slová v názve a v zdroji** (zoznam v konfigurácii): napr. `live`, `/live`, `(live)`, `F2 LIVE`, `křest`, `support`, `tour`, `+ kapela` → `live`; `dj set`, `b2b`, `w/`, `residents`, `all night long`, `rave` → `dj`. Pri konflikte nič neprepisuj.
3. **Charakter podniku a sekcie** (konfigurácia pre každý podnik/sekciu, napr. Akropolis hudba, Forum Karlín, Archa+ hudba, MeetFactory hudba → zvyčajne `live`; Fuchs2 a Cross večerné akcie bez znakov koncertu → zvyčajne `dj`). Matej očakáva, že live vs. dj sa dá väčšinou určiť; cieľ je, aby `music` (nerozlíšené) bolo výnimkou. Pravidlá ber z toho, čo vidíš v programe (vzorce názvov, časy začiatku: koncerty zvyčajne 19–21 h, DJ noci od 22–23 h), a zdokumentuj ich.
4. **Inak `music`** (hudobná akcia, nerozlíšené), alebo prázdne, ak nie je isté ani to, že ide o hudbu.
- `classification = {"method": "source" | "keyword" | "venue", "confidence": ...}` podľa pravidla, ktoré rozhodlo.
- Žánre akcií (`genres`) v tejto vrstve **nevypĺňaj** (z podniku sa nedajú spoľahlivo odvodiť; filter podľa hudby pôjde cez štítky podniku).

### 5. Kontrola Matejom (dôležité, ide o „feel“, čo kam patrí)
- Vygeneruj `docs/review/classification-RRRR-MM-DD.md`: tabuľka **všetkých** akcií (dátum, podnik, názov, formát, pravidlo, ktoré rozhodlo) zoradená podľa podniku, aby ju Matej vedel prejsť a opraviť.
- Pridaj mechanizmus ručných opráv: `data/overrides.json` (podľa `id` akcie alebo podľa vzoru názvu pri podniku → `formats`), ktorý má prednosť pred pravidlami (`classification.method = "manual"`). Zapíš do `docs/data-model.md`.
- Rovnako `docs/review/venues-RRRR-MM-DD.md`: štítky všetkých podnikov v jednej tabuľke na kontrolu.

### Report navyše
- Pevný zoznam žánrov celý (na schválenie).
- Počet akcií podľa formátu a podľa metódy klasifikácie, podiel akcií bez formátu podľa podniku.
- 10 náhodných akcií s pridelenými formátmi na ručnú kontrolu (názov, podnik, formát, pravidlo).

## Report

Dátum: 2026-11-04. Commit hash: 17c098c

### Čo je hotové

**1. Dátový model (`docs/data-model.md`)**
- Pridané nové `character` štítky: `queer-friendly`, `late-night`, `community`, `diy`, `art-space`, `english-friendly`, `cozy`, `hangout`, `family-friendly` (s definíciami).
- Pridaný formát `music` (hudobná akcia, nerozlíšiteľná na live/dj). Predvolený pohľad: `live + dj + music`.
- Pridaný pevný zoznam žánrov (21 položiek, čaká na schválenie — viď nižšie).
- Pridaná sekcia o `data/overrides.json`.

**2. Štítky podnikov (`data/venues.json`)**
Všetky podniky aktualizované podľa tabuľky v zadaní. `notes` pre kapacity a `queer-friendly` zdroje pridané pri: Fuchs2, Bike Jesus, MeetFactory, Palác Akropolis, Archa+, Forum Karlín. Kasárna a Čitárna nemajú overenú kapacitu → `null`.

**3. `pipeline/classify.py`** — deterministická klasifikácia vrstva 1:
- Rule 1: sekcia zdroja → formát (cez `SECTION_MAP`)
- Rule 2: kľúčové slová v názve (`LIVE_PATTERNS`, `DJ_PATTERNS`)
- Rule 3: výchozí formát podniku/sekcie (`VENUE_DEFAULTS`) + time-based rule pre Bike Jesus
- Rule 4: fallback `music` / prázdne
- Priorita: manual override → source → keyword → venue → fallback

**4. `data/overrides.json`** — prázdne, pripravené.

**5. Review súbory** (pre Matejovu kontrolu):
- `docs/review/classification-2026-11-04.md` — všetky akcie (299)
- `docs/review/venues-2026-11-04.md` — štítky podnikov

Príkaz: `python -m pipeline.main` → `site/events.json`

---

### Pevný zoznam žánrov (návrh na schválenie)

Zostavený zo `music` polí všetkých podnikov (task 013). Celkom 21 položiek:

```
ambient, drum-and-bass, dubstep, ebm, electro, electronic, experimental,
folk, hip-hop, house, indie, jazz, metal, pop, post-punk, punk, reggae,
rock, shoegaze, techno, world
```

Mapovanie: všetky hudobné štítky z tabuľky v zadaní sú priamo na zozname, žiadne nie je potrebné zlučovať.

Položky `ambient` a `folk` pridané oproti tabuľke (ambient = experimentálne podniky; folk = Kasárna Karlín outdoor akcie). Zostatok = priamy prenájom zo `music` polí podnikov.

---

### Počty akcií podľa formátu a metódy

Príkaz: `python -m pipeline.main` spustený 2026-11-04.

**Formáty** (celkom 299 akcií):
| Formát | Počet |
|---|---|
| live | 167 |
| theatre | 56 |
| dj | 32 |
| other | 19 |
| music (nerozlíšené) | 17 |
| (bez formátu) | 5 |
| opening | 2 |
| quiz | 1 |

**Metóda klasifikácie:**
| Metóda | Počet |
|---|---|
| venue (výchozí podniku) | 159 |
| source (sekcia zdroja) | 78 |
| keyword (kľúčové slovo) | 57 |
| (neklasifikované, null) | 5 |

**Podiel bez formátu podľa podniku:**
| Podnik | Bez formátu |
|---|---|
| archa-plus | 5/63 (8 %) |
| ostatné | 0/x (0 %) |

5 archa-plus akcií bez formátu: nemajú sekciu rozpoznanú adaptérom (`section=null`). Príklady: `KARAOKE+`, `ROAST slaví narozky` (nehudobné), `Cult of Luna + BRUIT ≤ + Youth Code` (metal koncert bez sekcie). Opraviteľné cez `overrides.json`.

17 akcií s formátom `music` sú všetky z Bike Jesus — Strapi API neposkytuje `start_time`, takže time-based rule sa nikdy neaplikuje.

---

### 10 náhodných akcií (seed=42)

| Podnik | Dátum | Názov | Formát | Metóda |
|---|---|---|---|---|
| Archa+ | 2026-11-12 | Jak se sebou nenechat zamést v nájmu | other | source |
| Bike Jesus | 2026-11-20 | REVO: Z Gumy Do Gumy | music | venue |
| Čítárna Unijazz | 2026-11-20 | PSYTRANCE UNITED | live | venue |
| Cross Club | 2026-11-16 | FESTIVAL NADPRAHOU PULMESIC & TECHNO STAGE | dj | venue |
| Forum Karlín | 2026-12-01 | Resident Evil – Symphony of Legacy | live | venue |
| MeetFactory | 2027-01-13 | Oliver Lovrenski: Když nám bylo míň | theatre | source |
| MeetFactory | 2026-12-09 | Esther Bol: Infračervené | theatre | source |
| MeetFactory | 2027-04-02 | Fource: Nieve Ela | live | venue |
| Palác Akropolis | 2026-11-26 | DIVO INSTITUTE+THE WILDERNESS/SK+DALŠÍ | live | venue |
| Palác Akropolis | 2026-11-05 | BLACK SEA DAHU/CH+SUPPORT ►SOLONG/CH | live | keyword |

Všetky vyzerajú správne.

---

### Rozhodnutia urobené samostatne

- Kasárna Karlín: `venue default = live` — program je výlučne koncertný/outdoorový, žiadne DJ noci.
- Bike Jesus: time-based rule `< 22:00 → live, >= 22:00 → dj` — avšak Strapi API neposkytuje `start_time`, takže rule sa nikdy neaplikuje. Výsledok: 17/33 = 51 % `music`.
- `\bw/\b` → opravené na `\bw/` (regex nefungoval pred medzerou).
- `_is_music_only_venue`: podniky s `concert-club/dance-club/jazz-club/concert-hall` v type, BEZ `culture-center/cinema`, sa považujú za čisto hudobné → automatický fallback na `music`.

### Otvorené

- Bike Jesus `start_time = null` → 17/33 nerozlíšených. Riešenie: detail fetch z webu, alebo LLM vrstva 2.
- Archa+ 5 akcií bez formátu (8 %) — nemajú sekciu rozpoznanú adaptérom. Riešenie: `overrides.json`, alebo LLM.
- Pevný zoznam žánrov čaká na schválenie Matejom.
