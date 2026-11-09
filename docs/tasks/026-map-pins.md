# 026: Mapa s pinmi, hotový tmavý štýl, šípky medzi miestami

## Zadanie
Zadal: hlavný chat, 2026-11-09. Po úlohe 025 (a oprave buildu `606a1df` od hlavného chatu).

Matej po teste 025 v telefóne:
- variant **A** áno, ale mapa je stále rozbitá (rieka miestami modrá, miestami zelená, pri oddialení nízke rozlíšenie),
- spojnice sa pri oddialení a ťuknutí kreslia rozbito,
- pilulky s menami nie sú to pravé.

Hlavný chat s Matejom prepracoval značky na **piny**. Predloha je aktualizovaná: **`docs/design.md` časti 2, 3 a 7** a nové snímky **`01-mapa-piny.png`** a **`02-mapa-vybrany-pin-karta.png`** (+ HTML s presným tvarom pinu, tieňom a pulzom). Staré `01-mapa.png` a `02-mapa-panel.png` už neplatia.

### 1. Podklad mapy: hotový štýl, nie vlastné skladanie
- Vezmi **hotový tmavý štýl pre schému OpenMapTiles** (napr. Dark Matter od OpenMapTiles/CARTO, alebo tmavý štýl, ktorý ponúka priamo OpenFreeMap). Over jeho licenciu a dodrž ju (autorstvo v ikonke „i“).
- Prefarbi ho do palety **variantu A** z `design.md`. **Voda musí mať všade rovnakú farbu.** Zisti, prečo bola Vltava miestami zelená (iná vrstva, napr. `landcover`/`wetland`/`waterway` nad `water`), a v reporte to uveď.
- **Najväčšie oddialenie = celá Praha** (`minZoom`, prípadne `maxBounds` okolo Prahy).
- **Popisy:**
  - štvrte, ulice, Vltava a ostrovy,
  - **stanice metra a dôležité budovy ako malé sivé ikonky** s názvom pri dostatočnom priblížení. Farby liniek metra nie.
- Bez obchodov a reštaurácií.
- **Prepínač variantov `?map=a|b|c` odstráň**, ostáva len A. Uložený výber v `localStorage` ignoruj alebo zmaž.

### 2. Piny namiesto pilulek (`design.md` časť 2)
- Pin presne podľa `01-mapa-piny.html`: tvar so stredne ostrým hrotom (SVG obrys z predlohy), plochá farba typu, tmavý kruh 36 px s ikonou 22 px, tieň pod pinom (`drop-shadow`). Bez mena, bez času.
- Odznaky: obľúbené (biely so srdiečkom, vpravo hore), `+N` (tmavý, vľavo hore). Prebiehajúca akcia: pulz okolo kruhu.
- **Vybraný pin** = pilulka vo farbe typu s tmavým kruhom, ikonou a menom (tmavým písmom) s chvostom dole presne na bode (`02-mapa-vybrany-pin-karta.html`).
- **Piny sa môžu prekrývať.** Zruš posúvanie nad seba, spojnice aj prechod na bodky pri oddialení. Ťuk na prekryté miesto vyberie vrchný pin.
- Hrot pinu musí ukazovať presne na súradnicu miesta (`anchor: bottom`), aj pri vybranom pine.

### 3. Karta a šípky (`design.md` časť 3)
- **Prvé ťuknutie na pin mapu nepresúva ani necentruje.**
- **Štítky miesta (charakter) z karty odstráň.** Ostáva jeden posúvateľný riadok štítkov akcie s rozplynutím vpravo.
- **Šípky ‹ ›** (biele kruhy 36 px nad kartou):
  - ‹ = najbližšie miesto na **západ**, › = najbližšie na **východ**,
  - poradie podľa zemepisnej dĺžky miest, ktoré majú akciu vo zvolenom dni a prechádzajú aktuálnym filtrom (Všetko/Obľúbené),
  - šípka vyberie pin, otvorí kartu a plynulo posunie mapu, aby bol pin viditeľný,
  - na krajoch sa šípka skryje.
- Potiahnutie karty ostáva na prepínanie akcií toho istého miesta.
- Ostatné správanie z 025 (mapa ovládateľná pri otvorenej karte, Späť zavrie kartu, stránka sa nezväčšuje) musí ostať.

### 4. Stránka akcie (`design.md` časť 7)
Len štítky akcie. Štítky miesta odstráň.

### 5. Overenie (štvrtýkrát, tentoraz bez výnimky)
Playwright je v `web/package.json` (`@playwright/test`). Ak chýba prehliadač, nainštaluj ho (`npx playwright install chromium`). Ak to prostredie naozaj nedovolí, napíš presnú chybovú hlášku.
- **Snímky 390 × 844, jazyk `sk`, s reálnymi dátami** do `docs/tasks/026/`:
  - celá Praha (najväčšie oddialenie),
  - centrum s pinmi,
  - ulica s metrom a budovami,
  - vybraný pin + karta,
  - karta po stlačení › (iné miesto),
  - stránka akcie.
- **Test dotykov** (`hasTouch: true`): otvorená karta → posun mapy (karta ostane, mapa sa posunie) → ťuk na iný pin (prepne kartu) → `page.goBack()` (karta sa zavrie, mapa ostane na mieste). Pozície a výsledok do reportu.
- **Offline, odkaz na akciu, manifest:** ako v zadaní 025 bod 6.
- **Pred pushom spusti `npm run build`** (v 025 nasadenie zlyhalo na chybe TypeScriptu). Po pushi over, že workflow „Deploy web app“ skončil úspešne, a uveď číslo behu.

### Report navyše
- Ktorý štýl si použil, jeho licencia a prečo bola rieka zelená.
- Tabuľka rozdielov oproti `01-mapa-piny.png` a `02-mapa-vybrany-pin-karta.png`.

## Report
