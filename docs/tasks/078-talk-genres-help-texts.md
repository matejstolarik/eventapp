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

## Report

**2026-11-19**, commit `c62b7ee` (pipeline, dáta, appka, testy, docs), report, snímka a Playwright skript v nasledujúcom commite. Pipeline **Daily pipeline #54** (run 44525925373): **success**, `events.json` vygenerovaný 2026-11-19 13:49:29; appka nasadená **Deploy web app** (run 44525908307, success, `c62b7ee`).

### Hotové
1. **Žánre talk** `slam-poetry`, `reading`, `book-launch`, `lecture`, `discussion` v `STAGE_GENRES` (`pipeline/genres.py`, nová množina `TALK_GENRES`), rodič `talk` v `data/genre_hierarchy.json`, `talk` v `UMBRELLAS`. Aliasy (len spojenia + zadané jednotlivé slová, samotné „slam“ nie) v `data/genre_aliases.json`.
   - Dáva ich `apply_talk_genres` (`pipeline/enrich_ai.py`, po AI kroku, bez API, každý beh): schválené spojenia v názve, `description` a `facts` uloženého prieskumu, celé slová; len akcie s `talk` vo `formats`, ostatným sa odstránia. To je zároveň **prepočet existujúcich akcií** (uložený prieskum + text, žiadne nové hľadanie).
   - Žánre talk od AI (napr. kandidát „slam poetry“ pri CROSS SLAM) sa zahodia – vznikajú len zo spojení v texte.
   - `docs/ai-rules.md` C10 (nový bod), `docs/data-model.md` (stage_genres, hierarchia), prompt `pipeline/ai_rules.py` (zoznam talk zvlášť, AI ich nevracia).
   - **Filter:** appka berie hierarchiu z `data/`, `talk` je podtyp kultúry → riadok žánrov sa ukáže sám (správanie z 076). Test vo `filter.test.ts` so skutočnou hierarchiou (riadok pri talk, žánre bez akcií nie, filter `talk:slam-poetry`).
2. **Texty karty typov** (DJ + veta dole) v `web/src/i18n/sk|cs|en.ts` presne podľa tabuľky; Koncert, Párty, Kultúra bez zmeny. Štítky `slam poetry`, `book launch` v `en.tags` (ostatné kódy sa zobrazia ako sú).

### Rozhodnutia (samostatne, v `docs/decisions.md`)
- Medzi slovami viacslovného spojenia môžu byť najviac 2 slová – inak by „KAVÁRNA KŘEST BOLDRIKOVO KNIHY“ / „křest první knihy haiku“ nedostali `book-launch`.
- „Akcia typu talk“ = `talk` kdekoľvek vo `formats` (aj doplnkový). Pri hlavnom type talk idú žánre talk na začiatok, inak na koniec.
- Pôvod `enrichment.genres` pri akcii bez žánrov = kópia pôvodu `formats` (ako 065), bez novej hodnoty `by`.

### Čísla (z publikovaného `events.json` behu #54)
Príkaz: `curl -s -o after.json https://matejstolarik.github.io/eventapp/events.json; python -I count078.py after.json` (scratchpad skript):
- akcií 372; `slam-poetry` **1**, `reading` **1**, `book-launch` **2**, `lecture` **0**, `discussion` **1**; akcií iného typu ako talk so žánrom talk: **0**.
  - `slam-poetry`: CROSS SLAM 2026 - NOVÁ GENERACE - No.4 (24. 11., `talk, dj`; z prieskumu „genres: slam poetry“)
  - `reading`: Podzemnická vánoční besídka (5. 12., hlavný `concert`, talk doplnkový; popis „Hraní, čtení, výstava“)
  - `book-launch`: KAVÁRNA KŘEST BOLDRIKOVO KNIHY (19. 11.), KŘEST KNIHY (Roxy, 9. 12.)
  - `discussion`: Střed zájmu: Síla kolektivu (Archa+, 26. 11.; z prieskumu „Talks/panel participants“)
- Lokálna simulácia na dátach pred behom (#53) dala to isté.

### Overenie
- `pytest -q`: **658 passed** (nový `tests/test_talk_genres_078.py`). `npm test`: **242 passed** (15 súborov). `npm run build`: OK.
- Playwright `tests/playwright/screenshots-078.spec.ts` (dáta z Pages po behu #54, čas 19. 11. 17:00, Najbližších 30 dní): 1 passed; riadok talk: `book launch 2`, `discussion 1`, `slam poetry 1`. Podzemnická besídka (`reading`) v riadku nie je – hlavný typ je koncert, riadok berie podtyp akcie (pravidlo 076).
- Snímka (JPEG 390 × 844) `docs/tasks/078/filter-talk.jpg` (neprezeraná – pravidlo kreditov).
- Na Pages bundle `assets/index-CVyWEWch.js` obsahuje „podľa ich hlavného zamerania“, `"slam-poetry":["talk"]` a „book launch“ (overené `curl`).

### Otvorené
- `lecture` zatiaľ nemá žiadna akcia (v textoch talk akcií nie je „přednáška/lecture“; „lecturer“ sa zámerne nepočíta).
- `reading` pri akcii s hlavným typom koncert sa vo filtri talk neukáže (076); ak to chceš inak, treba rozhodnutie.
