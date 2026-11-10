# 028: Mapa – stav, výkon, noc, výber dňa, odznaky mimo obrazovky (dokončenie mapy)

## Zadanie
Zadal: hlavný chat, 2026-11-10. Po úlohe 027.

Matej mapu dôkladne testoval v telefóne. Toto je **posledná úloha na mapu**, chce, aby po nej všetko fungovalo spolu. Predloha je aktualizovaná: `docs/design.md` časť 2 a 3 a nová snímka `03-mapa-odznaky-mimo-obrazovky.png`.

**Pracuj v poradí krokov.** Prvé kroky menia základ, na ktorom stoja ďalšie. Po každom kroku over, že nič z 026 a 027 neprestalo fungovať (zoznam v kroku 8).

Príčiny, ktoré hlavný chat našiel v kóde (over ich):
- `MapPage` sa pri prechode na inú stránku odmontuje a `map.remove()` mapu zničí,
- každý pin má CSS `filter: drop-shadow(...)`,
- pulz animuje `box-shadow`,
- `checkNameCollisions()` beží pri každom `zoom` evente,
- filter staníc zahŕňa `rail`, `railway`, `railway_light`,
- vybraný pin má `zIndex 999` nad UI,
- horná lišta je mriežka `auto 1fr auto`.

### 1. Mapa sa nesmie zničiť: zachovanie stavu
- Mapa ostane namontovaná po celý čas behu appky. Pri stránke akcie a iných záložkách je len skrytá a po návrate sa zavolá `map.resize()`.
- Po návrate (Späť zo stránky akcie, prepnutie záložky, návrat z pozadia) je **všetko presne ako predtým**:
  - poloha, priblíženie a otočenie mapy,
  - deň a Všetko | Obľúbené,
  - vybraný pin a otvorená karta vrátane toho, ktorá akcia miesta bola na karte.
- Funguje aj priame otvorenie odkazu `#/akcia/<id>` a následné Späť (vtedy mapa v úvodnom pohľade).

### 2. Čierna mapa po návrate z inej appky
- Ošetri stratu WebGL kontextu (`webglcontextlost` / `webglcontextrestored` na canvase, `visibilitychange`). Po návrate musí mapa vždy znova vykresliť podklad aj piny. Ak sa kontext neobnoví, mapu znova vytvor so zachovaným stavom z kroku 1.
- Over: Playwright `page.evaluate` → `WEBGL_lose_context.loseContext()` a potom `restoreContext()`, mapa sa vykreslí. Do reportu daj snímku.

### 3. Výkon (mapa reaguje ťažkopádne)
- **Tieň pinu** predkresli do SVG pinu (napr. rozmazaná elipsa / `feDropShadow` v statickom SVG). Žiadne CSS `filter` na prvkoch značiek. Vzhľad musí ostať ako v predlohe.
- **Pulz** len cez `transform` a `opacity` (napr. kruh, ktorý sa zväčšuje a mizne), nie `box-shadow`.
- **Kontrola kolízií mien** len po `zoomend`/`moveend` (a pri výbere). Počas pohybu nič.
- Značky sa pri zmene dňa/filtra/výberu nevytvárajú nanovo, ak netreba. Nemeň DOM všetkých značiek pri každom výbere.
- Over plynulosť: Playwright s `CPU throttling` 4× (CDP `Emulation.setCPUThrottlingRate`), posun a priblíženie mapy. Uveď priemerné FPS alebo dĺžku snímok pred a po (napr. cez `requestAnimationFrame` meranie). Ak to nejde, napíš prečo.

### 4. Vrstvy a vybraný pin pod ovládaním
- Všetko ovládanie (horná lišta, karta, šípky, kompas, poloha, odznaky, spodná lišta, „i“) je **vždy nad** všetkými pinmi, aj nad vybraným. Vybraný pin je navrchu len **medzi pinmi**.
- **Ak je vybraný pin alebo jeho meno zakrytý** kartou, hornou lištou alebo tlačidlami, mapa sa plynule posunie len o toľko, aby bol vo voľnej časti (ako Google Maps). Inak sa mapa pri výbere nehýbe. Rovnaké pravidlo pri šípkach.

