# 077: Post-punk a post-hardcore aj pod punk, počet akcií pri Kedykoľvek, vysvetlenie typov vo Filtri

## Zadanie

**Schválené Matejom 2026-11-19 12:40 a 12:42.** Čo nie je jasné, spýtaj sa.

**Čítaj:** report 076; `data/genre_hierarchy.json`; `pipeline/genres.py` (`drop_contained_parents`); `docs/design.md` 4 (riadok pod lištou); `web/src/pages/EventsPage.tsx` (`grep -n -i "anytime\|count"`).

### 1. Hierarchia žánrov
- `post-punk`: rodičia `alternative` + **`punk`**.
- `post-hardcore`: rodičia `alternative` + **`punk`**.
- `hardcore` a `grindcore` bez zmeny (`grindcore` už je pod `metal` aj `punk`).
- Dôsledok v pipeline: `drop_contained_parents` (rodič sa zo štítkov odstráni, keď je jeho názov v názve podžánru) teraz pri akcii so štítkami `punk` aj `post-punk` odstráni `punk` – rovnako ako pri `doom-metal`/`metal`. Over, že je to tak, a v reporte uveď, koľko akcií sa to týka.
- Filter: pri `punk` sa nájdu aj akcie s `post-punk` a `post-hardcore` (napr. Iceage). Test v `filter.test.ts`.

### 2. Počet akcií pri Kedykoľvek
- Riadok pod lištou v Akciách ukazuje počet („372 akcií“, pri Pre teba „N akcií pre teba“) **aj pri období Kedykoľvek** (`design.md` 4, zmena 2026-11-19). Ostatné bez zmeny.

### 3. Vysvetlenie typov vo Filtri (Matej 2026-11-19 13:06, doplnené pred spustením)
- V paneli Filtra vedľa nadpisu **TYP AKCIE** malá ikona **„?“** (obrys kruhu, farba `#8E8AA6`, veľkosť ako text nadpisu, ťukacia plocha aspoň 44 px). Ťuk otvorí **malú kartu nad panelom Filtra** (z Filtra sa neodchádza): tmavá karta v štýle appky (ako panely, zaoblenie 16), pre každý typ riadok s **ikonou a farbou typu** (ako čipy typu), názvom tučne a textom; dole veta kurzívou/stlmene. Zavrie ťuk mimo karty, krížik alebo systémové Späť. Pohyb krátky ako panel (bez spomalenia), `prefers-reduced-motion` = okamžite.
- **Texty presne takto** (bez úprav; kľúče v `i18n/*.ts`):

| | sk | cs | en |
|---|---|---|---|
| Koncert | Interpret alebo kapela hrá svoju hudbu naživo. | Interpret nebo kapela hraje svou hudbu naživo. | An artist or band plays their own music live. |
| DJ | DJ púšťa a mixuje skladby. Patria sem aj rave, techno a drum and bass noci a sound systémy. | DJ pouští a mixuje skladby. Patří sem i rave, techno a drum and bass noci a sound systémy. | A DJ plays and mixes tracks. Raves, techno and drum and bass nights and sound systems count too. |
| Párty | Veľká klubová párty: tematické noci, hity 80. a 90., študentské a Erasmus párty. | Velká klubová párty: tematické noci, hity 80. a 90. let, studentské a Erasmus párty. | A big club party: theme nights, 80s and 90s hits, student and Erasmus parties. |
| Kultúra | Film, divadlo, tanec, stand-up, prednášky a čítania, workshopy, vernisáže a kvízy. | Film, divadlo, tanec, stand-up, přednášky a čtení, workshopy, vernisáže a kvízy. | Film, theatre, dance, stand-up, talks and readings, workshops, exhibition openings and quizzes. |
| veta dole | Keď je na akcii viac vecí, napríklad kapela a po nej DJ, zaradíme ju podľa toho, kvôli čomu tam ľudia idú. | Když je na akci víc věcí, třeba kapela a po ní DJ, zařadíme ji podle toho, kvůli čemu tam lidi jdou. | When an event mixes things, like a band followed by a DJ, we file it under what people come for. |

- Názvy typov v karte = rovnaké ako na čipoch (Koncert/Concert, DJ, Párty/Party, Kultúra/Kultura/Culture).

### 4. Pipeline
- Hierarchia mení dáta (štítky) → **jeden beh na konci** (`CLAUDE.md`), raz počkaj; nasadenie appky prebehne v rámci behu.

## Overenie a report
- `pytest -q`, `npm test`, `npm run build`; číslo behu.
- Z publikovaného `events.json`: koľko akcií má `post-punk`/`post-hardcore`, koľko stratilo štítok `punk` (príkaz uveď), či Iceage prejde filtrom koncert + punk (test alebo výpočet).
- Snímky JPEG 390 × 844 do `docs/tasks/077/`: `akcie-kedykolvek.jpg` (riadok s počtom), `filter-typy-help.jpg` (otvorená karta vysvetlenia, slovenčina).

