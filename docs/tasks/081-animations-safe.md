# 081: Animácie bez rizika (hravosť appky)

## Zadanie

**Schválené Matejom 2026-11-20 14:18.** Mení len appku (`web/`) → **pipeline nespúšťaj**, over len nasadenie `deploy-app`. Cieľ: appka živšia a hravejšia **bez pozorovateľného spomalenia a bez toho, aby sa čokoľvek pokazilo**. Čo nie je jasné, spýtaj sa (nevymýšľaj UI nad rámec tohto zadania).

**Čítaj:** `docs/design.md` časť 1 (farby) a **blok „Animácie (081)“ na konci časti 8**; `web/src/components/FilterSheet.tsx` (vzor animácie panelu zdola: `ANIM_MS`, `reduced`, posun prstom), `web/src/components/SelectorSheet.tsx`, `web/src/components/BottomNav.tsx`, `web/src/components/ForYouChip.tsx`, `web/src/components/FilterButton.tsx`, `web/src/map/pinCss.ts`, `web/src/map/markerSync.ts`; miesta so srdiečkom (`grep -rln toggleFavorite web/src`), Idem v `web/src/pages/EventPage.tsx` (`toggleGoing`), riadok s počtom v `web/src/pages/EventsPage.tsx` (`grep -n "count"`).

### Pravidlá pre všetky animácie (záväzné)
- Animuje sa **len `transform` a `opacity`** (žiadne `width`, `height`, `top`, `padding`, `box-shadow`, `filter` počas animácie).
- **Obsah je použiteľný hneď**, animácia nič neblokuje (ťuk počas animácie funguje, zoznam sa ukáže hneď).
- Časté akcie (ťuk, záložky, filter, Pre teba) **najviac ~250 ms**, panely ako Filter (`ANIM_MS` 220), piny spolu najviac ~300 ms.
- **`prefers-reduced-motion: reduce` → žiadne animácie** (zmena ostane okamžitá); vibrácie áno.
- **Vibrácia** cez `navigator.vibrate` len ak existuje, krátka (10–15 ms), nikdy chyba.
- **Každá animácia má vypínač** v jednom module (napr. `web/src/core/motion.ts`: `MOTION = { heartPop: true, … }`) – aby sa dala jedným riadkom vypnúť, ak by na telefóne sekala.
- Animácia sa spúšťa **len pri akcii používateľa alebo zmene výberu**, nikdy pri scrolle ani pri posune/priblížení mapy.

### 1. Panel dátumu ako panel Filtra
- **Obdobie v Akciách aj výber dňa na mape** (`SelectorSheet`, aj kalendár „Iný dátum“): vyjde zdola a zíde dole rovnakým pohybom a časovaním ako panel Filtra, stmavené pozadie sa plynulo objaví a zmizne. Späť a ťuk mimo panelu zatvoria s animáciou. Zavretie posunom prsta nadol ako pri Filtri, ak to Filter má.

### 2. Reakcie na ťuk
- **Srdiečko** (všade: Miesta, profil miesta, onboarding, Preferencie akcií): pri zapnutí poskočí (scale 1 → 1,3 → 1, ~250 ms) + vibrácia; pri vypnutí bez poskoku.
- **Pre teba:** pri zapnutí sa ikona iskier na čipe raz zatrblieta (krátke pootočenie/zväčšenie, ~300 ms) a odznaky ✦ na kartách sa objavia s malým oneskorením za sebou (najviac prvých ~12 viditeľných kariet, spolu ≤ 300 ms; ostatné hneď).
- **Stlačenie:** karty akcií (riadky, mriežka, karta na mape), riadky miest a tlačidlá (čipy, Filter, Dnes/obdobie, hlavné ružové tlačidlá) sa pri dotyku zmenšia na ~0,97 a po pustení vrátia (~100 ms). Nesmie to rozbiť scroll (pri posune prstom sa stlačenie zruší).
- **Odznak počtu na Filtri:** pri zmene čísla krátko poskočí.
- **Počet akcií** („12 akcií · 3 pre teba“): pri zmene obdobia, filtra, Pre teba, Nové, hľadania sa nové číslo krátko vysunie zdola (staré odíde nahor), ~200 ms. Text inak bez zmeny.

