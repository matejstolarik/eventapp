# 035: Mapa – „V noci“, zastarané piny, pulz, animácia miznutia

## Zadanie

**Čítaj:** `design.md` 1 + 2 (hlavne riadky o pulze a „Noc (0:00–5:00)“); `decisions.md` riadok 110 (`grep -n "V noci" docs/decisions.md`); `web/src/core/night.ts`, `core/events.ts`, `core/day.ts`; `web/src/map/markers.ts`; `web/src/components/DaySelector.tsx`; v `web/src/pages/MapPage.tsx` funkcie `buildMarkers`, `updateMarkers`, nočný `useEffect` (~r. 280), blok `panelEvents` / `sortedVenues` / `leftCount` (~r. 830–895), CSS `pin-appear` / `.pin-new`. `formatDayLabel` v `i18n/index.ts`.

Matej po teste v telefóne (2026-11-15). Hlavný chat našiel v kóde tieto koreňové príčiny:

1. **Piny sa po vytvorení nikdy neaktualizujú.** `updatePinElement` (`markers.ts`) mení len triedu `pin-selected`. Ak miesto ostane viditeľné po zmene dňa / Obľúbených / „V noci“ alebo po plynutí času, pin si drží typ, farbu, prstenec pulzu, srdiečko a `+N` z chvíle, keď vznikol. Preto napr. EPIC pulzuje aj na deň o 3 dni neskôr a pri prepnutí na „V noci“ piny nepulzovali, kým Matej nereštartoval appku.
2. **Viditeľnosť sa počíta na troch miestach rôzne.** `buildMarkers` vo „V noci“ filtruje miesta cez `isNightEvent`, ale udalosti pinu (`primary`, `extraCount`), `panelEvents`, `sortedVenues` (šípky ‹ ›) aj počty na šípkach berú všetky akcie predošlého dňa cez `getVenueEvents` / `getActiveVenueIds`. Preto šípky ukazujú počty z večera a v karte sa dá prepínať medzi akciami, ktoré už skončili (koncerty bez konca). Nočná vetva navyše ignoruje `showFavorites`, preto Obľúbené vo „V noci“ nerobia nič.
3. **„V noci“ sa nikdy samo nevyberie.** Počiatočný stav je `getToday(now)` (pred 5:00 = včerajší dátum) a nočný `useEffect` o polnoci len zapne `showNight`, `selectedDay` neprepne. Mapa sa tak po polnoci tvári ako predošlý deň (s jeho dátumom v tlačidle).
4. **Zoznam dní v noci začína včerajškom.** `getUpcomingDays(14, now)` začína od `getToday` (pred 5:00 včerajšok), `formatDayLabel` ho podľa kalendára označí ako „So 14. 11.“, potom „Dnes“. Matej chce: „V noci“, potom „Dnes“ (kalendárny dnešok, nový večer), „Zajtra“…, spolu 5 možností ako doteraz.
5. **Pulz bez známeho konca trvá do 5:00.** `isEventLive` pri akcii bez `end_time` vráti true od začiatku až do prepnutia dňa, aj koncert od 19:00 o polnoci.
6. **Časovače v pozadí nebežia.** `setTimeout` na polnoc/5:00 a stav „prebieha“ sa v PWA na pozadí (zamknutý telefón) neprepočíta; po návrate do appky ostane starý stav.

### Požadované správanie

**A. Jedna funkcia viditeľnosti (core, s testami).** Nová čistá funkcia v `web/src/core/` (napr. `visibleEvents(data, day, now, { favoritesOnly, isFavorite })` → mapa `venueId → Event[]` zoradená ako dnes v `getVenueEvents`). Z nej sa berie všetko: ktoré piny existujú, `primary`, `+N`, pulz, udalosti v karte, poradie a počty šípok ‹ ›. Žiadne iné miesto v `MapPage` už viditeľnosť nepočíta samo.
- Bežný deň: ako dnes (zrušené/zmiznuté a skončené so známym koncom preč).
- `NIGHT_DAY`: presne dohodnuté pravidlo z `design.md` 2 a `decisions.md` r. 110, bez zmeny: akcie predošlého dňa (`getToday(now)`), ktoré spĺňajú existujúce `isNightEvent` (známy koniec po teraz; bez konca len `party`/`dj` alebo miesto `late-night`, začiatok od 20:00). Nič iné (žiadny koncert z večera bez konca). `isNightEvent` nemeň, len ho použi všade.
- `favoritesOnly`: platí rovnako vo všetkých režimoch vrátane „V noci“.

