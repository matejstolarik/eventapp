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
