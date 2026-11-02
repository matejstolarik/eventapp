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

6. `docs/project.md` je v rozpore s rozhodnutiami z 2026-10-31 (doplnené do zadania 2026-11-02 pred začatím úlohy). Oprav:
   - Rozsah v1 obsahuje aj: obľúbené podniky („moje podniky“), onboarding pri prvom spustení (výber podnikov a formátov, žánre až po vzniku zoznamu; každý krok preskočiteľný; uložený lokálne), osobné „going“ (lokálne, zoznam „moje akcie“) a tlačidlo „pridať do kalendára“ (`.ics`). Bez účtu a bez backendu. Profil a obľúbené cez jednu vrstvu (napr. `profileStore`), aby sa neskôr dala vymeniť za sync s účtom bez prepisovania UI.
   - Mimo v1: účty a registrácia, sociálne „going“ (kto ešte ide), push notifikácie, mapa, Spotify, IG, natívna appka. Z backlogu odstráň follow, going a onboarding (sú vo v1).
   - Pridaj sekciu „Fázy vydania“: 1) v1 PWA pre Mateja a kamarátov, bez účtu; 2) verejná PWA aj v Play Store (Trusted Web Activity) s účtami: registrácia na začiatku s možnosťou preskočiť, sync profilu, mazanie účtu v appke, sociálne „going“, push notifikácie; 3) App Store a natívna appka (pravdepodobne React Native / Expo) až pri dôvere v projekt. Dôsledok už pre v1: odkazy na akcie a podniky musia fungovať bez prihlásenia a stáť na nemennom `id`.
   - „Poradie práce“: 1 až 2 hotové; 3 adaptéry pre súčasné podniky (Cross, MeetFactory, Kasárna, Čitárna, Akropolis); 4 denný beh + GitHub Pages; 5 test LLM extrakcie nad HTML (Twist, Akropolis ako kontrola) → rozhodnutie vlastné parsery vs. LLM; 6 minimálna PWA; 7 ďalšie podniky.
   - Tieto rozhodnutia (2026-10-31) pridaj aj do `docs/decisions.md` ako nové riadky.

## Report
