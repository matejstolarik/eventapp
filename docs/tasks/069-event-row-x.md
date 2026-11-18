# 069: Riadok akcie „X“ (nižší obrázok, farebné štítky, bez krúžku), návrat programu podniku a Môj účet, medzery pri „·“, preblikávanie detailu

## Zadanie

**Schválené Matejom 2026-11-18 večer** po teste 068. Dizajn: `docs/design.md` časť 4, blok **„Zmena 2026-11-18 večer – riadok akcie X“** (platí pred blokom A3). Appka takmer 1:1 podľa design.md; čo nejde, spýtaj sa.

**Čítaj:** design.md časť 1, časť 4 (oba bloky 2026-11-18), 3, 6, 7; report 068; `web/src/components/EventRow.tsx` (`MetaLine`, `TypeRing`, `BadgeTagRow`), `EventPanel.tsx`, `EventPage.tsx` (hero), `VenuePage.tsx`, `MyAccountPage.tsx`, stav pred 068: `git show design-pre-068:web/src/...` (program podniku, Môj účet, karta na mape).

### 1. Riadok Akcií „X“
- Obrázok šírka 112, výška podľa textového bloku (min 72), cover z náhľadu 4 : 3, zaoblenie 8; na obrázku len **new** vpravo hore.
- Bez krúžku typu. Štítky s **farebným textom typu** (`EVENT_TYPE_TAG_TEXT`) ako pred 068; bez štítkov jeden štítok s typom. **pre teba** (ružové iskry) prvé v riadku štítkov.
- Riadok „dátum · čas · miesto“ na jednom riadku, skracuje sa len miesto (ako v 068).

### 2. Návrat programu podniku a Môj účet → Akcie
- **Presne ako pred 068** (`design-pre-068`), vrátane farebných štítkov a usporiadania (dátum ako hlavná časť v programe podniku). Len náhľad je teraz 4 : 3 – v starých štvorcových políčkach `object-fit: cover`.

### 3. Karta akcie na mape a stránka akcie
- Karta na mape: **bez krúžku**, štítky farebným textom typu (ako pred 068); obrázok 4 : 3, new / pre teba na začiatku riadku štítkov ostávajú.
- Stránka akcie: **bez krúžku** (celý obrázok a farebné štítky bez plnofarebného štítku typu ostávajú z 068).
- `TypeRing` odstráň, ak sa už nikde nepoužíva.

### 4. Medzery pri oddeľovači „·“ (všade)
- **Koreňová príčina (hlavný chat z kódu):** medzera na začiatku alebo konci textu v položke `display:flex` sa zahodí. `EventRow.MetaLine`: `' · '` na konci prvého `span` → chýba medzera **za** bodkou; `EventPanel` (karta na mape): `' · 20:00'` na začiatku druhého `span` → chýba medzera **pred** bodkou. Over a oprav aj `VenuePage` (adresa · vzdialenosť), `EventPage` a ostatné výskyty (`grep -rn "·" web/src`).
- Oprava: jedna obyčajná medzera pred aj za bodkou vizuálne (napr. ` · ` alebo jeden spoločný komponent oddeľovača), **nie väčší okraj**. Unit test na `MetaLine` / spoločný oddeľovač (text obsahuje medzery na oboch stranách).

### 5. Preblikávanie pri otvorení akcie
- Matej: po ťuknutí na akciu stránka „preblikne“ – obsah sa najprv ukáže na inom mieste a potom skočí. **Hypotéza (z kódu, neoverená):** od 068 má hero obrázok výšku `auto` bez vyhradeného miesta (predtým štvorec `paddingTop: 100%`); stránka sa vykreslí bez obrázka a po stiahnutí `image_detail` (~1200 px) sa text posunie nadol.
- **Najprv over:** Playwright, otvorenie akcie zo zoznamu Akcií, snímky v čase 0 / 100 / 300 / 1000 ms (alebo trace) do `docs/tasks/069/` – potvrď alebo vyvráť hypotézu; skontroluj aj, či overlay nezdedí scroll pozíciu zoznamu.
- Ak sa potvrdí: pipeline zapíše rozmery `image_detail` (`image_detail_w`, `image_detail_h` – do `data-model.md`), stránka akcie vyhradí miesto podľa pomeru strán (pri chýbajúcich rozmeroch náhľad 4 : 3 ako zástupca, kým sa nenačíta). Ak je príčina iná, napíš ju a oprav ju.

## Overenie a report
- `npm test`, `npm run build`, `pytest -q`; číslo nasadenia a behu.
- Snímky JPEG 390 × 844 do `docs/tasks/069/`: `akcie-dnes.jpg`, `akcie-scroll.jpg`, `program-podniku.jpg`, `moje-akcie.jpg`, `mapa-karta.jpg`, `detail.jpg` + snímky z časti 5.
- Report: čo hotové, príčina preblikávania (overená), odchýlky, otvorené body.
