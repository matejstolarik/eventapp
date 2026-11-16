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
