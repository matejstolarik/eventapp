# 068: Riadok akcie A3 s krúžkom typu, celý obrázok v detaile

## Zadanie

**Schválené Matejom 2026-11-18** (návrh v chate, varianty A/B/A2/A3; zvolené A3 s krúžkom typu). **Spusti až po 067.** Dizajn je zapísaný v `docs/design.md` (commit `75242c7`): časť 4 blok „Zmena 2026-11-18 – riadok akcie A3“, časť 7 „Zmena 2026-11-18“. Appka má byť **takmer 1:1 podľa design.md**; čo nie je jasné alebo nejde, zastav sa a spýtaj Mateja.

**Čítaj:** `docs/design.md` časť 1 (farby, Ikony), časť 3, časť 4 (blok 2026-11-18 a pravidlá, ktoré ostávajú: odznaky, prázdny stav, scroll), časť 6 (program podniku), časť 7; `web/src/pages/EventsPage.tsx`, `EventPage.tsx`, `VenuePage.tsx`, `MyAccountPage.tsx`, `web/src/components/EventPanel.tsx`, `web/src/core/eventType.ts` (farby, `eventTags`), ikony pinov na mape (`web/src/map/markers.ts`, `docs/design/icons/`); `pipeline/thumbs.py`.

### 0. Možnosť návratu
- Pred prvou zmenou vytvor na aktuálnom `main` git tag **`design-pre-068`** a pushni ho (`git push origin design-pre-068`). Žiadny prepis histórie. Návrat = `git revert` commitov 068 (napíš do reportu presný príkaz).

### 1. Náhľad 4 : 3 (pipeline)
- `image_thumb` akcie: **stredový výrez 4 : 3, 640 × 480** (namiesto štvorca 480). Rovnaká cache/hash logika ako v 066; jednorazovo zvýš limit, aby sa prepočítali všetky (napíš o koľko), potom vráť. `image_detail` bez zmeny. `data-model.md` aktualizuj.

### 2. Riadok A3 (Akcie, program podniku, Môj účet → Akcie)
- Jeden spoločný komponent riadku podľa design.md 4 (blok 2026-11-18): obrázok 4 : 3 vľavo (45 %), názov, „dátum · čas · miesto“, sivé štítky; krúžok typu v ľavom hornom rohu obrázka; odznaky pre teba (vpravo hore) a new (vpravo dole); bez obrázka plocha `EVENT_TYPE_DARK` s ikonou.
- **Krúžok typu:** použi **tie isté ikony ako piny na mape** (rovnaké SVG/komponent, kultúra podľa podtypu), nie novú sadu. Má pôsobiť elegantne a ako súčasť appky: ikona opticky vycentrovaná, ťah ako na pine, správny kontrast ikony na všetkých štyroch farbách, obrys 2 px `#111118` aby bol čitateľný na svetlých aj farebných plagátoch.
- Ostatné správanie Akcií ostáva (obdobie, Pre teba, Nové, hľadanie, zoradenie, kompaktná lišta pri scrolle, šípka navrch, obnovenie potiahnutím, prázdny stav).

### 3. Karta akcie na mape
- Podľa design.md 3 + blok 2026-11-18: obrázok 4 : 3 (šírka 120) s krúžkom typu, sivé štítky. Ostatné (šípky, ťahanie medzi akciami, bodky) bez zmeny.

### 4. Stránka akcie
- Podľa design.md 7 „Zmena 2026-11-18“: celý obrázok bez orezu (`image_detail`, záloha `image_url`), max 70 % výšky obrazovky, vycentrovaný na `#111118`; krúžok typu vpravo hore (36 / ikona 20); štítky s farebným textom typu, **bez prvého plnofarebného štítku typu**; bez štítkov jeden štítok s názvom typu. Tlačidlo Plagát ostáva.

## Overenie a report
- `npm test`, `npm run build`, `pytest -q`; číslo nasadenia a behu pipeline.
- Snímky (Playwright, `tests/playwright/`, JPEG 390 × 844, skutočné `events.json` z Pages) do `docs/tasks/068/`: `akcie-dnes.jpg`, `akcie-scroll.jpg` (kompaktná lišta), `akcia-bez-obrazka.jpg` (ak je v dátach), `mapa-karta.jpg`, `program-podniku.jpg` (Cross Club alebo Archa+), `moje-akcie.jpg` (s 2 uloženými), `detail-banner.jpg` (široký obrázok, napr. Forum Karlín), `detail-plagat.jpg` (na výšku, napr. MeetFactory), `detail-bez-stitkov.jpg` (ak je v dátach).
- Report: čo je hotové, odchýlky od design.md (ak nejaké) a prečo, príkaz na návrat, otvorené body.
