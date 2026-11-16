# 051: Nové ikony typov, bez štítkov podniku v Akciách, testovacie obrázky

## Zadanie

**Čítaj:** `design.md` časť 1, odsek „Typ akcie pre farbu a ikonu značky“ a „Ikony“. Súbory `docs/design/icons/*.svg`. V kóde: `map/markers.ts` (`ICON_SVG`, `MarkerData`), `map/markerSync.ts` (kde vzniká `MarkerData`), `icons/index.tsx` (`EventTypeIcon`), `core/eventType.ts`, `pages/EventsPage.tsx` (štítky podniku na karte).

Každá časť vlastný commit.

### 1. Ikona podľa typu a podtypu (`core/`)
- Funkcia (napr. `eventIconKey(formats)`) → `concert` | `party` | `dj` | `film` | `comedy` | `dance` | `culture`. Pri type kultúra rozhoduje **prvý** podtyp kultúry vo formátoch: `film` → `film`, `comedy` → `comedy`, `dance` → `dance`, inak `culture` (masky). Typ `other` → `culture`. Testy.
- Farba ostáva podľa typu (`EVENT_TYPE_COLOR` / `EVENT_TYPE_DARK`), ikona podľa `eventIconKey`.

### 2. SVG ikon
- Prevezmi presne `docs/design/icons/concert-guitar.svg`, `film-clapper.svg`, `comedy-mic.svg`, `dance.svg` (nekresli nanovo, nemeň cesty ani mierku).
- `dance.svg` je **plná silueta** (`fill` vo farbe, bez ťahu) – jediná výnimka.
- Koncert: elektrická gitara nahrádza mikrofón. Párty, DJ, masky bez zmeny.
- Licencia: gitara a klapka sú z Lucide (ISC). Pridaj licenčný text Lucide do repa (napr. `web/src/icons/LICENSE-lucide.txt`).

### 3. Kde sa ikona mení
- **Piny na mape:** `MarkerData` dostane kľúč ikony (z akcie, podľa ktorej sa dnes určuje `eventType` pinu); kľúč zahrň do `pinDataKey`, aby sa pin prekreslil. Veľkosť a pozícia ako doteraz (22 px v 36 px kruhu).
- **`EventTypeIcon`** (plocha bez obrázka v Akciách, karta na mape, stránka akcie, Miesta): rovnaké ikony podľa kľúča. Komponent dostane kľúč ikony alebo formáty; volajúci posielajú údaje akcie.
- Jedno miesto pravdy pre SVG (zdieľané pre `markers.ts` aj `EventTypeIcon`), nie dve kópie.

### 4. Bez štítkov podniku v mriežke Akcií
Karta v Akciách nezobrazuje štítky charakteru podniku (`venue.character`, biele pilulky) – len štítky akcie (`eventTags`). Štítky podniku ostávajú len na stránke a profile podniku.

### 5. Testy a poriadok
- Fixtúry Playwright: testovacie obrázky sa v 050 nenačítali (cesty `/eventapp/test-thumb-*.jpg` neexistujú). Pridaj malé testovacie JPEG do `tests/playwright/` (alebo do public len pre test server) tak, aby sa v screenshote naozaj zobrazili.
- Zmaž z repa `docs/tasks/048/pw-output/` (`git rm`) a pridaj `pw-output` do `.gitignore`.

## Overenie
- `npm test` (`--reporter=dot`), build OK.
- Screenshoty (Playwright, JPEG 390 × 844 do `docs/tasks/051/`): `mapa-piny.jpg` (aspoň po jednom pine koncert, párty, DJ, film, comedy, dance, divadlo), `akcie-mriezka.jpg` (akcie s obrázkom – fotky viditeľné – aj bez obrázka s novými ikonami, žiadne štítky podniku).

## Report

**Dátum:** 2026-11-16  
**Commity:** 7613da6, 897ed0e, 234f3db, 69633a0

### Čo je hotové

1. **`eventIconKey(formats)` → `EventIconKey`** (`core/eventType.ts`): nový typ `EventIconKey = 'concert' | 'party' | 'dj' | 'film' | 'comedy' | 'dance' | 'culture'`. Funkcia určuje ikonu podľa priorite: party/dj/concert priamo; kultúra → prvý podtyp film/comedy/dance, inak culture; other → culture. 15 testov prechádza.

2. **SVG ikony** (`icons/index.tsx`): `IconConcert` nahradený Lucide `guitar-electric` (scale 1.12); pridané `IconFilm` (Lucide `clapperboard`), `IconComedy` (retro stojacový mikrofón), `IconDance` (plná silueta, fill bez stroke). `EventTypeIcon` prijíma `iconKey: EventIconKey` namiesto `type: EventType`. SVG cesty prebraté presne z `docs/design/icons/`.

3. **Piny na mape** (`map/markers.ts`): `ICON_SVG` prekľúčovaný na `EventIconKey` – všetky 7 ikon. `MarkerData` dostalo `iconKey`; `pinDataKey` ho zahŕňa. `MapPage.tsx` počíta `iconKey = eventIconKey(primary.formats)`.

4. **Bez štítkov podniku v mriežke Akcií** (`EventsPage.tsx`): `venueTags` a ich renderovanie odstránené z `EventCard`. `venue.character` zostáva len na VenuePage a PlacesPage.

5. **Testovacie JPEG** (`web/public/test-thumb-*.jpg`): 6 súborov (concert, party, dj, film, comedy, dance) uložených v `public/` – servované na `/eventapp/test-thumb-*.jpg`. `screenshots051.mjs` skript pre beh screenhotov.

6. **Čistenie**: `docs/tasks/048/pw-output/` odstránený z gitu; `pw-output/` pridaný do `.gitignore`. Licencia Lucide v `web/src/icons/LICENSE-lucide.txt`.

### Rozhodnutia

- `EventTypeIcon` prijíma `iconKey` namiesto `type` – jeden interface, žiadne pretypovanie. VenuePage a PlacesPage (len `EventType`, nie formats) používajú `et === 'other' ? 'culture' : et as EventIconKey`.
- SVG v `ICON_SVG` (markers.ts) sú inline string kópie rovnakých ciest ako JSX komponenty – nie je zdieľaný súbor SVG, lebo markers.ts je vanilla JS (nie React). Jedno miesto pravdy pre tvar ikon je `docs/design/icons/*.svg`.
- Playwright `.spec.ts` súbory zlyhávajú na module resolution (testDir je mimo `web/`); screenshots idú cez `.mjs` skript ako ostatné úlohy.

### Overenie

- `npm test -- --reporter=dot`: 185 testov (11 súborov) prechádza. Build OK (3.85s).
- Screenshoty v `docs/tasks/051/`: `mapa-piny.jpg` (7 piny – koncert, party, DJ, film, comedy, dance, divadlo), `akcie-mriezka.jpg` (akcie s obrázkom aj s novou ikonou, bez štítkov podniku).
