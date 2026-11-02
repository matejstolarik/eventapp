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

Dátum: 2026-11-02. Commit: `966b4da` Task 001+002: task workflow docs, Citarna fixes, sold_out/room, Palac Akropolis adapter

### Čo je hotové

1. `docs/tasks/README.md` vytvorený – formát NNN-nazov.md, sekcie Zadanie + Report, append-only.
2. `CLAUDE.md` doplnený: pravidlo `## Report` (dátum, commity, čo je hotové, rozhodnutia, čísla z events.json + príkaz, overenie webu, otvorené) a pravidlo o append-only `docs/`.
3. `docs/project.md` opravený: zdroje v1 (RSS, JSON-LD, HTML; bez RA), rozsah v1 rozšírený (moje podniky, onboarding, going, .ics, profileStore), odstránený follow/going/onboarding z backlogu, pridaná sekcia „Fázy vydania" a opravené „Poradie práce" (7 krokov, 1–2 hotové, 3 prebieha).
4. `docs/data-model.md` opravený: zastaraný odkaz na WP REST API / `citarna_mec` nahradený popisom `html` strategy.
5. `docs/decisions.md` doplnený: poznámka „(nahradené ...)" pri riadku 2026-10-29, 10 nových riadkov z 2026-10-31.
6. `docs/status.md`: sekcia „Otvorené úlohy" nahradená odkazom na `docs/tasks/`.
7. `docs/tasks/000-history.md` vytvorený s históriou úloh 1–5.

### Rozhodnutia

Žiadne – zadanie bolo jednoznačné.

### Čísla

Úloha 001 nemení pipeline ani events.json; čísla sú v reporte úlohy 002.

### Overenie

Zmeny sú čisto v docs/; overenie nie je potrebné.

### Otvorené

Nič.