## Report

**2026-11-19**, commit `cb65843` (hierarchia, appka, testy, rozhodnutie), report a snímky v nasledujúcom commite. Pipeline **Daily pipeline #53** (run 44521929731): **success**, `events.json` vygenerovaný 2026-11-19 13:22:46; appka nasadená **Deploy web app #51** (success, `cb65843`).

### Hotové
1. **Hierarchia** (`data/genre_hierarchy.json`): `post-punk` a `post-hardcore` → `alternative` + `punk`. `hardcore`, `grindcore` bez zmeny.
   - C7 (`drop_contained_parents`) odstráni `punk` **len pri `post-punk`** (`punk` je v názve). Pri `post-hardcore` sa `punk` ponechá – `punk` nie je podreťazec `post-hardcore` (pravidlo je podľa názvu, rovnako `trap` + `hip-hop`). Testy v `tests/test_genres_065.py`.
   - Filter: čip `punk` nájde `post-punk` aj `post-hardcore` (test v `filter.test.ts` so skutočnou hierarchiou, akcia ako Iceage: koncert + `post-punk` prejde filtrom koncert + punk).
2. **Počet pri Kedykoľvek** (`EventsPage.tsx` `countRowText`): riadok pod lištou ukazuje počet pri každom období (snímka: „368 akcií“; 4 z 372 akcií sú v čase snímky 19. 11. 17:00 už minulé). Pre teba bez zmeny.
3. **Vysvetlenie typov** (`FilterSheet.tsx`, kľúče `typeHelpLabel`, `typeHelpClose`, `typeHelp`, `typeHelpNote` v `i18n/sk|cs|en.ts`): „?“ (obrys kruhu `#8E8AA6`, 14 px, ťukacia plocha 44 × 44 – overené Playwrightom) vedľa TYP AKCIE; karta nad panelom s ikonou a farbou typu, názvom tučne, textom a vetou dole kurzívou. Zatvorí ťuk mimo, krížik, systémové Späť (zatvorí len kartu, Filter ostane; ďalšie Späť zavrie Filter). 220 ms ako panel, `prefers-reduced-motion` okamžite. Texty presne podľa zadania.

### Rozhodnutia (samostatne, v `docs/decisions.md`)
- Vzhľad karty nad rámec zadania: v strede obrazovky, `#1C1C27` s obrysom `#2E2D3C`, zaoblenie 16, stmavenie pozadia, ikona typu v obryse kruhu farby typu, názov farbou typu; poradie Koncert, DJ, Párty, Kultúra ako v tabuľke zadania.
- `punk` pri `post-hardcore` ostáva (vyplýva z C7, viď vyššie).

### Čísla (z publikovaného `events.json` behu #53)
Príkaz: `python count077.py after.json before.json` (scratchpad skript; `after.json` = `curl https://matejstolarik.github.io/eventapp/events.json` po behu #53, `before.json` = to isté pred behom, beh z 076):
- akcií 372; `post-punk` **10**, `post-hardcore` **1**.
- štítok `punk` stratila **1** akcia: `palac-akropolis-2026-11-26-divo-institute-the-wilderness-sk-dalsi` (pred: `punk, blues, rock, techno, post-punk, shoegaze, experimental`, po: bez `punk`). Žiadna akcia už nemá `punk` + `post-punk`.
- Iceage (`Live Nation: Iceage`, formats `concert`, genres `indie, post-punk`): rodičia vedú k `punk` → prejde filtrom koncert + punk (výpočet v skripte + test).

### Overenie
- `pytest -q`: **654 passed**. `npm test`: **241 passed** (15 súborov). `npm run build`: OK.
- Playwright `tests/playwright/screenshots-077.spec.ts` (dáta z Pages po behu #53, čas 19. 11. 17:00, z `web/` s `NODE_PATH=web/node_modules`): 2 passed – počet pri Kedykoľvek, texty karty, plocha „?“ ≥ 44 px, Späť/krížik/ťuk mimo.
- Snímky (JPEG 390 × 844) v `docs/tasks/077/`: `akcie-kedykolvek.jpg`, `filter-typy-help.jpg` (neprezerané – pravidlo kreditov).
- Na Pages bundle `assets/index-P5KQJcqZ.js` obsahuje `filter-type-help-card`, „kvôli čomu tam ľudia idú“ a `"post-punk":["alternative","punk"]` (overené `curl`).

### Otvorené
- Vzhľad karty (rozhodnutie vyššie) na potvrdenie Matejom podľa snímky.
- Plynulosť animácie na telefóne neoverená.
