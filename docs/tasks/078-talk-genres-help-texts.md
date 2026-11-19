# 078: Žánre pre talk, úprava textov vysvetlenia typov

## Zadanie

**Schválené Matejom 2026-11-19 13:28–13:31.** Mení dáta (žánre) → **jeden beh pipeline na konci** (`CLAUDE.md`). Čo nie je jasné, spýtaj sa.

**Čítaj:** report 077; `docs/ai-rules.md` C (body 5 a 9) a B6; `docs/data-model.md` (`stage_genres`, `genre_candidates`, hierarchia); `data/genre_hierarchy.json`, `data/genre_aliases.json`; `pipeline/genres.py`; prepočet z uloženého prieskumu z 065 (`pipeline/enrich_ai.py`, `grep -n "065"`); `web/src/core/filter.ts` (rodičia žánrov kultúry, `grep -n -i "film, theatre, dance\|culture"`); `web/src/i18n/*.ts` (texty karty typov z 077).

### 1. Nové žánre pod `talk`
- Do zoznamu `stage_genres` pridaj **`slam-poetry`, `reading`, `book-launch`, `lecture`, `discussion`**, rodič v hierarchii **`talk`** (druh `stage`, bez zmeny schémy).
- Mapovania (aliasy) len na slovné spojenia, nie samotné slová: „slam poetry“, „poetry slam“ → `slam-poetry`; „autorské čtení“, „autorské čítanie“, „čtení“ (len pri akcii typu talk) → `reading`; „křest knihy“, „krst knihy“, „book launch“ → `book-launch`; „přednáška“, „prednáška“, „lecture“ → `lecture`; „diskuse“, „diskusia“, „debata“, „panel“ (len pri akcii typu talk) → `discussion`. Samotné „slam“ nemapovať.
- `docs/ai-rules.md` C: doplň bod (alebo rozšír 9), že pri podtype `talk` sú žánre `slam-poetry`, `reading`, `book-launch`, `lecture`, `discussion` (zastrešením je podtyp `talk`, ako pri filme a divadle), krátko kedy ktorý. B6 bez zmeny.
- **Prepočet existujúcich akcií** z uloženého prieskumu a textu akcie (mechanizmus z 065), **bez nového hľadania cez AI**.
- **Filter:** `talk` je zastrešenie žánrov kultúry rovnako ako `film`, `theatre`, `dance` – pri vybratom podtype talk sa ukáže riadok jeho žánrov (správanie z 076). Žánre bez akcií sa nezobrazujú (ako doteraz).

### 2. Texty karty vysvetlenia typov (nahrádzajú texty z 077)
| | sk | cs | en |
|---|---|---|---|
| DJ | DJ púšťa a mixuje skladby: rave, techno a drum and bass noci, sound systémy. | DJ pouští a mixuje skladby: rave, techno a drum and bass noci, sound systémy. | A DJ plays and mixes tracks: raves, techno and drum and bass nights, sound systems. |
| veta dole | Akcie, ktoré spájajú viac typov (napríklad koncert a po ňom DJ), zaraďujeme podľa ich hlavného zamerania. | Akce, které spojují více typů (třeba koncert a po něm DJ), řadíme podle jejich hlavního zaměření. | Events that combine several types (for example a concert followed by a DJ) are listed by their main focus. |

Koncert, Párty a Kultúra bez zmeny.

### 3. Pipeline
- Jeden beh na konci, raz počkaj.

## Overenie a report
- `pytest -q`, `npm test` (test: riadok žánrov pri vybratom talk), `npm run build`; číslo behu.
- Z publikovaného `events.json` (príkaz uveď): koľko akcií dostalo ktorý nový žáner, zoznam ich názvov (napr. CROSS SLAM → `slam-poetry`); žiadna akcia iného typu ako talk ich nesmie mať.
- Snímka JPEG 390 × 844 do `docs/tasks/078/`: `filter-talk.jpg` (Akcie, Najbližších 30 dní, vybratý talk s riadkom žánrov; ak žiadna talk akcia v období nemá nový žáner, Kedykoľvek).
