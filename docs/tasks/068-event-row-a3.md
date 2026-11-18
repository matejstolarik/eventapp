# 068: Riadok akcie A3 s krúžkom typu, celý obrázok v detaile

## Zadanie

> **Doplnok 2026-11-18 15:35 (Matej, pred spustením):** odznaky pre teba a new nie sú na obrázku, ale prvé v riadku štítkov (**new prvé** – doplnok 15:50, potom pre teba s ružovými iskrami). Riadok dátum · čas · miesto vždy na jednom riadku. Platí aj pre kartu na mape.

**Schválené Matejom 2026-11-18** (návrh v chate, varianty A/B/A2/A3; zvolené A3 s krúžkom typu). **Spusti až po 067.** Dizajn je zapísaný v `docs/design.md` (commit `75242c7`): časť 4 blok „Zmena 2026-11-18 – riadok akcie A3“, časť 7 „Zmena 2026-11-18“. Appka má byť **takmer 1:1 podľa design.md**; čo nie je jasné alebo nejde, zastav sa a spýtaj Mateja.

**Čítaj:** `docs/design.md` časť 1 (farby, Ikony), časť 3, časť 4 (blok 2026-11-18 a pravidlá, ktoré ostávajú: odznaky, prázdny stav, scroll), časť 6 (program podniku), časť 7; `web/src/pages/EventsPage.tsx`, `EventPage.tsx`, `VenuePage.tsx`, `MyAccountPage.tsx`, `web/src/components/EventPanel.tsx`, `web/src/core/eventType.ts` (farby, `eventTags`), ikony pinov na mape (`web/src/map/markers.ts`, `docs/design/icons/`); `pipeline/thumbs.py`.

### 0. Možnosť návratu
- Pred prvou zmenou vytvor na aktuálnom `main` git tag **`design-pre-068`** a pushni ho (`git push origin design-pre-068`). Žiadny prepis histórie. Návrat = `git revert` commitov 068 (napíš do reportu presný príkaz).

### 1. Náhľad 4 : 3 (pipeline)
- `image_thumb` akcie: **640 × 480 (4 : 3)** namiesto štvorca 480. **Pravidlo podľa tvaru zdroja (Matej 2026-11-18):** obrázok **na výšku** (šírka / výška < 0,8, napr. plagáty 2 : 3, 3 : 4) sa **neoreže** – celý plagát vo výške náhľadu v strede, po stranách ten istý obrázok zväčšený, rozmazaný a stmavený (výplň, ako obaly albumov). **Všetko ostatné** (na šírku, štvorec, banner) = **stredový výrez 4 : 3**. Hranicu 0,8 napíš ako konštantu; v reporte počet obrázkov podľa pravidla a 3 príklady z každej skupiny (id + pomer strán) na Matejovu kontrolu v appke. Testy na syntetických obrázkoch (2 : 3, 4 : 5, 1 : 1, 16 : 9, 3 : 1). Rovnaká cache/hash logika ako v 066; jednorazovo zvýš limit, aby sa prepočítali všetky (napíš o koľko), potom vráť. `image_detail` bez zmeny. `data-model.md` aktualizuj.

### 2. Riadok A3 (Akcie, program podniku, Môj účet → Akcie)
- Jeden spoločný komponent riadku podľa design.md 4 (blok 2026-11-18): obrázok 4 : 3 vľavo (45 %), názov, „dátum · čas · miesto“, sivé štítky; krúžok typu v ľavom hornom rohu obrázka; odznaky **new** (biela pilulka, vždy prvá) a **pre teba** (pilulka s ružovými iskrami `#FF4D8D`, za new) na začiatku riadku štítkov, nie na obrázku (design.md zmena 2026-11-18, doplnok 15:35); riadok „dátum · čas · miesto“ vždy na jednom riadku, skracuje sa len miesto; bez obrázka plocha `EVENT_TYPE_DARK` s ikonou.
- **Krúžok typu:** použi **tie isté ikony ako piny na mape** (rovnaké SVG/komponent, kultúra podľa podtypu), nie novú sadu. Má pôsobiť elegantne a ako súčasť appky: ikona opticky vycentrovaná, ťah ako na pine, správny kontrast ikony na všetkých štyroch farbách, obrys 2 px `#111118` aby bol čitateľný na svetlých aj farebných plagátoch.
- Ostatné správanie Akcií ostáva (obdobie, Pre teba, Nové, hľadanie, zoradenie, kompaktná lišta pri scrolle, šípka navrch, obnovenie potiahnutím, prázdny stav).

