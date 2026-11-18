# 072: Najviac 4 štítky bez rozplynutia, jazyk, dátum v Môj účet, obrázok v detaile, zoom plagátu

## Zadanie

**Schválené Matejom 2026-11-19 00:16.** Len frontend (`web/`). **Pipeline nespúšťaj** (`CLAUDE.md`), over nasadenie `deploy-app`. **Záväzné:** nič nevymýšľaj, drž štýl appky; mení sa **len** to, čo je nižšie. Čo nie je jasné, spýtaj sa.

**Čítaj:** `docs/design.md` časť 4 (bloky „Zmena 2026-11-19“, „2026-11-18 20:12“, „19:31“, „večer po 068“), časť 5 (stránka akcie), časť Môj účet; report 071; `web/src/components/EventRow.tsx`, `web/src/pages/EventPage.tsx` (obrázok a prekrytie Plagát), `web/src/pages/MyAccountPage.tsx`, `web/src/core/store.ts` (`detectLanguage`).

### 1. Riadok v Akciách: najviac 4 štítky, bez rozplynutia
- V riadku **Akcií** je **najviac 4 pilulky vrátane pilulky s ikonou typu** (ikona + najviac 3 štítky).
- **Rozplynutie (fade) na konci riadku štítkov sa ruší.** Zobrazí sa len štítok, ktorý sa celý zmestí; ten, ktorý by sa nezmestil, a všetky za ním sa nezobrazia. Pilulka s ikonou sa zobrazí vždy.
- Poradie štítkov bez zmeny. Karta na mape a program podniku bez zmeny.

### 2. Jazyk
- **Automaticky podľa zariadenia:** prejdi `navigator.languages` (celý zoznam, v poradí) a vyber prvý z `cs`, `sk`, `en`; ak žiadny, **angličtina**. Uložená voľba používateľa má prednosť ako doteraz.
- **Poradie v Môj účet → jazyk: čeština, slovenčina, angličtina** (dnes `sk`, `cs`, `en`).

### 3. Dátum v Môj účet → Akcie
- Dnes sa ukazuje surový dátum `2026-11-21`. Zobraz **deň. mesiac. rok** – `21. 11. 2026` (vo všetkých jazykoch rovnako). Ostatné v riadku bez zmeny.

### 4. Obrázok na stránke akcie (detail)
- Dnes je obrázok na výšku celý s prázdnymi pruhmi po stranách. Nové: **obrázok vyplní celú šírku**, výška najviac 50 % obrazovky ako dnes; ak je obrázok vyšší, **oreže sa zospodu – zarovnanie na stred hore** (`object-fit: cover`, `object-position: center top`). Rozhodnutie hlavného chatu: na plagátoch je dôležité hore (meno, názov), dole býva dátum a miesto, ktoré sú v texte stránky.
- Obrázok na šírku alebo nižší ako 50 % obrazovky: bez zmeny (celý na šírku).
- Rámik má vyhradenú výšku od prvého snímku ako po 069 a `5cd07ad` (bez preblikávania).
- Celý obrázok ostáva cez tlačidlo **Plagát**.

### 5. Plagát: priblíženie
- V prekrytí Plagát: **priblíženie dvoma prstami** (až 4×), **dvojité ťuknutie** prepína 1× / 2,5× v mieste ťuknutia, pri priblížení **posúvanie prstom**, obrázok nevyjde mimo okrajov. Pri 1× ako dnes (celý, `contain`).
- **Zatvorenie len šípkou späť a systémovým späť** (dnes zatvorí aj ťuk kamkoľvek – kolidovalo by s dvojitým ťuknutím).
- Bez ťažkej knižnice; ak to bez nej nejde spoľahlivo, malá knižnica je OK, zapíš do `decisions.md`.