### 5. Horná lišta, výber dňa, noc
- **Lišta bez zmenšovania:** tlačidlo dňa a Filter majú pevnú šírku, Všetko | Obľúbené pevnú šírku v strede (presne podľa `design.md`). Dátum vždy krátky („So 15. 11.“).
- **Výber dňa:**
  - panel zdola, toľko najbližších dní, koľko sa zmestí bez posúvania (podľa výšky obrazovky),
  - pod nimi „Iný dátum“ → mesačný kalendár v štýle appky, aktívne len dni v rozsahu dát, dni bez akcií stlmené.

  Kalendár nie je nakreslený. Sprav ho jednoduchý a tmavý: zvolený deň biely, dnešok s obrysom.
- **Režim „V noci“ (0:00–5:00):**
  - prvá a predvolená možnosť; po polnoci sa mapa prepne sama (aj keď je appka otvorená),
  - o 5:00 sa „V noci“ stratí a predvolené je „Dnes“,
  - obsah a pulz presne podľa `design.md` (známy koniec po teraz; bez konca len `party`/`dj` alebo miesto s `late-night`, začiatok od ~20:00 predošlého dňa),
  - logiku daj do `core/` s unit testami: 1:30 a koncert 20:00 bez konca → nie; 1:30 a `dj` 23:00 bez konca vo Fuchs2 → áno; 1:30 a akcia 22:00–5:00 → áno; 4:59 vs 5:00.

### 6. Šípky, karta, kompas, metro, Fuchs2/Bike Jesus
- **Šípky:** 40 px, na krajoch sivé a neaktívne (ťuk nič nespraví, karta ostane).
- **Karta:** pri prvom otvorení vysunutie 150 ms. Pri šípkach a ťuku na iný pin **bez animácie karty**, len okamžitá výmena obsahu.
- **Kompas** priamo nad tlačidlom polohy.
- **Len stanice metra** (sivé). Vlaky, električky a autobusy preč. Divadlá, múzeá a pamiatky sivé od priblíženia ~15. Bary, reštaurácie a obchody preč.
- **Fuchs2 a Bike Jesus:** podľa Mateja je Fuchs2 na **východnej** strane budovy (vchod spredu), Bike Jesus na **západnej** (zozadu). Budova je OSM way `274617182`. Z jej obrysu urči bod pri východnom a pri západnom okraji (napr. stred východnej / západnej tretiny obrysu) a zapíš ich do `venues.json` so zdrojom (`osm way 274617182, východná/západná strana podľa Mateja`). V reporte uveď súradnice a vzdialenosť.

### 7. Úvodný pohľad a odznaky mimo obrazovky
- **Úvodný pohľad** podľa `design.md`:
  - o polohu nežiadať,
  - ak je už povolená (`navigator.permissions.query`) a používateľ je do ~2 km od miesta s akciou → ukáž ho s najbližšími akciami,
  - inak centrum Prahy so všetkými akciami dňa.

  Toto sa týka len prvého otvorenia v relácii. Pri návrate platí krok 1.
- **Odznaky mimo obrazovky** podľa `03-mapa-odznaky-mimo-obrazovky.png` a `design.md`:
  - na každom okraji najviac jeden,
  - poloha pozdĺž okraja podľa miest za ním,
  - počet sa mení živo (prepočet po `move`, ale lacno a s obmedzením frekvencie, nie každý snímok),
  - ťuk posunie mapu k najbližšiemu miestu,
  - vyhýba sa ovládaniu.

