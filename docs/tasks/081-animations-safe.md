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
