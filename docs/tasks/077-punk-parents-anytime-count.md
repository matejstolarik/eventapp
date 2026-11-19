# 077: Post-punk a post-hardcore aj pod punk, počet akcií pri Kedykoľvek

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

### 3. Pipeline
- Hierarchia mení dáta (štítky) → **jeden beh na konci** (`CLAUDE.md`), raz počkaj; nasadenie appky prebehne v rámci behu.

## Overenie a report
- `pytest -q`, `npm test`, `npm run build`; číslo behu.
- Z publikovaného `events.json`: koľko akcií má `post-punk`/`post-hardcore`, koľko stratilo štítok `punk` (príkaz uveď), či Iceage prejde filtrom koncert + punk (test alebo výpočet).
- Snímka JPEG 390 × 844 do `docs/tasks/077/`: `akcie-kedykolvek.jpg` (riadok s počtom).