### 3. Karta akcie na mape
- Podľa design.md 3 + blok 2026-11-18: obrázok 4 : 3 (šírka 120) s krúžkom typu, sivé štítky. Ostatné (šípky, ťahanie medzi akciami, bodky) bez zmeny.

### 4. Stránka akcie
- Podľa design.md 7 „Zmena 2026-11-18“: celý obrázok bez orezu (`image_detail`, záloha `image_url`), max 70 % výšky obrazovky, vycentrovaný na `#111118`; krúžok typu tesne v pravom hornom rohu obrázka (36 / ikona 20, 8 px od okrajov); **v detaile bez odznakov new a pre teba**; štítky s farebným textom typu, **bez prvého plnofarebného štítku typu**; bez štítkov jeden štítok s názvom typu. Tlačidlo Plagát ostáva.

## Overenie a report
- `npm test`, `npm run build`, `pytest -q`; číslo nasadenia a behu pipeline.
- Snímky (Playwright, `tests/playwright/`, JPEG 390 × 844, skutočné `events.json` z Pages) do `docs/tasks/068/`: `akcie-dnes.jpg`, `akcie-scroll.jpg` (kompaktná lišta), `akcia-bez-obrazka.jpg` (ak je v dátach), `mapa-karta.jpg`, `program-podniku.jpg` (Cross Club alebo Archa+), `moje-akcie.jpg` (s 2 uloženými), `detail-banner.jpg` (široký obrázok, napr. Forum Karlín), `detail-plagat.jpg` (na výšku, napr. MeetFactory), `detail-bez-stitkov.jpg` (ak je v dátach).
- Report: čo je hotové, odchýlky od design.md (ak nejaké) a prečo, príkaz na návrat, otvorené body.

## Report

**2026-11-18** · commity `6906356` (pipeline 4 : 3), `4aa3a88` (frontend, snímky, decisions; limit späť 150) · tag `design-pre-068` na `bd8f422` (pushnutý) · beh pipeline **44353927769** (úspech) · nasadenie appky **Deploy web app 44358005935** (úspech).

**Návrat:**
```bash
git revert --no-edit 4aa3a88 6906356 && git push
```
(potom ďalší beh pipeline prepočíta náhľady naspäť na štvorec – limit treba znova jednorazovo zvýšiť na 400; alebo stav súborov z tagu: `git diff design-pre-068 -- web/src pipeline`).

### Hotové
1. **Náhľad 4 : 3** – `pipeline/thumbs.py`: `image_thumb` 640×480, `PORTRAIT_MAX_RATIO = 0.8`; na výšku (w/h < 0,8) celý plagát v strede na výplni (ten istý obrázok cover 4 : 3, blur 24 px, jas 0,45), ostatné stredový výrez 4 : 3. Hash obsahuje `640x480r0.8` (rovnaká cache logika ako 066). Limit jednorazovo **400** (o 250 viac), v behu 44353927769 `new=335 cache=0 errors=0 deferred=0 (portrait=35 crop=300)`, potom späť **150**. `image_detail` bez zmeny. Testy na syntetických obrázkoch 2 : 3, 4 : 5, 1 : 1, 16 : 9, 3 : 1 (`tests/test_event_thumbs.py`). `data-model.md` aktualizovaný.
2. **Riadok A3** – nový `web/src/components/EventRow.tsx` (riadok, krúžok `TypeRing`, obrázok `EventImage43`, `BadgeTagRow`, `MetaLine`), použitý v Akciách, programe podniku a Môj účet → Akcie. Krúžok = presne SVG pinov (`typeIconSvg` v `map/markers.ts`), 28 / ikona 16 v `EVENT_TYPE_DARK`, obrys 2 px `#111118`, 6 px od rohu. new (biela) → pre teba (ružové iskry) → sivé štítky; nezmestené štítky miznú na konci. „dátum · čas · miesto“ na jednom riadku, skracuje sa len miesto. Bez obrázka plocha `EVENT_TYPE_DARK` s ikonou vo farbe typu, bez krúžku. Ostatné správanie Akcií nezmenené.
3. **Karta na mape** – obrázok 4 : 3 šírka 120 s krúžkom, new / pre teba na začiatku riadku štítkov, sivé štítky, riadok „miesto · čas · vzdialenosť“ na jednom riadku.
4. **Stránka akcie** – celý obrázok (`image_detail`, pri chybe `image_url`), max 70vh, vycentrovaný na `#111118`, bez stmavnutia; krúžok 36 / 20 vpravo hore 8 px; bez new / pre teba; všetky štítky farebným textom typu, plnofarebný štítok zrušený; bez štítkov jeden štítok s typom (`eventTags`). Tlačidlo Plagát ostáva (presunuté do pravého dolného rohu obrázka, 12 px).

