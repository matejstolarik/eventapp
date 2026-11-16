# 050: Štítky s textom vo farbe typu, názov nad dátumom

## Zadanie

**Čítaj:** `design.md` časť 4: odsek Mriežka (body názov, dátum · čas, štítky a „Štítky akcie a typ“); časť 3 (riadok štítkov v karte); časť 6 (Program); časť 7 (druhý bod). V kóde: `core/eventType.ts`, `pages/EventsPage.tsx` (karta), `components/EventPanel.tsx` (karta na mape), `pages/VenuePage.tsx` (program), `pages/EventPage.tsx` (štítky).

Robí sa **po 048**. Úloha 049 je pozastavená, nerob ju. Každá časť vlastný commit.

### 1. Spoločná logika štítkov (`core/`)
- Funkcia (napr. `eventTags(event)`) vráti štítky na zobrazenie: podtypy kultúry (`theatre`, `dance`, `talk`, `comedy`, `film`, `opening`, `workshop`, `quiz`) prvé, potom žánre; **bez** `party`, `dj`, `concert`, `music`.
- Záloha: ak by zoznam bol prázdny, vráti formát typu (napr. `concert`), aby karta nebola bez štítku.
- Funkcia pre stránku akcie (napr. `primaryTypeTag(event)`): koncert/párty/DJ → ten formát; kultúra → prvý podtyp; typ `other` → nič.
- Farba textu štítku: `EVENT_TYPE_COLOR`, pre koncert (fialová) **`#A48BFF`** (len text štítkov; piny, čipy filtra a plochy ostávajú `#8B6CFF`). Napr. `EVENT_TYPE_TAG_TEXT`.
- Testy pre všetky prípady vrátane zálohy.

### 2. Mriežka Akcií
- Štítky na obrázku: tmavé pilulky, text vo farbe typu, bez štítku typu. Plnofarebný štítok typu zo 047 zruš.
- **Poradie v karte: názov, dátum · čas (sivý), miesto.**

### 3. Karta na mape
Riadok štítkov ako v mriežke: bez štítku typu, tmavé pilulky s textom vo farbe typu.

### 4. Program miesta
- Čas **sivý** (dnes vo farbe typu).
- Štítky: bez štítku typu, text vo farbe typu.

### 5. Stránka akcie
Prvý štítok plnou farbou typu s tmavým textom (`primaryTypeTag`, ak existuje), ostatné tmavé s textom vo farbe typu.

### Nemeniť
„pre teba“, „new“, piny, čipy typu vo filtri, štítky miesta (charakter) – ostávajú biele.

## Overenie
- `npm test` (`--reporter=dot`), build OK.
- Screenshoty (Playwright, `tests/playwright/`, JPEG 390 × 844 do `docs/tasks/050/`): `akcie-mriezka.jpg`, `mapa-karta.jpg`, `podnik-program.jpg`, `stranka-akcie-koncert.jpg`, `stranka-akcie-film.jpg`. Fixtúry musia mať aspoň pár akcií s obrázkom (doplň testovací obrázok do fixtúr, nie do dát), aspoň jednu kultúrnu akciu s podtypom a jednu akciu bez žánru (záloha).

## Report

**Dátum:** 2026-11-16  
**Commity:** db1fab3, a1db9f6, 462f08f, bc8d071, 8a6e308, 252a9ca

### Čo je hotové

**Časť 1 – Spoločná logika (`web/src/core/eventType.ts`):**
- `EVENT_TYPE_TAG_TEXT`: rovnaké ako `EVENT_TYPE_COLOR`, ale concert = `#A48BFF` (svetlejšia fialová pre čitateľnosť textu na tmavom pozadí)
- `eventTags(formats, genres)`: vráti culture subtypes (theatre, dance, talk, comedy, film, opening, workshop, quiz) + žánre; vylúči party/dj/concert/music; záloha = typ akcie ako string (napr. `'concert'` pre akciu bez žánrov)
- `primaryTypeTag(formats)`: concert/party/dj → type string; culture → prvý subtyp; other → null
- Testy: 176 passed (11 test files), vrátane 15 nových testov pre `eventTags` a `primaryTypeTag`

**Časť 2 – Mriežka Akcií (`EventsPage.tsx`):**
- Štítky na obrázku teraz používajú `eventTags()` (bez štítku typu)
- Všetky štítky: `rgba(17,17,24,0.9)` pozadie, text `EVENT_TYPE_TAG_TEXT[type]`
- Plnofarebný štítok typu zo 047 zrušený
- Poradie v karte: názov (13/700) → dátum · čas (sivý) → miesto

**Časť 3 – Karta na mape (`EventPanel.tsx`):**
- `eventTags()` namiesto formats+genres, tmavé pilulky `#2A2838`, text `EVENT_TYPE_TAG_TEXT[type]`
- Zrušený lokálny `FORMAT_COLORS` lookup a separátne `formatTags`/`genreTags`

**Časť 4 – Program miesta (`VenuePage.tsx`):**
- Čas vždy sivý `#8E8AA6` (zmena z predošlého: farba typu)
- `eventTags()` pre štítky v programe, text `EVENT_TYPE_TAG_TEXT[type]`

**Časť 5 – Stránka akcie (`EventPage.tsx`):**
- `primaryTypeTag()` → prvý štítok s `EVENT_TYPE_COLOR` pozadím a `EVENT_TYPE_DARK` textom
- Ostatné (culture subtypes bez primary + genres): `#2A2838` pozadie, `EVENT_TYPE_TAG_TEXT` text
- Zrušený lokálny `FORMAT_COLORS` lookup

**Screenshoty:**
- 5 JPEG 390×844, `docs/tasks/050/`: akcie-mriezka.jpg (82kB), mapa-karta.jpg (175kB), podnik-program.jpg (70kB), stranka-akcie-koncert.jpg (50kB), stranka-akcie-film.jpg (57kB)
- Playwright spustený: `NODE_PATH=web/node_modules npm run playwright -- ../tests/playwright/screenshots-050.spec.ts`; 5/5 passed (23.6s)

### Rozhodnutia

- Design.md sekcia 4 hovorí "dnes vo farbe typu" pre čas v programe, ale zmena 2026-11-16 večer v sekcia 6 explicitne mení na "čas sivý" — implementované podľa novšej zmeny (vždy sivý)
- Pre EventPage: `remainingTags` vypočítané priamo (culture subtypes bez primary + genres) namiesto `eventTags()`, aby sa predišlo duplicite primary tagu vo fallback scenári
- Playwright testy vyžadujú `NODE_PATH=D:\AI\eventapp\web\node_modules` kvôli umiestneniu node_modules mimo testového adresára

### Čo zostáva otvorené

- Farebný odtieň pre čas TODAY v programe miesta (design sekcia 6 hovorí "sivý" pre všetky — zmena z predošlého "dnes vo farbe typu") — implementované podľa aktuálnej zmeny v design.md
- Nič ďalšie — úloha kompletná
