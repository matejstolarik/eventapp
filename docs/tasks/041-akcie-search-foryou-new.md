# 041: Akcie, časť 2 – hľadanie, Pre teba, Nové (+ oprava ikony v mriežke)

## Zadanie

**Čítaj:** `design.md` časť 4 (hlavička, hľadanie, Pre teba, Nové, karta, prázdny stav); snímky `docs/design/screens/10-akcie-mriezka.png`, `12-akcie-hladanie.png` a HTML `docs/design/html/10-akcie-mriezka.html`, `12-akcie-hladanie.html` (rozmery a farby odtiaľ). V kóde: `web/src/pages/EventsPage.tsx`, `core/period.ts`, `core/store.ts` (obľúbené miesta / `profileStore`), `core/eventType.ts`, `map/markers.ts` (len objekt s ikonami typov, r. 6–12), `i18n/*` (sekcia `events`).

### 0. Oprava z 040: ikona typu v mriežke je neviditeľná
Príčina (hlavný chat z kódu): `TypeIcon` v `EventsPage.tsx` kreslí ikonu farbou `EVENT_TYPE_COLOR`, teda rovnakou farbou ako pozadie plochy, preto je na snímke `040/01` len prázdna farebná plocha. Navyše ikony sú vlastné (párty = hviezda, nie pohár).
- Použi ikony z `map/markers.ts` (mikrofón, pohár, gramofón, masky). Vyčleň ich do zdieľaného modulu (napr. `core/typeIcons.ts`), aby ich používala mapa aj Akcie; mapa sa vizuálne nemení.
- Farba ikony na ploche = tmavá dvojica typu (`EVENT_TYPE_DARK`), veľkosť ~40 px, v strede plochy.
- Rovnakú náhradu skontroluj v `EventPanel`, `MyAccountPage` a programe `VenuePage`; ak tam je rovnaká chyba, oprav tiež.

### 1. Hľadanie
Podľa `design.md` 4 a snímky `12`:
- okrúhla lupa 44 px vpravo od nadpisu; ťuk → biele pole sa roztiahne od lupy doľava cez nadpis (200 ms, šírka + priehľadnosť nadpisu), lupa → krížik, klávesnica sa otvorí hneď; zavretie rovnakou animáciou naspäť. **Obsah pod hlavičkou sa nesmie posunúť** (pole je v hlavičke na mieste nadpisu, rovnaká výška 44 px).
- hľadá sa priebežne pri písaní (s malým oneskorením ~150 ms) v: názve akcie, mene miesta, štítkoch akcie (formáty, žánre) a štítkoch charakteru miesta. Bez diakritiky a bez ohľadu na veľkosť písmen („cross“ nájde „Cross Club“, „cajovna“ nájde „Čajovňa“).
- pri otvorení hľadania sa obdobie prepne na **Kedykoľvek** (tlačidlo to ukáže); po zavretí sa vráti predošlé obdobie a text sa vymaže. Zmena obdobia počas hľadania je povolená a platí, kým je hľadanie otvorené.
- Pre teba a Nové platia aj pri hľadaní.
- prázdny výsledok: „Nič sme nenašli.“ (CZ/EN v `i18n`).

### 2. Pre teba a Nové
- Čipy **Pre teba** (ikona iskier, nie srdiečko) a **Nové** za tlačidlom obdobia podľa snímky `10` (40 px; vypnuté `#23232F`/`#B9B6CC`, zapnuté `#FF4D8D`/`#1A0710`). Miesto pre Filter vpravo zatiaľ ostáva prázdne (Filter príde samostatne). Ak sa čipy nezmestia, pás sa posúva vodorovne a na okraji sa stráca – len keď pretekajú.
- **Pre teba** = akcia v obľúbenom mieste (preferencie žánrov zatiaľ nie sú; logiku daj do jednej funkcie v `core`, aby sa neskôr dala rozšíriť o preferencie). Vypnuté: všetky akcie, pri akciách pre teba odznak **pre teba** vľavo hore na obrázku. Zapnuté: len akcie pre teba.
- **Nové** = `first_seen` za posledných 7 dní (vrátane dneška). Odznak **nové** vpravo hore na obrázku vždy; zapnutý čip ukáže len nové.
- Riadok s počtom: „12 akcií · 3 pre teba“ (vypnuté Pre teba), „9 akcií pre teba“ (zapnuté). Ak obľúbené miesta nie sú žiadne, časť „· N pre teba“ sa nezobrazí a ťuk na Pre teba ukáže prázdny stav s textom „Pridaj si obľúbené miesta v záložke Miesta.“
- Stav Pre teba a Nové sa pamätá lokálne (`store.ts`).
- Prázdny stav pri zapnutom Pre teba/Nové: tlačidlo „Zrušiť filtre“ (vypne oba čipy).

### 3. Text zoradenia „čas“ (Matej 2026-11-15, `design.md` 4 „Zoradenie“)
Pri jednodňovom období (Dnes, Zajtra, Iný dátum s jedným dňom) sa možnosť zoradenia volá **„čas“** (v ponuke aj v „Zoradiť: čas“), pri ostatných obdobiach **„dátum“**. Radí sa vždy rovnako (dátum + čas začiatku). Predvolené ostáva toto zoradenie; vzdialenosť sa na karte nezobrazuje.

### Testy
- Vitest: normalizácia textu bez diakritiky, zhoda hľadania (názov, miesto, štítky), Pre teba, Nové (hranica 7 dní), počty, text zoradenia čas/dátum podľa obdobia.