**B. Pulz (Matej 2026-11-15).** Akcia „prebieha“:
- so známym koncom: od začiatku do konca (ako dnes),
- bez konca, formát `party` alebo `dj`, alebo miesto so štítkom `late-night`: od začiatku do 5:00 nasledujúceho rána,
- bez konca, ostatné: najviac 3 hodiny od začiatku.
- Akcia v inom dni ako „teraz“ nikdy nepulzuje. Kde sa pulz ukazuje v karte alebo poradí (live najprv), platí tá istá funkcia. Pridaj riadok do `decisions.md`.

**C. Piny sa aktualizujú.** `updatePinElement` musí premietnuť zmenu typu (farba, ikona), pulzu, srdiečka, `+N` a mena. Porovnaj kľúč dát pinu a pri zmene prestav len vnútro pinu (nie `Marker`), aby sa nestratil klik a výber. Mapa sa prepočíta: pri zmene dňa/Obľúbených, každých 60 s, keď je mapa viditeľná, a pri `visibilitychange` / `focus` (návrat do appky).

**D. „V noci“ sa vyberá samo.**
- Pri štarte medzi 0:00–4:59 je predvolený `NIGHT_DAY`.
- O polnoci (aj po návrate z pozadia) sa mapa prepne na `NIGHT_DAY`, ak mal používateľ vybraný „Dnes“ (dátum, ktorý práve prestal byť dneškom). Iný ručne vybraný deň ostáva.
- O 5:00 (aj po návrate z pozadia) „V noci“ zmizne a `NIGHT_DAY` sa zmení na `getToday(now)` (ako dnes, ale aj cez `visibilitychange`).
- „Na mape“ z akcie (`pendingSelect`) v noci: ak akcia patrí do „V noci“ (podľa A), vyber `NIGHT_DAY`, inak jej dátum.
- Ak vybrané miesto po zmene prestane byť viditeľné, karta sa zatvorí (rovnako ako ťuknutie mimo).

**E. Zoznam dní v noci.** „V noci“, potom 4 dni od **kalendárneho** dneška („Dnes“, „Zajtra“, …). Mimo noci bez zmeny (5 dní od `getToday`). Kalendár „Iný dátum“ bez zmeny.

**F. Animácia miznutia pinov (Matej).** Pin, ktorý z mapy odchádza (zmena dňa, Obľúbené, „V noci“, prechod cez 5:00/koniec akcie), zmizne opačnou animáciou k `pin-appear`: 180 ms, `ease-in`, opacity 1→0, scale 1→0.82, ten istý `transform-origin` ako pri objavení. Podmienky, aby sa s ničím nebila:
- Odchádzajúci pin má `pointer-events: none`, nie je vo `markersRef` (presuň ho do zoznamu odchádzajúcich) a nepočíta sa do kolízií mien, prekryvov pinov ani spoločného mena dvojice.
- Marker sa odstráni po `animationend` (záloha `setTimeout` 250 ms).
- Ak sa to isté miesto vráti počas miznutia (rýchle prepínanie), miznutie sa zruší, pin sa použije znova (vráti sa do `markersRef`) a plynulo sa vráti do plnej veľkosti (prechod z aktuálneho stavu, nie skok).
- Vybraný pin, ktorý odchádza, najprv stratí `pin-selected` (karta sa zatvára podľa D).
- `prefers-reduced-motion`: okamžité odstránenie.
- Objavovanie (`pin-new`) a miznutie bežia súčasne pri tom istom prepnutí (staré miznú, nové sa objavujú), bez posunu ostatných pinov.

### Testy
- Vitest pre funkciu z A a pre B, so zmrazeným `now`: 01:30 – koncert predošlého dňa 19:00 bez konca skrytý; párty predošlého dňa 23:00 bez konca viditeľná a pulzuje; akcia s koncom 02:00 viditeľná, o 02:30 skrytá; `favoritesOnly` vo „V noci“; 21:00 – koncert od 19:00 bez konca pulzuje, o 22:30 nie; akcia o 3 dni neskôr (EPIC 22:00–05:00) nikdy nepulzuje.
- Test zoznamu dní v noci (E) a predvoleného dňa (D) – čisté funkcie, nie komponent.

### Overenie
- `npm test`, `npm run build` vo `web/`, číslo nasadenia (beh Actions) v reporte.
- Snímky Playwright (`page.clock` na 01:30 v sobotu, syntetické `events.json` podľa `scripts/review/map-names-check.js`), JPEG do `docs/tasks/035/`: `01-noc-predvolene.jpg` (mapa po štarte o 01:30), `02-noc-dni.jpg` (otvorený výber dňa), `03-noc-oblubene.jpg` (V noci + Obľúbené), `04-den-o-3-dni.jpg` (deň o 3 dni, žiadny pulz).
- V reporte zoznam situácií, kde beží miznutie (F), aby ich Matej prešiel v telefóne.