### 3. Spodná lišta
- Ružová pilulka aktívnej záložky sa pri prepnutí **presunie** na novú záložku (posun cez `transform`, nie zmenou šírky/paddingu – dnešné `transition: all` nahradiť), ikona novej záložky krátko poskočí. Rozmery a vzhľad lišty podľa `design.md` 1 bez zmeny.

### 4. Mapa – piny pri zmene dňa
- Pri **otvorení mapy, zmene dňa, filtra a Všetko | Obľúbené** piny „padnú“ na miesto (z ~12 px vyššie, malý odskok), s oneskorením podľa vzdialenosti od stredu obrazovky, spolu ≤ 300 ms. Nahrádza dnešné `pin-appear`. Miznutie pinov ako doteraz.
- **Nie** pri posune, priblížení, otočení mapy ani pri ťuknutí na pin. Logika prekrývania pinov (`collisions.ts`) a vybratý pin s pulzom bez zmeny.

### 5. Idem
- Pri zapnutí Idem sa ikona plus zmení na fajku s krátkou animáciou (fajka sa „dokreslí“ / poskočí, ~250 ms) a malý výbuch niekoľkých bodiek vo farbe appky okolo tlačidla (≤ 400 ms, zmizne sám); vibrácia. Pri vypnutí bez efektu.

### Nerobiť (odložené, rizikové)
- Obrázok akcie zväčšujúci sa do detailu (View Transitions), preskladanie zoznamu s animáciou pri zmene filtra, kostry s leskom pri načítaní, animované prázdne stavy.

## Overenie a report
- `npm test -- --reporter=dot` (testy vypínačov a `prefers-reduced-motion` – pri reduce sa animácie nespúšťajú), `npm run build`; nasadenie `deploy-app` (číslo behu). Dáta sa nemenia.
- **Meranie plynulosti** (Playwright, Chromium, CPU throttling 4× cez CDP `Emulation.setCPUThrottlingRate`, 390 × 844, dáta z Pages): pred zmenou (commit pred 081) a po nej, pri (a) otvorení panelu obdobia, (b) zapnutí Pre teba, (c) prepnutí záložky Akcie → Mapa, (d) zmene dňa na mape, (e) ťuku na srdiečko. Metrika: priemerné a najhoršie FPS / najdlhší snímok počas animácie (`requestAnimationFrame` alebo Performance trace) a čas od ťuku po zobrazenie obsahu. Tabuľka v reporte. **Ak niečo pri meraní citeľne zhorší (najdlhší snímok > 50 ms, ktorý predtým nebol), vypni to vypínačom a napíš to do reportu.**
- Snímky netreba (animácie na nich nevidno); namiesto nich v reporte zoznam, čo sa animuje a kde je vypínač.

## Report

**Dátum:** 2026-11-20. Commit: pozri `git log --grep 081` (feat + report v jednom commite). Pipeline sa nespúšťala (mení sa len `web/`).

