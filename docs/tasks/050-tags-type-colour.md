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