## Report

**Dátum:** 2026-11-15  
**Commit:** (pozri nižšie po commite)

### Čo je hotové

**A. `visibleEvents` (core, single source of truth)**  
Nová funkcia `web/src/core/visible.ts` → `visibleEvents(data, day, now, {favoritesOnly, isFavorite})` vracia `Map<venueId, Event[]>`. Použitá na všetkých miestach v `MapPage.tsx`: ktoré piny existujú, `primary`, `+N`, `panelEvents`, `sortedVenues`, šípky ‹ ›, geolocation view. `favoritesOnly` platí aj vo `NIGHT_DAY`.

**B. Pulz (`isEventPulsing`)**  
Nová funkcia `web/src/core/events.ts`. So známym koncom: od začiatku do konca. Bez konca + `party`/`dj` alebo `late-night`: od začiatku do 5:00 nasledujúceho rána. Ostatné: max 3 h od začiatku. Iný deň = nikdy. Zaznamenané v `docs/decisions.md` (2026-11-15). `getVenueEvents` radí pulsujúce akcie na začiatok. `getPrimaryEvent` zjednodušená na `events[0] ?? null`.

**C. Piny sa aktualizujú**  
`pinDataKey()` + `buildPinInner()` v `markers.ts`. `updatePinElement` porovnáva kľúč a prestavuje `.pin-inner` pri zmene. Mapa sa prepočíta každých 60 s, pri `visibilitychange`/`focus`, pri zmene dňa/Obľúbených. `updateMarkersRef` drží referenčnú funkciu.

**D. „V noci" sa vyberá samo**  
Počiatočný stav: `isNightTime(now) ? NIGHT_DAY : getToday(now)`. O polnoci/5:00 (aj po návrate z pozadia): `visibilitychange` + `focus` listener prepína stav. `pendingSelect` nočná vetva: `isNightEvent` → `NIGHT_DAY`, inak dátum akcie. Zatvorenie karty ak vybrané miesto zmizne z `visibleEvents`.

**E. Zoznam dní v noci**  
`showNight ? getUpcomingDays(4, noonToday) : getUpcomingDays(5, curNow)` kde `noonToday = new Date(toDateString(curNow) + 'T12:00:00')`. V noci: V noci + 4 dni od kalendárneho dneška. Bez zmeny mimo noci.

**F. Animácia miznutia pinov**  
CSS `@keyframes pin-disappear` (opacity 1→0, scale 1→0.82, 180 ms, ease-in). `leavingMarkersRef` drží odchádzajúce piny. `animationend` / záloha 250 ms ich odstráni. Rýchle prepnutie späť: zruší animáciu, pin sa vráti do `markersRef`. `prefers-reduced-motion`: okamžité odstránenie. Vybraný pin: stráca `pin-selected` pred odchodom (karta sa zatvára).

### Testy

```
npm test  →  80/80 passed (8 súborov)
npm run build  →  success, žiadne TS chyby
```

Nové testy: `web/src/core/visible.test.ts` (16 testov) — pokrýva A, B, D, E.

### Snímky Playwright

`docs/tasks/035/` (syntetické events.json, `page.clock.setFixedTime` na 2026-11-21 01:30 sobota):
- `01-noc-predvolene.jpg` — mapa po štarte, auto-vybrané NIGHT_DAY
- `02-noc-dni.jpg` — otvorený výber dňa (V noci + 4 kalendárne dni)
- `03-noc-oblubene.jpg` — V noci + Obľúbené (len Cross Club)
- `04-den-o-3-dni.jpg` — deň +3 (utorok), žiadny pulzový prsteň

### Situácie kde beží animácia miznutia (F) – otestovať v telefóne

1. Prepnutie dňa: staré piny miznú (pin-disappear), nové sa objavujú (pin-appear) súčasne
2. Zapnutie/vypnutie Obľúbených: piny bez obľúbenia miznú
3. Prechod cez 5:00: NIGHT_DAY zmizne, zvyšok dňa ostáva
4. Rýchle prepnutie späť na ten istý deň počas miznutia: animácia sa zruší, pin sa použije znova
5. Vybraný pin pri zmene dňa: pin-selected sa odoberie, karta sa zavrie, pin zmizne animáciou
6. Koniec akcie (60-sekundový interval): pin zmizne ak mu vypršali všetky akcie

### Čo ostáva otvorené

- Nasadenie (GitHub Actions) – číslo behu bude doplnené po push
- Animácia F (body 1–6) je treba overiť na reálnom telefóne (Matej)