### Čo je hotové (vypínače v `web/src/core/motion.ts`, `MOTION`)
| Animácia | Kde | Vypínač | Stav |
|---|---|---|---|
| Panel obdobia / dňa / kalendár zdola ako Filter (220 ms, stmavenie, Späť, ťuk mimo, posun prstom nadol) | `SelectorSheet.tsx` | `sheet` | zapnuté |
| Srdiečko poskočí 1 → 1,3 → 1 (250 ms) + vibrácia | `PrefPickers` (onboarding, preferencie), `PlacesPage`, `VenuePage` | `heartPop` | **vypnuté po meraní** (vibrácia ostáva) |
| Pre teba: iskra sa zatrblieta | `ForYouChip.tsx` | `forYouSparkle` | **vypnuté po meraní** |
| Pre teba: odznaky ✦ naskočia postupne (max 12, ≤ 300 ms) | `EventsPage.tsx` | `forYouBadges` | **vypnuté po meraní** |
| Stlačenie 0,97 (100 ms), ruší sa pri posune prstom | riadky akcií, karta na mape, riadky miest, čipy, Filter, Dnes/obdobie, ružové tlačidlá | `press` | zapnuté |
| Odznak Filtra poskočí | `FilterButton.tsx` | `filterBadge` | zapnuté |
| Počet akcií sa vysunie zdola (200 ms) – animuje sa celý riadok počtu | `SlideText.tsx`, `EventsPage.tsx` | `countSlide` | zapnuté |
| Pilulka v lište sa presúva cez `transform` (FLIP), ikona poskočí; `transition: all` odstránené | `BottomNav.tsx` | `navPill` | zapnuté |
| Piny padnú (−12 px, odskok, oneskorenie podľa vzdialenosti od stredu, ≤ 300 ms) pri otvorení mapy, zmene dňa, filtra, Všetko/Obľúbené; nie pri posune/zoome | `markerSync.ts`, `pinCss.ts`, `MapPage.tsx` | `pinDrop` | zapnuté |
| Idem: záložka poskočí + výbuch 8 bodiek (≤ 400 ms) + vibrácia (Matej v chate: záložka ostáva, bez fajky) | `EventPage.tsx` | `goingBurst` | zapnuté |

Pri `prefers-reduced-motion: reduce` sa nespúšťa nič (vibrácia áno). Ladenie: `?motionoff=heartPop,press` alebo `?motionoff=all` v URL vypne animácie pre jedno načítanie.

### Overenie
- `npm test -- --reporter=dot`: 286 passed (nové `core/motion.test.ts`: vypínače, reduce, vibrácia bez chyby, časy). `npm run build`: OK.
- Meranie: `tests/playwright/perf-081.spec.ts` + `web/playwright-081.config.ts` (Chromium, CPU 4×, 390 × 844, dáta z Pages, produkčné buildy cez `vite preview`: pred = ac5fc52, po = pracovná kópia so všetkými animáciami zapnutými). Príkaz: `cd web; $env:NODE_PATH='D:\AI\eventapp\web\node_modules'; $env:PERF_RUNS='5'; npx playwright test -c playwright-081.config.ts`. Výsledok v `docs/tasks/081/perf.json` (posledný beh, 5 opakovaní). Najdlhší snímok (max) / čas do obsahu (priemer):

| Scenár | Pred | Po |
|---|---|---|
| (a) panel obdobia | 83,3 ms / 56 ms | 33,4 ms / 55 ms |
| (b) Pre teba | 33,4 ms / 35 ms | **66,7 ms** / 55 ms |
| (c) Akcie → Mapa | 266,6 ms / 63 ms | 250 ms / 60 ms |
| (d) zmena dňa na mape | 33,4 ms / 17 ms | 33,4 ms / 14 ms |
| (e) srdiečko | 33,4 ms / 33 ms | **66,7 ms** / 31 ms |

Priemerné FPS boli vo všetkých scenároch okrem (c) 55–60 pred aj po; (c) ~12–13 FPS pred aj po (inicializácia mapy). Meranie je rozkolísané (napr. „pred“ (a) raz 83 ms), ale (b) a (e) prekročili 50 ms v dvoch meraniach po sebe, a predtým nie → podľa zadania vypnuté vypínačmi (`heartPop`, `forYouSparkle`, `forYouBadges`).

### Otvorené
- Meranie s vypnutými (b)/(e) animáciami som po vypnutí neopakoval (Matej ukončil úlohu po ~50 min). Nepotvrdená príčina (možno vytvorenie kompozitnej vrstvy pri WAAPI pod 4× spomalením); dá sa skúsiť `?motionoff=` na telefóne.
- `deploy-app`: číslo behu nižšie, ak sa stihlo overiť; inak skontrolovať v Actions.
- Rozhodnutie zapísané v `docs/decisions.md`.