### Rozhodnutia (zapísané v `decisions.md`)
- Ikona krúžku z pinov (React ikony v `web/src/icons` majú iné masky kultúry).
- Karta na mape: štítky ostali veľké (32 px, posúvateľné) podľa časti 3, zmenená len farba a odznaky.
- Program podniku: riadok A3 ukazuje aj meno miesta (rovnaký riadok podľa design 4) a cenu už nie – **na Matejovu kontrolu**, meno je na profile miesta nadbytočné.
- Stránka akcie bez obrázka: ostal štvorec vo farbe typu s ikonou (design 7 tento prípad nemení), bez krúžku.

### Čísla
Príkaz (events.json z Pages po behu 44353927769, `generated_at 2026-11-18T18:16:58+01:00`; pomer strán z `image_detail` = pomer zdroja):
```bash
python -X utf8 picks068.py docs/tasks/068/picks.json   # skript v scratchpade, stiahne events.json + image_detail z https://matejstolarik.github.io/eventapp/
```
- 377 akcií, 335 s `image_thumb` aj `image_detail`; **na výšku (celé na výplni) 35**, **výrez 300**.
- Príklady na výšku: `meetfactory-2027-04-02-fource-nieve-ella` 675×1200 (0,56), `archa-plus-2027-02-16-a-u-banger-factory-w-ursula-sereghy` 800×1200 (0,67), `citarna-unijazz-2026-11-26-syrovy-tony-katka-sarkozi` 848×1200 (0,71).
- Príklady výrez: `meetfactory-2027-02-24-live-nation-jacob-banks` 960×1200 (0,80 – presne na hranici, výrez), `kasarna-karlin-2026-11-17-i-m-not-everything-i-want-to-be` 1200×1200 (1,00), `forum-karlin-2026-12-17-dalibor-janda` 1200×630 (1,90).

### Overenie
- `npm test` 199 passed, `npm run build` OK, `pytest -q` 627 passed.
- Snímky (`tests/playwright/screenshots-068.spec.ts`, dáta a obrázky z Pages, čas 18. 11. 18:00) v `docs/tasks/068/`: `akcie-dnes.jpg`, `akcie-scroll.jpg`, `akcia-bez-obrazka.jpg` (`cross-club-2026-11-18-krizovatka`), `mapa-karta.jpg` (Kasárna Karlín, obľúbené → pre teba), `program-podniku.jpg` (Cross Club), `moje-akcie.jpg` (2 uložené Cross Club), `detail-banner.jpg` (`forum-karlin-2026-12-17-dalibor-janda`), `detail-plagat.jpg` (`meetfactory-2027-04-02-fource-nieve-ella`), `detail-bez-stitkov.jpg` (`kasarna-karlin-2026-11-22-clothing-swap`). Snímky som neposudzoval vizuálne (pravidlo CLAUDE.md) – kontrola dizajnu je na Matejovi.

### Otvorené
- Meno miesta v riadku programu podniku – ponechať / skryť?
- Vizuálna kontrola krúžku (optické centrovanie, hrúbka ťahu pri 16 px) na snímkach.
