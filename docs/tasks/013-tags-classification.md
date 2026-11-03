# 013: Štítky podnikov, pevný zoznam žánrov a zatriedenie akcií (vrstva 1)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-04. Podmienka pred PWA: bez formátov je predvolený pohľad (`live` + `dj`) prázdny a bez štítkov nefungujú filtre. Bez LLM (to je vrstva 2, neskôr).

### 1. Zmeny dátového modelu (odsúhlasené Matejom 2026-11-04; zapíš do `docs/data-model.md` a `docs/decisions.md`)
**character** (podnik), pridať: `queer-friendly`, `late-night`, `community`, `diy`, `art-space`, `english-friendly`, `cozy`, `hangout`, `family-friendly`. Definície:
- `queer-friendly`: doložený queer program alebo spolupráca (queer kolektívy, Prague Pride, queer debaty). Len s doloženým zdrojom (do `notes` podniku), nikdy jediný štítok charakteru; nezistené neznamená „nie je“. (`queer` ostáva pre podniky, ktoré sú queer ako také.)
- `late-night`: program bežne do rána; `community`: komunitne vedené; `diy`: svojpomocné, nezávislé; `art-space`: galéria/rezidencie popri hudbe; `english-friendly`: program výslovne prístupný v angličtine; `cozy`: komorný priestor; `hangout`: hlavne posedenie, akcie doplnok; `family-friendly`: aj pre deti.

**features**, pridať: `garden`, `riverside`, `courtyard`.

**formats** akcie, pridať: `music` = hudobná akcia, pri ktorej sa nedá rozlíšiť `live` vs. `dj`. Predvolený pohľad v appke: `live` + `dj` + `music`. (Lepšie ako prázdne formáty alebo hádať live/dj.)

### 2. Štítky podnikov do `data/venues.json` (podľa Matejovho schválenia)
| Podnik | type | character | features | music | capacity | size |
|---|---|---|---|---|---|---|
| cross-club | (bez zmeny) concert-club, dance-club | alternative, underground, late-night | open-air | (bez zmeny) | 250 | small |
| fuchs2 | dance-club, concert-club | alternative, underground, queer-friendly, late-night | riverside | techno, electro, ebm, post-punk, indie | 650 | medium |
| bike-jesus | concert-club, dance-club, bar | underground, alternative, community, diy, queer-friendly | garden, riverside | techno, house, post-punk, indie, shoegaze | 280 | small |
| palac-akropolis | concert-club, culture-center | alternative | – | indie, rock, world, jazz, punk | 700 | medium |
| archa-plus | culture-center, concert-hall | alternative, experimental, queer-friendly, english-friendly | – | indie, electronic, metal, experimental | 1200 | medium |
| meetfactory | culture-center, concert-club | alternative, experimental, art-space | – | indie, electronic, experimental, metal, hip-hop, jazz | 750 | medium |
| forum-karlin | concert-hall | commercial | – | rock, pop, metal, hip-hop, electronic | 3800 | large |
| citarna-unijazz | cafe, culture-center | alternative, experimental, community, cozy | – | jazz, experimental | null | small |
| kasarna-karlin | culture-center, bar, cinema | alternative, hangout, community, family-friendly | open-air, seasonal, courtyard | indie | null | null |

Zdroje kapacít a `queer-friendly` zapíš do `notes` podniku:
- kapacita: Fuchs2 selection.cz/en/venues/fuchs2; Bike Jesus kdykam.com/en/venue/bike-jesus-praha-165; Akropolis liveurope.eu/palac-akropolis (700 veľký sál, 80 malý); Archa+ archatheatre.cz/en/spaces-and-technical.html (200–350 sedenie, do 1 200 stánie); MeetFactory meetfactory.cz/en/informace-pro-kapely; Forum Karlín Cvent (3 800 stánie, 1 800 sedenie).
- queer-friendly: Fuchs2 – séria FEMXCORE (easterndaze.net/?p=2082) a lokalita Prague Pride Festival (festival.praguepride.com/en/lokace/fuchs2-bike-jesus/); Bike Jesus – lokalita Prague Pride Festival (tá istá stránka); Archa+ – queer program na webe (debaty „Jste queer?“, „God Save the Drama Queen“).

### 3. Pevný zoznam žánrov (`docs/data-model.md`)
Zostav ho nad reálnymi dátami: zjednotenie `music` všetkých podnikov + žánre, ktoré zdroje samy uvádzajú (sekcie, tagy). Malé písmená, pomlčky, anglicky, cca 20–30 položiek, bez zbytočne jemného delenia. Ak niektorý hudobný štítok z tabuľky nesedí do zoznamu, namapuj ho a uveď v reporte. Zoznam je návrh na schválenie Matejom (uveď ho v reporte celý).

### 4. Zatriedenie akcií – vrstva 1 (deterministické, `pipeline/classify.py`)
Poradie pravidiel, každé len keď je isté; inak `formats` ostanú prázdne a `classification = null`:
1. **Sekcia/tag zo zdroja** → formát: napr. divadlo → `theatre`, film → `film`, kvíz → `quiz`, vernisáž → `opening`, hudba → `music`; tanec, debata, přednáška, workshop → `other`. Mapovanie pre každý zdroj zvlášť v konfigurácii, nie natvrdo v kóde.
2. **Kľúčové slová v názve** (opatrne, zoznam v konfigurácii): napr. `live`, `/live`, `(live)`, `křest`, `support`, `tour` → `live`; `dj set`, `b2b`, `w/` pri tanečnom klube → `dj`. Pri konflikte nič neprepisuj, len `music`.
3. **Podnik ako posledná možnosť:** ak podnik je výhradne hudobný (napr. type len `concert-club`/`dance-club`) a nič iné neplatí → `music`.
- `classification = {"method": "source" | "keyword" | "venue", "confidence": ...}` podľa pravidla, ktoré rozhodlo.
- Žánre akcií (`genres`) v tejto vrstve **nevypĺňaj** (z podniku sa nedajú spoľahlivo odvodiť; filter podľa hudby pôjde cez štítky podniku).

### Report navyše
- Pevný zoznam žánrov celý (na schválenie).
- Počet akcií podľa formátu a podľa metódy klasifikácie, podiel akcií bez formátu podľa podniku.
- 10 náhodných akcií s pridelenými formátmi na ručnú kontrolu (názov, podnik, formát, pravidlo).

## Report
