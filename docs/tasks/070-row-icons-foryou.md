# 070: Ikona typu pri štítkoch, pre teba v rohu obrázka, obrázok 120 × 90

## Zadanie

**Schválené Matejom 2026-11-18 19:31.** **Záväzné:** nič nevymýšľaj, drž štýl appky; mení sa **len** to, čo je nižšie. Čo nie je jasné, spýtaj sa.

**Čítaj:** `docs/design.md` časť 4 (blok „Zmena 2026-11-18 večer po 068“), časť 3, 6; report 069; `web/src/components/EventRow.tsx`, `EventPanel.tsx` (karta na mape), `VenuePage.tsx` (program podniku), `web/src/map/markers.ts` (`typeIconSvg` – ikony pinov), `core/eventType.ts` (`EVENT_TYPE_TAG_TEXT`, podtypy kultúry).

### 1. Ikona typu ako prvý štítok
- **Naše ikony – presne tie isté ako na pinoch mapy** (`typeIconSvg` / rovnaké SVG; kultúra podľa podtypu: klapka, mikrofón stand-up, tanec, masky; koncert gitara, párty pohár, DJ gramofón). Žiadna iná sada ikon.
- Vzhľad: pilulka ako ostatné štítky (`#2A2838`, rovnaká výška a zaoblenie), v nej len ikona vo farbe `EVENT_TYPE_TAG_TEXT` typu, veľkosť opticky zladená s textom štítkov (cca 12–13 px, ťah ako na pine), vycentrovaná. Za ňou štítky farebným textom typu ako teraz.
- Kde: **riadok v Akciách**, **karta na mape**, **program podniku** (v programe podniku **len** pridať túto ikonu pred štítky, nič iné tam nemeniť).

### 2. Pre teba a new na obrázku
- **Pre teba** = ikona iskier vo farbe appky `#FF4D8D` **bez pozadia**, s **jemným čiernym obrysom** (cca 1–1,5 px), **vľavo hore** na obrázku (5 px od okrajov). Obrys musí byť **hladký a súvislý okolo celého tvaru** (napr. tá istá SVG ikona pod ňou s čiernym `stroke` a `stroke-linejoin: round`, alebo `paint-order: stroke`), nie tieň, nie zubaté posuny `drop-shadow`. Over na snímke zväčšenej 3× – ak vyzerá hrubo alebo zubato, uprav.
- **new** ostáva vpravo hore na obrázku (ako po 069).
- Platí v **Akciách** a na **karte na mape** (z riadku štítkov na mape new aj pre teba odstráň a daj ich na obrázok rovnako ako v Akciách).

### 3. Obrázok v riadku Akcií 120 × 90
- Riadok aj obrázok **90 px** výška, obrázok **120 px** šírka (4 : 3, rozhodnutie hlavného chatu – Matej to nechal na neho; 069 dal 106,67 × 80, Matejovi to príde malé). Textový blok zvislo vycentrovaný ako teraz. Ostatné rozmery riadku bez zmeny.

### Nemení sa
- Stránka akcie (detail), Môj účet, Miesta, mapa okrem karty.

## Overenie a report
- `npm test`, `npm run build`; číslo nasadenia.
- Snímky JPEG 390 × 844 do `docs/tasks/070/`: `akcie-dnes.jpg`, `mapa-karta.jpg` (akcia pre teba + new, ak je), `program-podniku.jpg`, a výrez obrázka s iskrami zväčšený 3× (`iskry-3x.png`) na tmavom aj svetlom plagáte.
- Report: čo hotové, otvorené body.