## Overenie a report
- `npm test`, `npm run build`; číslo nasadenia (`deploy-app`).
- Snímky JPEG 390 × 844 do `docs/tasks/072/`: `akcie-dnes.jpg`, `detail-plagat-na-vysku.jpg`, `detail-na-sirku.jpg`, `moj-ucet-akcie.jpg`, `moj-ucet-jazyk.jpg`, `plagat-zoom.jpg` (2,5× po dvojitom ťuknutí).
- Test `detectLanguage` (napr. `['de-DE','cs-CZ']` → `cs`, `['de','sk-SK']` → `sk`, `['en-US','cs-CZ']` → `en`, `['de']` → `en`).
- Report: čo hotové, otvorené body.

## Report

**2026-11-19**, commit `dcbf71f` (práca), report v nasledujúcom commite. Nasadenie `deploy-app` #47 (run 44420819104) – success. Pipeline sa nespúšťala (len `web/`), dátové čísla sa preto neuvádzajú.

### Hotové
1. **Riadok v Akciách** (`BadgeTagRow`): ikona + najviac 3 štítky, rozplynutie zrušené. Štítok, ktorý sa celý nezmestí, sa nezobrazí a ani žiadny za ním (`flex-wrap` s výškou jedného riadku, `overflow: hidden`). Poradie bez zmeny. `BadgeTagRow` sa používa len v riadku Akcií, karta na mape a program podniku sa nemenili.
2. **Jazyk:** `pickLanguage(navigator.languages)` prejde celý zoznam v poradí, prvý z cs/sk/en, inak en; uložená voľba má prednosť. Poradie v Môj účet: čeština, slovenčina, angličtina.
3. **Dátum v Môj účet → Akcie:** `21. 11. 2026` (`formatDateDMY`, bez úvodných núl, napr. `5. 12. 2026`).
4. **Obrázok v detaile:** plná šírka, `aspect-ratio` z `image_detail_size` + `max-height: 50vh` (rámik vyhradený od prvého snímku), `object-fit: cover`, `object-position: center top`. Overené Playwrightom na 390 × 844: plagát na výšku 390 × 422 px (= 50 %), obrázok na šírku 390 × 204 px (celý).
5. **Plagát:** nový komponent `PosterZoom` bez knižnice – dva prsty (1–4×), dvojité ťuknutie 1× / 2,5× v mieste ťuknutia, posun pri zoome, obrázok nevyjde z okrajov. Ťuk na plochu už nezatvára; zatvára šípka a systémové späť (história ako doteraz). Overené: jeden ťuk prekrytie nezavrie, dvojitý klik → `translate(0px, 183px) scale(2.5)`.

### Testy a build
- `npm test`: 14 súborov, 205 testov OK; nový `src/core/language.test.ts` (`['de-DE','cs-CZ']`→cs, `['de','sk-SK']`→sk, `['en-US','cs-CZ']`→en, `['de']`→en, `[]`→en; dátum).
- `npm run build`: OK.

### Snímky
`tests/playwright/screenshots-072.spec.ts` (dáta a obrázky z Pages, čas 19. 11. 17:00, spustené z `web/` s `NODE_PATH=web/node_modules`) → `docs/tasks/072/`: `akcie-dnes.jpg`, `detail-plagat-na-vysku.jpg` (MeetFactory, Good Times Only, 796 × 1200), `detail-na-sirku.jpg` (Cross Club, Moordoor, 1200 × 627), `moj-ucet-akcie.jpg`, `moj-ucet-jazyk.jpg`, `plagat-zoom.jpg` (2,5× po dvojitom ťuknutí). Snímky som neposudzoval.

### Rozhodnutia (zapísané v `decisions.md`)
- Zoom bez knižnice (vlastné pointer events); štítky čisto v CSS bez merania v JS; dátum bez úvodných núl.

### Otvorené
- Priblíženie dvoma prstami je overené len logikou a dvojklikom myšou v Playwrighte, nie na skutočnom telefóne – treba vyskúšať na zariadení.
