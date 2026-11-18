# 070: Ikona typu pri štítkoch, pre teba v rohu obrázka, obrázok 120 × 90

## Zadanie

**Schválené Matejom 2026-11-18 19:31.** **Záväzné:** nič nevymýšľaj, drž štýl appky; mení sa **len** to, čo je nižšie. Čo nie je jasné, spýtaj sa.

**Čítaj:** `docs/design.md` časť 4 (blok „Zmena 2026-11-18 večer po 068“), časť 3, 6; report 069; `web/src/components/EventRow.tsx`, `EventPanel.tsx` (karta na mape), `VenuePage.tsx` (program podniku), `web/src/map/markers.ts` (`typeIconSvg` – ikony pinov), `core/eventType.ts` (`EVENT_TYPE_TAG_TEXT`, podtypy kultúry).

### 1. Ikona typu ako prvý štítok
- **Naše ikony – presne tie isté ako na pinoch mapy** (`typeIconSvg` / rovnaké SVG; kultúra podľa podtypu: klapka, mikrofón stand-up, tanec, masky; koncert gitara, párty pohár, DJ gramofón). Žiadna iná sada ikon.
- Vzhľad: pilulka ako ostatné štítky (`#2A2838`, rovnaká výška a zaoblenie), v nej len ikona vo farbe `EVENT_TYPE_TAG_TEXT` typu, veľkosť opticky zladená s textom štítkov (cca 12–13 px, ťah ako na pine), vycentrovaná. Za ňou štítky farebným textom typu ako teraz.
- Kde: **riadok v Akciách**, **program podniku** (v programe podniku **len** pridať túto ikonu pred štítky, nič iné tam nemeniť). **Na karte na mape nie** (Matej 19:42: ikony typu sú už na pinoch mapy).

### 2. Pre teba a new na obrázku
- **Pre teba** = ikona iskier vo farbe appky `#FF4D8D` **bez pozadia**, s **jemným čiernym obrysom** (cca 1–1,5 px), **vľavo hore** na obrázku (5 px od okrajov). Obrys musí byť **hladký a súvislý okolo celého tvaru** (napr. tá istá SVG ikona pod ňou s čiernym `stroke` a `stroke-linejoin: round`, alebo `paint-order: stroke`), nie tieň, nie zubaté posuny `drop-shadow`. Over na snímke zväčšenej 3× – ak vyzerá hrubo alebo zubato, uprav.
- **new** ostáva vpravo hore na obrázku (ako po 069).
- Platí v **Akciách** a na **karte na mape** (z riadku štítkov na mape new aj pre teba odstráň a daj ich na obrázok rovnako ako v Akciách).

### 3. Obrázok v riadku Akcií 120 × 90
- Riadok aj obrázok **90 px** výška, obrázok **120 px** šírka (4 : 3, rozhodnutie hlavného chatu – Matej to nechal na neho; 069 dal 106,67 × 80, Matejovi to príde malé). Textový blok zvislo vycentrovaný ako teraz. Ostatné rozmery riadku bez zmeny.

### Nemení sa
- Stránka akcie (detail), Môj účet, Miesta, mapa okrem karty.

## Overenie a report
- `npm test`, `npm run build`; číslo nasadenia (`deploy-app`).
- **Pipeline (`daily.yml`) nespúšťaj** – úloha mení len frontend, dáta sa nemenia; nasadenie appky ide cez `deploy-app` pri pushi do `web/`. Čísla v reporte netreba (Matej 19:42).
- Snímky JPEG 390 × 844 do `docs/tasks/070/`: `akcie-dnes.jpg`, `mapa-karta.jpg` (akcia pre teba + new, ak je; bez ikony typu v štítkoch), `program-podniku.jpg`, a výrez obrázka s iskrami zväčšený 3× (`iskry-3x.png`) na tmavom aj svetlom plagáte.
- Report: čo hotové, otvorené body.

## Report

**2026-11-18** · commit `d5ce6b1` (frontend, design.md, decisions.md, skript snímok) + commit tohto reportu · nasadenie appky **Deploy web app 44374456721** (úspech, `d5ce6b1`). Pipeline sa nespúšťala (len frontend).

### 1. Ikona typu ako prvý štítok
- `TypeIconPill` v `EventRow.tsx`: ikona z `typeIconSvg` (to isté SVG ako na pinoch, kultúra podľa podtypu), 13 px, farba `EVENT_TYPE_TAG_TEXT`, pilulka výška 20, zaoblenie 10, odsadenie 6 px, vycentrovaná. Ťah = ťah pinu (rovnaké SVG zmenšené).
- Riadok v Akciách: prvá pilulka `#2A2838`, za ňou štítky ako doteraz.
- Program podniku: pridaná len ikona – **za časom** (čas nie je štítok, je prvý v riadku) a pred štítkami; pilulka má farbu štítkov programu `#1E1D2A` (v programe sú štítky `#1E1D2A`, nie `#2A2838` – „ako ostatné štítky“ a „nič iné nemeniť“). Akcia bez času: ikona prvá.
- Karta na mape: bez ikony.

### 2. Pre teba a new na obrázku
- `OutlinedSparkleIcon`: iskry `#FF4D8D` 18 px bez pozadia; pod nimi tá istá ikona čiernym ťahom širším o 2 × 1,25 px, `stroke-linejoin/linecap: round` → súvislý hladký obrys. Vľavo hore 5 px. new vpravo hore ako po 069.
- Akcie aj karta na mape; z riadku štítkov karty new aj pre teba odstránené (riadok štítkov sa ukáže, len ak má akcia štítky – vždy má aspoň typ).
- Overené na výreze 3× (`iskry-3x-tmavy.png`, `iskry-3x-svetly.png` – dva súbory namiesto jedného `iskry-3x.png`): obrys súvislý, bez zubov, na tmavom aj svetlom plagáte čitateľný.

### 3. Riadok Akcií 120 × 90
- `ROW_IMG_H = 90`, `ROW_IMG_W = 120`. Zmerané v Playwright: riadok 90, obrázok 120 × 90, textový blok 80 (vycentrovaný).

### Overenie
- `npm test` 201 passed (13 súborov), `npm run build` OK.
- Snímky (`tests/playwright/screenshots-070.spec.ts`, dáta a obrázky z Pages, čas 18. 11. 19:30): `akcie-dnes.jpg`, `mapa-karta.jpg` (Kasárna Karlín ako obľúbené → pre teba), `program-podniku.jpg` (Cross Club), `iskry-3x-tmavy.png` / `iskry-3x-svetly.png` (všetky miesta obľúbené, obdobie 7 dní, najtmavší a najsvetlejší ľavý horný roh náhľadu: jas 1,9 a 250 z 255). Okrem výrezov iskier (zadanie ich žiada overiť) som snímky neposudzoval.

### Rozhodnutia (v `decisions.md`)
- Spôsob obrysu iskier a veľkosť 18 px; ikona v programe za časom a s farbou pilulky programu.

### Otvorené
- Či má new na karte mapy ostať aj pri karte bez štítkov – teraz je vždy na obrázku, takže to netreba riešiť.
- Pilulka ikony v programe podniku má `#1E1D2A` (farba štítkov programu), nie `#2A2838` zo zadania – ak má byť `#2A2838`, je to jedna hodnota v `VenuePage.tsx`.
