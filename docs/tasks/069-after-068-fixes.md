# 069: Úpravy po 068 – vrátenie programu podniku a Môj účet, farebné štítky bez krúžku, pevný riadok, preblikávanie detailu, oddeľovač

## Zadanie

> **Oprava 19:05:** šírka obrázka 112 px bol odhad hlavného chatu – neplatí; rozmer sa počíta (časť 3).
> **Matej 19:00 – záväzné pre celú úlohu:** nič nevymýšľaj. Drž sa štýlu, ktorý appka má (existujúce komponenty, farby, písma, veľkosti, zaoblenia, medzery). Čo sa vracia (program podniku, Môj účet → Akcie, farebné štítky, plnofarebný štítok typu v detaile), **vráť presne tak, ako bolo pred 068** (`git show design-pre-068:…`), bez „vylepšení“. Ak niečo v zadaní nie je jasné, nepredpokladaj – spýtaj sa.

> Jediné platné zadanie 069 (`069-event-row-x.md` je zlúčené sem a neplatí). Doplnok 19:00: obrázok v detaile max 50 % výšky obrazovky; príčina oddeľovača v časti 5.

**Schválené Matejom 2026-11-18 večer** po teste 068. Dizajn: `docs/design.md` časť 4, blok „Zmena 2026-11-18 večer po 068“ (platí pred blokom A3), časť 7 (krúžok zrušený). Takmer 1:1; čo nie je jasné, spýtaj sa.

**Čítaj:** design.md blok „Zmena 2026-11-18 večer po 068“, časť 3, 6, 7; report 068; `web/src/components/EventRow.tsx`, `EventPanel.tsx`, `pages/EventPage.tsx`, `VenuePage.tsx`, `MyAccountPage.tsx` (alebo kde je Môj účet → Akcie), `core/eventType.ts`; stav pred 068: `git show design-pre-068:<súbor>`.

Každá časť vlastný commit.

### 1. Preblikávanie pri otvorení akcie (najprv diagnostika)
- Matej: po ťuknutí na akciu stránka „preblikne“ – najprv sa ukáže posunutá (obsah nižšie/vyššie), až potom správne hore.
- **Hypotéza (hlavný chat, z kódu, neoverená):** od 068 má obrázok v `EventPage` výšku podľa načítaného obrázka (`width/height: auto`, `maxHeight: 70vh`), predtým pevný štvorec (`paddingTop: 100%`). Kým sa `image_detail` (~1200 px) stiahne, má výšku 0 → text sa vykreslí hore, po načítaní obrázka skočí nadol (posun rozloženia). Druhá možnosť: prekrytie `position: fixed` + vnútorný `overflowY: auto` dedí posun.
- **Over** Playwrightom: snímky 0 / 100 / 300 / 800 ms po ťuknutí na akciu (pomalé sieťové spojenie, napr. throttling „Fast 3G“), napíš, čo sa deje. Oprav podľa skutočnej príčiny. Ak je to hypotéza: pipeline zapíše rozmery `image_detail` (napr. `image_detail_size: [w, h]`, zmena dátového modelu schválená týmto zadaním – zapíš do `data-model.md`) a detail si vopred vyhradí miesto s týmto pomerom (**max 50vh**); dovtedy tmavá plocha alebo náhľad `image_thumb`. Stránka akcie sa vždy otvára navrchu.

### 2. Program podniku a Môj účet → Akcie presne ako pred 068
- Vráť komponenty a vzhľad z `design-pre-068` (vrátane farebných štítkov, rozloženia, dátumu ako hlavnej časti v programe podniku). Náhľad je teraz 4 : 3 – v starých štvorcových políčkach `object-fit: cover`. Nič iné nemeň.

### 3. Riadok v Akciách (design.md blok večer po 068)
- **Bez krúžku typu**; štítky farebným textom typu (`EVENT_TYPE_TAG_TEXT`) na `#2A2838`; bez štítkov jeden štítok s typom.
- **Názov akcie 14 px** (Matej 19:00; hrúbka, písmo a farba ako dnes v appke), max. 2 riadky s „…“.
- **Pevná výška riadku** = 2 riadky názvu + riadok „dátum · čas · miesto“ + riadok štítkov; **výška obrázka = výška textového bloku pri plnom riadku** (2 riadky názvu 14 px + riadok „dátum · čas · miesto“ + riadok štítkov vrátane medzier, s písmami a riadkovaním, ktoré appka používa – **vypočítaj, nevymýšľaj číslo**), **šírka = výška × 4/3** (náhľad 4 : 3 sa zobrazí celý, bez ďalšieho orezu), zaoblenie 8; výsledné px napíš do reportu a do design.md; pri 1-riadkovom názve textový blok zvislo vycentrovaný; štítky jeden riadok s rozplynutím vpravo.
- **new** = biela pilulka vpravo hore na obrázku; **pre teba** = prvá pilulka v štítkoch (ružové iskry).

### 4. Karta na mape a stránka akcie
- Karta na mape: krúžok preč, štítky farebným textom typu; zvyšok z 068 ostáva.
- Stránka akcie: krúžok preč; **prvý štítok = plnofarebný štítok typu** (`koncert`, `párty`, `DJ`, pri kultúre podtyp; plná farba typu, tmavý text – presne ako pred 068, slúži ako legenda farieb; Matej 18:57), za ním štítky farebným textom typu; bez new a pre teba. Obrázok podľa časti 1, **najviac 50 % výšky obrazovky** (zmena z 70 %, Matej 18:55; celý obrázok na ťuk cez Plagát).

### 5. Oddeľovač „·“
- Matej: medzery okolo bodky sú nerovnomerné (Miesta: chýba za bodkou; Akcie: chýba; karta na mape: chýba pred). **Koreňová príčina (z kódu):** medzera na začiatku alebo konci textu v položke `display:flex` sa zahodí – `EventRow.MetaLine` má `' · '` na konci prvého `span` (chýba medzera za bodkou), `EventPanel` má `' · 20:00'` na začiatku druhého `span` (chýba pred bodkou); over aj `VenuePage` (adresa · vzdialenosť), `EventPage` (`grep -rn "·" web/src`). Nájdi všetky miesta, kde sa skladá „x · y“, a nahraď **jednou spoločnou funkciou**: obyčajná medzera pred aj za „·“, žiadne extra okraje. Test. Skontroluj na snímkach.

## Overenie a report
- `npm test`, `npm run build`, (`pytest -q`, ak sa menila pipeline); číslo nasadenia.
- Snímky do `docs/tasks/069/` (JPEG 390 × 844, skutočné dáta): `akcie-dnes.jpg`, `akcie-jednoriadkovy-nazov.jpg` (výrez s 1- a 2-riadkovým názvom vedľa seba), `mapa-karta.jpg`, `program-podniku.jpg`, `moje-akcie.jpg`, `detail.jpg`, `miesta.jpg` (oddeľovač) a 4 snímky z diagnostiky časti 1 (pred opravou) + 4 po oprave.
- Report: príčina preblikávania (overená), čo sa zmenilo, otvorené body.
