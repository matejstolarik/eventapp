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

## Report

**2026-11-18** · commity `8bab043` (časť 1 pipeline + diagnostika), `0e49f2e` (časť 5 `joinDot`), `3a6999c` (časť 2 program podniku, Môj účet), `ef2dded` (časti 3, 4 a frontend časti 1) + commit tohto reportu · beh pipeline **Daily pipeline 44367001649** (úspech, `generated_at 2026-11-18T19:19:52+01:00`) · nasadenie appky **Deploy web app 44367300336** (úspech, `ef2dded`).

Pozn.: zmeny v `EventPage.tsx` patria k častiam 1, 4 aj 5 v tom istom súbore, preto sú v jednom commite `ef2dded` spolu s riadkom (časť 3) a kartou na mape (časť 4).

### 1. Preblikávanie – príčina overená
- Playwright (`tests/playwright/diag-069.spec.ts`): Akcie, posun zoznamu o 600 px, ťuk na 4. riadok; stiahnutie `image_detail` spomalené o 1,5 s; každý snímok prehliadača sa zapisuje poloha titulku, `scrollTop` prekrytia a výška obrázka.
- **Pred opravou** (`diag-pred-log.json`, `[ms, y titulku, scrollTop, výška obrázka]`): `[57, 16, 0, 0]` → `[1738, 146, 0, 130]` – titulok sa vykreslí hore pri obrázku výšky 0 a po načítaní obrázka skočí o 130 px nadol. **Hypotéza potvrdená**; `scrollTop` je stále 0, posun zo zoznamu sa nededí (druhá možnosť vyvrátená).
- **Po oprave** (`diag-po-log.json`): `[57, 146, 0, 130]` a ďalej žiadna zmena – rámček obrázka má konečnú veľkosť od prvého snímku.
- Oprava: pipeline zapisuje `image_detail_size: [š, v]` (čítané zo zapísaného JPEG; `data-model.md` doplnený), stránka akcie vyhradí rámček `min(100 %, 50vh × š/v)` s `aspect-ratio`, kým obrázok príde, je tmavá plocha `#1C1C27`. `EventPage` má `key` = id akcie (vždy sa otvorí navrchu).
- Snímky `diag-pred-{0,100,300,800}ms.jpg` a `diag-po-…` (390 × 844; skutočné časy snímok 0 / 113 / 302 / 815 ms a 0 / 110 / 311 / 808 ms). „Pred“ je simulované tým, že skript z `events.json` odstráni `image_detail_size` (frontend sa potom správa ako pred opravou). Skok „pred“ nastáva až pri 1738 ms, teda po 4. snímke – na snímkach je stav „text hore bez obrázka“, samotný skok dokladá záznam. Prvý pokus o snímky (bez `scale: 'css'`) dal 4 rovnaké snímky (snímanie bolo pomalšie ako interval), druhý pokus je v poriadku.

### 2. Program podniku a Môj účet → Akcie
- `VenuePage.tsx` a `MyAccountPage.tsx` obnovené z `design-pre-068` (dátumový stĺpec, farebné štítky, čas, cena, štvorec 56 px s `object-fit: cover`). Jediná zmena: „·“ cez `joinDot` (rovnaký text).

### 3. Riadok v Akciách
- Bez krúžku; štítky 11/500 farebným textom typu na `#2A2838`, jeden riadok s rozplynutím vpravo (24 px); bez štítkov štítok s typom; **pre teba** prvá pilulka; **new** biela pilulka vpravo hore na obrázku (5 px, vzhľad odznaku new z mriežky pred 068: 18 px, 10/600).
- **Výpočet:** názov 14 px × 1,25 = 17,5 → 2 riadky 35; medzera 4; meta riadok 12 px Outfit `line-height: normal` = 15; medzera 4; štítky 2 + 20 → **riadok aj obrázok 80 px, obrázok šírka 106,67 px** (80 × 4/3), zaoblenie 8. Zmerané v prehliadači (`docs/tasks/069/meranie.json`): riadok 80, textový blok 80 (2 riadky) / 62,5 (1 riadok, vycentrovaný), obrázok 106,66. Zapísané v design.md časť 4.

