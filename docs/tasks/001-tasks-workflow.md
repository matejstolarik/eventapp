# 001: Úlohy ako súbory, reporty, oprava zastaraných docs

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02.

1. Vytvor `docs/tasks/README.md`: každá úloha je súbor `NNN-kratky-nazov.md` so sekciami `## Zadanie` (píše hlavný chat, nemeníš ho) a `## Report` (píšeš ty na konci úlohy). Súbory sa nemažú ani neprepisujú, nová úloha = nové číslo. Zadania môže do repa commitovať aj hlavný chat; pred začatím úlohy sprav `git pull`.
2. Do `CLAUDE.md` pridaj pravidlo: na konci každej úlohy zapíš do jej súboru `## Report` s týmito časťami:
   - Dátum, commity (hash + správa)
   - Čo je hotové
   - Čo si rozhodol sám a prečo
   - Čísla: počítaj ich skriptom zo `site/events.json` z posledného behu a uveď aj príkaz, ktorým si ich vypočítal
   - Overenie proti webu (konkrétne URL a hodnoty)
   - Čo ostalo otvorené alebo čo si nestihol
   Report commitni a pushni spolu s prácou. Do chatu napíš len: číslo úlohy, hotovo/nehotovo, commit. Medzivýsledky nie sú výsledok.
3. Do `CLAUDE.md`: `docs/` je jediný zdroj pravdy pre technické veci. `decisions.md` a `tasks/` sú len na pridávanie, staré záznamy sa nemažú ani neprepisujú (zmena = nový riadok, ktorý starý nahrádza).
4. Oprav zastarané veci v docs:
   - `docs/project.md`: zdroje v1 sú RSS, schema.org Event (JSON-LD), HTML. Resident Advisor nie je zdroj, len odkaz `ra_url`.
   - `docs/data-model.md`: riadok o `html` strategy `citarna_mec` (WP REST API) je zastaraný, Čitárna je `jsonld` / `mec_ajax` + detail stránky. Oprav ho.
   - `docs/decisions.md`: riadok z 2026-10-29 s prioritou `ra` > `jsonld` nechaj, je nahradený riadkom z 2026-10-30. Ak chýba poznámka, že je nahradený, pridaj ju na koniec riadku.
5. V `status.md` nahraď sekciu „Otvorené úlohy“ odkazom na `docs/tasks/` (hotové úlohy 1 až 5 z tabuľky presuň do `docs/tasks/000-history.md`, nič nemaž).

## Report