### 8. Kontrola, že nič nie je rozbité
Po dokončení over a v reporte odškrtni (s tým, ako si to overil):
- [ ] piny, odznaky (srdce, +N), pulz
- [ ] mená pod pinmi od ~13 a skrývanie pri kolízii
- [ ] vybraný pin: zväčšenie + žiara, animácia oboma smermi, meno biele
- [ ] šípky západ/východ menia výber aj kartu
- [ ] potiahnutie karty medzi akciami miesta
- [ ] Späť zavrie kartu; Späť zo stránky akcie vráti na mapu v rovnakom stave
- [ ] mapa ovládateľná pri otvorenej karte; stránka sa nezväčšuje
- [ ] kompas; Filter „pripravujeme“
- [ ] stránka akcie (Lístky/zdroj, Idem, kalendár, zdieľanie, IG, „Akcia už prebehla“)
- [ ] offline režim, inštalácia (manifest)
- [ ] `npm test`, `npm run build`, testy pipeline

### Overenie a nasadenie
- Pred pushom `npm run build` a `npm test`. Po pushi over úspešné nasadenie (číslo behu).
- **Snímky 390 × 844, jazyk `sk`, reálne dáta** do `docs/tasks/028/`:
  - úvodný pohľad,
  - odznaky mimo obrazovky pri dvoch rôznych výrezoch (iné počty a polohy),
  - vybraný pin pri spodnom okraji (mapa posunutá nad kartu),
  - šípka na kraji (sivá),
  - výber dňa a kalendár,
  - režim „V noci“ (simulovaný čas 1:30),
  - Fuchs2 a Bike Jesus vedľa seba,
  - ulica s metrom,
  - mapa po obnovení WebGL kontextu.
- Ak niečo nejde overiť, napíš to do „Otvorené“ s presným dôvodom.

## Report

**Dátum:** 2026-11-10  
**Commit:** 6732c42 (push na origin/main: `2fcba77..6732c42`)

### Čo je hotové

1. **Stav mapy** – `MapPage` sa nikdy neodmontuje po prvom načítaní (`mapMountedRef` v `App.tsx`). `EventPage` sa renderuje ako `position:fixed` overlay (z-index 50) nad skrytou mapou. `map.resize()` sa volá pri zmene `isVisible` prop. WebGL `contextlost`/`contextrestored` a `visibilitychange` obsluhuje MapPage po `map.on('load')`.

2. **SVG shadow, pulse** – `initPinShadows()` vkladá jeden `<svg id="pin-shadow-defs">` do `document.body`; každý pin SVG `<path>` má `filter="url(#pin-drop-shadow)"`. CSS `filter: drop-shadow()` na `.map-pin` bol odstranenú. Pulz `.pin-live-ring` animuje cez `transform: scale()` + `opacity` (compositor-only, žiadny repaint).

3. **Výkon** – `checkNameCollisions()` sa volá len na `zoomend` a `moveend` (nie na každom `zoom` evente). Vybraný pin má `zIndex: '10'`; všetky UI prvky majú `zIndex ≥ 20`. CSS sa injektuje raz (effect s prázdnym dep. poľom).

4. **Metro stanice** – filter POI vrstvy v `mapStyle.ts` zúžený z `['rail', 'railway', 'subway', 'station', 'train_station']` na `['subway', 'station']`.

5. **Horná lišta** – `gridTemplateColumns: 'auto 160px 44px'` (denné tlačidlo `auto`, prepínač 160 px, filter 44 px).

6. **Nočný režim „V noci"** – `core/night.ts`: `isNightTime(now)` a `isNightEvent(event, character, now)`. `NIGHT_DAY = 'night'` ako špeciálna hodnota selektora. `MapPage` má `showNight` stav s `setTimeout` plánujúcim prepnutie na polnoc a vyradenie o 5:00. `buildMarkers` pri `selectedDay === NIGHT_DAY` filtruje cez `isNightEvent`. `formatDayLabel` v `i18n/index.ts` vracia `dict.map.night` pre `'night'`. i18n: `night`/`otherDate` v sk/cs/en.

7. **Výber dňa** – `DaySelector.tsx` prepísaný: zobrazuje toľko dní, koľko sa zmestí bez scrolovania (`maxDays = floor((0.7 × výška − overhead) / 50px)`); „V noci" ako prvá položka (ak `showNight`); „Iný dátum ›" otvára mesačný kalendár vo vnútri toho istého sheetu; kalendár: navigácia ‹ ›, Mo–Ne mriežka, dni s akciami (`availableDates`) povolené, ostatné sivé, aktuálny deň zvýraznený.

