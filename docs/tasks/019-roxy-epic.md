# 019: Roxy a EPIC (+ nové žánre a štítok `tourist`)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-04. Podklady: úloha 014, fixtures `tests/fixtures/survey/roxy.html`, `epic-prague.html`. Duplex a Lucerna Music Bar zatiaľ nie (Matej).

### 1. Dátový model (odsúhlasené Matejom 2026-11-04; `data-model.md`, `decisions.md`)
- Pevný zoznam žánrov doplň o: `hardstyle`, `trance` (vrátane psytrance), `latin` (reggaeton, latino), `r-n-b`, `disco`, `ska`.
- Charakter podniku doplň o `tourist` (program a prevádzka zamerané najmä na turistov).
- Formát `party` sa **nepridáva**: klubová noc s DJ-mi je `dj` (v appke sa zobrazí ako „Párty / DJ“). Téma večera (študentská, 80s/90s, latino) ide cez `character` akcie (`student`, `retro`…) a žánre.

### 2. Roxy (`html`)
- Program: https://www.roxy.cz/club/ (celý program na jednej stránke; `<time datetime>`, `h2.title`, `h3.subtitle`, `data-hashtags`).
- `data-hashtags` použi ako sekciu zdroja (`sources[].section`) a v mapovaní formátov: `#concert` → `live`, `#party` → `dj`, ostatné zaloguj a mapuj rozumne (napr. umelecký večer → `other`/`opening` podľa obsahu); mapovanie v konfigurácii.
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