### 4. Karta na mape a stránka akcie
- Karta na mape: krúžok preč (aj z `EventImage43`), štítky farebným textom typu; new / pre teba na začiatku štítkov a obrázok 4 : 3 ostávajú.
- Stránka akcie: krúžok preč; štítky presne ako pred 068 (prvý plnofarebný `primaryTypeTag`, potom podtypy a žánre farebným textom); bez new / pre teba; obrázok max 50vh. `TypeRing` odstránený (nikde sa nepoužíval).

### 5. Oddeľovač „·“
- `web/src/core/dot.ts` (`joinDot`, `DOT_SEP = ' · '`) + `dot.test.ts`. Použité: riadok Akcií (jeden text, „…“ len na konci = miesto), karta na mape (druhá časť `white-space: pre`), stránka akcie (dátum · čas, · vzdialenosť), profil miesta (adresa · vzdialenosť), Môj účet, počet akcií, dvojité meno pinu. `grep -rn "·" web/src` – žiadne ďalšie skladanie.

### Rozhodnutia (v `decisions.md`)
- Zástupca obrázka v detaile = tmavá plocha `#1C1C27` (nie `image_thumb`: má pomer 4 : 3, rámček by sa aj tak menil).
- Vzhľad odznaku new na obrázku a rozplynutie štítkov prevzaté z existujúcich prvkov pred 068.
- Pri zlyhaní `image_detail` (záloha `image_url`) rozmery nie sú známe → bez vyhradenia (zriedkavé).

### Čísla
Príkaz (`events.json` z Pages po behu 44367001649):
```bash
curl -s https://matejstolarik.github.io/eventapp/events.json -o ev069.json && python -X utf8 -c "import json;d=json.load(open('ev069.json',encoding='utf-8'));ev=d['events'];print(d['generated_at'],len(ev),sum(1 for e in ev if e.get('image_detail')),sum(1 for e in ev if e.get('image_detail_size')))"
```
- 377 akcií, 335 s `image_detail`, **335 s `image_detail_size`**, 0 s detailom bez rozmerov.

### Overenie
- `npm test` 201 passed (13 súborov), `npm run build` OK, `pytest -q` 629 passed.
- Rozmery proti webu: `https://matejstolarik.github.io/eventapp/img/events/detail/meetfactory-2027-04-02-fource-nieve-ella.jpg` = 675 × 1200, v dátach `[675, 1200]`; `…/forum-karlin-2026-12-17-dalibor-janda.jpg` = 1200 × 630, v dátach `[1200, 630]`.
- Snímky (`tests/playwright/screenshots-069.spec.ts`, dáta a obrázky z Pages, čas 18. 11. 19:30, JPEG 390 × 844): `akcie-dnes.jpg`, `akcie-jednoriadkovy-nazov.jpg` (výrez 390 × 196, susedné riadky s 1- a 2-riadkovým názvom), `mapa-karta.jpg` (Kasárna Karlín, obľúbené), `program-podniku.jpg` (Cross Club), `moje-akcie.jpg` (2 uložené Cross Club), `detail.jpg` (`meetfactory-2027-04-02-fource-nieve-ella`, plagát na výšku), `miesta.jpg`. Vizuálne som ich neposudzoval (pravidlo CLAUDE.md).

### Otvorené
- „Miesta: chýba za bodkou“: v zozname Miesta sa „·“ nevyskytuje; chyba bola v riadku 068 v programe podniku (profil miesta), ktorý sa vrátil na stav pred 068. `miesta.jpg` je zoznam Miesta. V profile miesta sa „adresa · vzdialenosť“ v praxi nezobrazuje, lebo `App.tsx` posiela `VenuePage` `userLocation={null}` (aj pred 068) – na rozhodnutie Matejovi, či to opraviť.
- Kľúč `venue.dot` v i18n sa už nepoužíva (ponechaný).