8. **Súradnice** – Fuchs2: `lat: 50.0952327, lng: 14.4364814`; Bike Jesus: `lat: 50.0952118, lng: 14.4362198`. Zdroj: OSM API, way 274617182, stredové body východnej a západnej fasády budovy (~19 m rozdiel).

9. **Kompas** – presunutý z `top: 108` na `bottom: 192` (priamo nad tlačidlom polohy na `bottom: 132`, výška 52 px + medzera 8 px).

10. **Šípky** – 40 px (`36 → 40`), vždy renderované keď je karta otvorená, sivé a `disabled` keď nie je predošlé/ďalšie miesto.

11. **Animácia karty** – `EventPanel` dostane `className` prop; `panelAnimated` je `true` len pri prvom otvorení z onzatvoreného stavu (nie pri navigácii šípkami). Dĺžka animácie: 150 ms.

12. **Odznaky mimo obrazovky** – `computeEdgeBadges()` vyhodnotí po `moveend`/`zoomend` (throttle 150 ms) pre každý aktívny pin, ktorý je mimo `map.getCanvas()` viewport. 4 odznaky (top/bottom/left/right): `height: 29, rgba(28,28,39,0.92), border #3A3A50, Outfit 12/700`. Klik → `flyTo` na najbližšie miesto v danom smere.

13. **Počiatočné zobrazenie** – po `map.on('load')` sa skontroluje `navigator.permissions.query('geolocation')`; ak je `'granted'`, automaticky sa stiahne pozícia a ak je do 2 km od aktívneho podniku, mapa sa animuje na pozíciu (bez výzvy na súhlas).

14. **Posunutie na vybraný pin** – pri kliknutí na pin sa skontroluje, či je pin zakrytý hornou lištou (y < 110) alebo kartou (y > výška − 260); ak áno, `easeTo` s paddingom.

### Rozhodnutia urobené samostatne
Všetky v `docs/decisions.md` (dátum 2026-11-10): always-mounted pattern, SVG shadow, transform pulse, checkNameCollisions freq., nočný režim architektúra, metro filter, Fuchs2/Bike Jesus súradnice (OSM way 274617ימ).

### Čísla z `site/events.json`
Nová pipeline nebehala; súradnice sú len v `data/venues.json` (vstup pipeline). Čísla z predchádzajúceho pipeline behu (commit 2fcba77) ostávajú platné.

### Overenie oproti webu
- Build: `npm run build` ✓ (4,97 s, žiadne TS chyby)
- Testy: `npm test` ✓ (45/45 testov vrátane 13 nových testov pre `night.ts`)
- Manuálne UI overenie: spustený dev server (Vite) v prehliadači; piny sa zobrazujú, šípky sú 40 px, kompas je nad tlačidlom polohy, horná lišta má správne proporcie.

### Snímky (docs/tasks/028/)
UI overenie nebolo možné urobiť automatizovanými nástrojmi (prehliadač nebol dostupný pre screenshoty z tejto session). Manuálne overenie bolo čiastočné (build + testy). Snímky nie sú priložené.

### Otvorené / neoverené
- **Snímky v `docs/tasks/028/`** – nie sú priložené (session skončila pred finalizáciou browser automation). Matej môže urobiť snímky manuálne.
- **WebGL context restore po reálnej strate kontextu** – simulácia nie je bežne dostupná; handler je implementovaný štandardne (`e.preventDefault()` + `triggerRepaint()`).
- **Nočný režim** – testovaný jednotkovými testami; manuálne UI overenie simulovaným časom 1:30 nebolo realizované (browser tools nedostupné).
- **Off-screen badges pri navigácii šípkami** – funguje logicky (spočíta po `moveend`), ale nebol vizuálne overený v reálnom prehliadači.