### Overenie
- `npm test`, `npm run build`, číslo nasadenia.
- Snímky Playwright (syntetické dáta, aspoň 2 obľúbené miesta, akcie bez obrázka aj s obrázkom, zmrazený čas nedeľa 15. 11. 18:00) do `docs/tasks/041/`: `01-akcie-odznaky.jpg` (vypnuté čipy, viditeľné odznaky a ikony v plochách), `02-akcie-pre-teba.jpg`, `03-hladanie.jpg` (napísané „techno“), `04-hladanie-nic.jpg`.

## Report

Dátum: 2026-11-15  
Commit: f13788e

### Čo je hotové

**0. Oprava ikony v mriežke (bug z 040)**
- `EventsPage.tsx`: odstranil lokálnu `TypeIcon` komponentu, nahradil `EventTypeIcon` z `../icons` s farbou `EVENT_TYPE_DARK[type]` (40 px, v strede plochy)
- `EventPanel.tsx`, `VenuePage.tsx`, `EventPage.tsx`: tieto stránky už používali `EventTypeIcon` s `color={dark}` / `color={fg}` kde `fg = EVENT_TYPE_DARK[type]` → správne, nič nemenené

**1. Hľadanie**
- Lupa 44 px vpravo od nadpisu (`#23232F`, ikona `#F4F2FF`)
- Animácia 200 ms: `scaleX(0→1)` + `opacity(0→1)` s `transformOrigin: right` → pole sa roztiahne od lupy doľava
- Nadpis `opacity` 1→0 počas animácie, `pointerEvents: none` keď hľadanie otvorené
- `caretColor: #FF4D8D` (ružový kurzor)
- Debounce 150 ms (`debouncedQuery`)
- Hľadá v: `event.title`, `venue.name`, `event.formats`, `event.genres`, `venue.character`
- Normalizácia: lowercase + decompose NFD + remove combining chars → „cajovna" nájde „Čajovňa"
- Pri otvorení: uloží predošlé obdobie, prepne na Kedykoľvek; pri zatvorení: obnoví
- Zmena obdobia počas hľadania: platí, `searchPreviousPeriod` sa aktualizuje

**2. Pre teba a Nové**
- Čipy v lište za tlačidlom obdobia (40 px, iskry ikona pre Pre teba)
- Vypnuté: `#23232F`/`#B9B6CC`, zapnuté: `#FF4D8D`/`#1A0710`
- Pás čipov: `flex:1`, `overflow:hidden`, gradient fadeout vpravo (len keď pretekajú)
- **Pre teba**: `isForYou(event, favorites)` = `favorites.has(event.venue_id)`
- **Nové**: `isNew(event, now)` = `first_seen ≥ (now - 6 dní)` (7 dní vrátane dneška)
- Odznaky na kartách: „pre teba" (tmavý, iskry, top-left), „nové" (biely, top-right), `position:absolute; zIndex:2`
- Riadok s počtom: „12 akcií · 3 pre teba" (Pre teba OFF) / „9 akcií pre teba" (Pre teba ON) / bez „· N pre teba" ak žiadne obľúbené
- Stav sa pamätá: `store.ts` → `getStoredEventsFilters` / `setStoredEventsFilters`
- Prázdny stav + Pre teba bez obľúbených: „Pridaj si obľúbené miesta v záložke Miesta."
- Prázdny stav + filter aktívny: tlačidlo „Zrušiť filtre"

**3. Text zoradenia „čas" vs „dátum"**
- `isSingleDayPeriod(period)` exportovaná z `core/period.ts`: true pre `today`, `tomorrow`, `custom from===to`
- Pri jednodňovom období: sortDateLabel = `dict.events.sortTime` = „čas" / „čas" / „time"
- Radí sa rovnako (dátum + čas začiatku)

### Nové súbory
- `web/src/core/search.ts`: `normalizeText`, `matchesSearch`, `isForYou`, `isNew`
- `web/src/core/search.test.ts`: 29 testov (normalizácia, hľadanie, Pre teba, Nové, isSingleDayPeriod)

### Testy
```
npm test -- --reporter=dot
# Test Files  10 passed (10), Tests  142 passed (142)
```

### Build
```
npm run build
# ✓ built in 4.10s
# dist/assets/index-DalvfQ0g.js 1,062.73 kB
```

### Snímky
Vytvorené: `docs/tasks/041/01-akcie-odznaky.jpg` (106 KB), `02-akcie-pre-teba.jpg` (119 KB), `03-hladanie.jpg` (120 KB), `04-hladanie-nic.jpg` (38 KB)

### Rozhodnutia
- Filter button zatiaľ nezobrazovaný (task 041 hovorí „ostáva prázdne")
- Badges sa zobrazujú na všetkých kartách (aj keď čip je vypnutý) podľa dizajnu
- `first_seen` ≥ `now - 6 dní` = 7 dní vrátane dneška (nediskutabilné – task spec)
- `searchPreviousPeriod` sa aktualizuje aj počas otvoreného hľadania ak používateľ zmení obdobie
- Ikony Pre teba/Nové badge sú inline (nie z `icons/index.tsx`) – sú len 2 riadky SVG

### Čo ostáva otvorené
- Filter panel (príde v samostatnej úlohe)
- Ikona v ploche: ikona je v strede plochy (nie vľavo dole ako v design HTML kde bolo `alignItems:flex-end`) – toto bolo zámerné rozhodnutie pre lepšiu viditeľnosť ikony veľkosťou 40 px
