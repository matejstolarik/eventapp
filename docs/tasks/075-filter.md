# 075: Filter (mapa aj Akcie)

## Zadanie

**Schválené Matejom 2026-11-19 11:53.** Len frontend (`web/`) → **pipeline nespúšťaj** (`CLAUDE.md`), over nasadenie `deploy-app`. **Záväzné:** UI presne podľa `docs/design.md` 7b (blok „Zmena 2026-11-19“ + zvyšok časti) a `docs/design/screens/09-filter.png`; nič nevymýšľaj, drž štýl appky. Čo chýba alebo sa nedá, **stop a spýtaj sa**.

**Čítaj:** `docs/design.md` časť 1 (farby, čipy, ikony), 3 (mapa: horná lišta, Filter, piny), 4 (Akcie: lišta, prázdny stav), **7b celá**; `docs/design/screens/09-filter.png`; `data/genre_hierarchy.json`; `web/src/core/types.ts` (`Venue.character`, `Venue.size`, `Event.genres`, `formats`, `primary_format`, `free`), `web/src/core/eventType.ts` (typ, podtypy kultúry, ikony), `web/src/map/markers.ts` (ikona a farba pinu), `web/src/pages/MapPage.tsx` a `EventsPage.tsx` (dnešné tlačidlo Filter – `grep -n -i filter`), `web/src/core/store.ts` (ukladanie stavu). Panel obdobia v Akciách ako vzor panelu zdola.

### 1. Panel Filtra
- Otvára ho ružové tlačidlo Filter na mape aj v Akciách (dnes len hláška). Panel zdola podľa 7b a kresby: nadpis, „Zrušiť všetko“, sekcie **Typ akcie → podtypy kultúry → Žáner → Charakter miesta → Veľkosť miesta → Cena**, dole stále viditeľné tlačidlo „Zobraziť N akcií“ / na mape „Zobraziť N miest“.
- **Pohyb:** panel plynulo vyjde zdola a zíde dole (~200–250 ms; `prefers-reduced-motion` = okamžite), stlmené pozadie. **Obsah sa posúva plynulo** (natívny posun, žiadne zasekávanie ani pri desiatkach čipov; nič ťažké sa neprepočítava pri posune). Zatvorenie: tlačidlo Zobraziť, ťuk na stlmené pozadie, potiahnutie dole, systémové Späť.

### 2. Skupiny a správanie
- **Typ akcie:** 4 čipy s ikonou a farbou typu (legenda). Predvolene **všetky zapnuté, používateľ vypína**; posledný zapnutý sa vypnúť nedá (7b).
- **Podtypy kultúry:** blok pod typmi, len keď je Kultúra zapnutá; čipy `film`, `theatre`, `talk`, `workshop`, `quiz`, `opening`, `dance`, `stand-up` s našimi ikonami (tie isté ako piny a pilulka ikony). Nič nevybraté = celá kultúra; voľby sa pamätajú aj pri vypnutej Kultúre. Akcia patrí podtypu podľa toho istého pravidla, ktorým sa dnes vyberá jej ikona (`eventIconKey` / `primary_format`) – jedno miesto v kóde.
- **Žáner:** len zastrešujúce žánre z `data/genre_hierarchy.json` (rodič zahŕňa podžánre; žáner bez rodiča = sám sebe zastrešením; rovnaký názov naprieč druhmi = jeden čip). Len žánre, ktoré majú akcie **zapnutých typov**. 12 najčastejších + „Všetky (N) ›“ podľa kresby. Hierarchiu načítaj priamo do appky pri builde (import JSON z `data/`), **bez zmeny pipeline a `events.json`**; do `deploy-app.yml` `paths` pridaj `data/genre_hierarchy.json`.
- **Charakter miesta** (štítky `Venue.character`, po anglicky) a **Veľkosť miesta** (`Venue.size` small/medium/large, zobrazené malé / stredné / veľké podľa jazyka) – dve sekcie.
- **Cena:** čip **zadarmo** = `free === true`.
- **Kombinovanie, počty, poradie, odznak, prázdny výsledok, 0-čipy:** presne podľa 7b (v skupine ALEBO, medzi skupinami A; počet pri čipe = výsledok, keby sa čip pridal, pri aktuálnom dni/období a Všetko | Obľúbené; na mape miesta, v Akciách akcie; poradie žánrov a charakteru podľa počtu, určené pri otvorení; odznak = zapnuté štítky vrátane podtypov + 1 pri vypnutých typoch; karta prázdneho výsledku s „Najbližšie …“ a „Zrušiť filter“).

### 3. Spoločný a zapamätaný filter
- **Jeden filter pre mapu aj Akcie**, zachová sa pri zmene dňa/obdobia a prepnutí záložky; **uložený lokálne** (ako ostatné nastavenia v `store.ts`), platí aj po zatvorení appky, kým ho používateľ nezmení alebo nezruší. Nikdy sa sám nevypína.
- Spolupracuje s Obľúbené (mapa), Pre teba, Nové, obdobím, hľadaním a zoradením (Akcie) cez A; nič z toho sa do filtra nepresúva.

### 4. Piny na mape podľa filtra
- Pin miesta (ikona, farba, počet) sa počíta len z akcií, ktoré prešli filtrom. Miesto bez takej akcie nemá pin. Karta miesta ukáže len akcie, ktoré prešli filtrom.

### 5. Logika oddelená od UI
- Filtrovanie, počty a hierarchia v čistých funkciách (napr. `web/src/core/filter.ts`) s testami, aby sa dali neskôr použiť aj pre Pre teba.

## Overenie a report
- `npm test` – testy: ALEBO/A, rodič zahŕňa podžáner, žánre len zapnutých typov, podtypy (nič = všetko), zadarmo, odznak, počty na mape (miesta) vs. Akcie (akcie), uloženie a načítanie filtra, posledný typ sa nedá vypnúť. `npm run build`; číslo nasadenia.
- Snímky JPEG 390 × 844 do `docs/tasks/075/`: `filter-akcie.jpg` (panel v Akciách, Najbližších 7 dní, predvolený stav), `filter-kultura.jpg` (Kultúra zapnutá s blokom podtypov a jedným vybratým), `filter-mapa.jpg` (panel na mape), `mapa-po-filtri.jpg` (mapa s vypnutým Koncertom – piny podľa filtra), `akcie-prazdny.jpg` (karta prázdneho výsledku).
- Plynulosť: v reporte uveď, ako si overil posun a animáciu (napr. Playwright trace, čas snímky); ak niečo trhá, napíš kde.
- Report: čo hotové, rozhodnutia, otvorené body.

## Report

**2026-11-19**, commity `8a22b2b` (kód, testy, rozhodnutia), report v nasledujúcom commite. Len frontend – pipeline sa nespúšťala (`CLAUDE.md`). Nasadenie **Deploy web app #49** (run 44513106280): prvý pokus zlyhal v kroku `deploy-pages` na chybe API GitHubu („Found 0 artifact(s)“, build aj upload prešli), opakovanie (pokus 2) **success**. Na Pages je bundle `assets/index-Dz_4J2kL.js` s panelom Filtra (overené `curl`: obsahuje „Zrušiť všetko“, `filter-sheet`, hierarchiu žánrov).

### Hotové
- **Panel Filtra** (`web/src/components/FilterSheet.tsx`) z ružového tlačidla na mape aj v Akciách (aj v kompaktnej lište): nadpis, „Zrušiť všetko“, sekcie Typ akcie → podtypy kultúry (blok `#22212F` len pri zapnutej Kultúre) → Žáner (12 + „Všetky (N) ›“) → Charakter miesta → Veľkosť miesta → Cena (`zadarmo`), dole stále viditeľné „Zobraziť N akcií“ / na mape „Zobraziť N miest“. Vzhľad čipov podľa `09-filter.html` (typ: plná farba / farebný obrys; neutrálne: biely / `#2A2838`; čip s 0 stlmený a zapnuteľný). Ikony typov a podtypov = ikony pinov (koncert gitara, kultúra podľa podtypu).
- **Pohyb:** vysunutie a zasunutie 220 ms (`transform`, stlmené pozadie), `prefers-reduced-motion` = okamžite; zatvorenie tlačidlom Zobraziť, ťukom na pozadie, potiahnutím dole, systémovým Späť. Obsah = natívny posun (`overflow-y: auto`, `overscroll-behavior: contain`); počty sa prepočítajú len pri zmene filtra, nie pri posune.
- **Logika v `web/src/core/filter.ts`** (čisté funkcie): ALEBO v skupine / A medzi skupinami, hierarchia žánrov (rodič zahŕňa podžánre aj cez viac úrovní, `goregrind` → `metal`, `punk`), žánre len zapnutých typov, podtypy (nič = celá kultúra, pamätajú sa pri vypnutej Kultúre), zadarmo = `free === true`, posledný typ sa nedá vypnúť, odznak, počty (mapa = miesta, Akcie = akcie), uloženie (`parseFilter`/`serializeFilter`). Hierarchia sa importuje z `data/genre_hierarchy.json` pri builde; pipeline ani `events.json` sa nemenili. `deploy-app.yml` reaguje aj na zmenu hierarchie.
- **Podtyp kultúry z jedného miesta:** `cultureSubtype()` v `eventType.ts`, `eventIconKey` z neho berie ikonu (správanie ikon bez zmeny, pokryté testami).
- **Jeden filter** v `App.tsx` pre mapu aj Akcie, uložený v `localStorage` (`store.ts` `getStoredFilter`/`setStoredFilter`), zachová sa pri zmene dňa/obdobia, záložky aj po zatvorení appky. Spolupracuje s Obľúbené, Pre teba, Nové, obdobím, hľadaním a zoradením cez A.
- **Piny podľa filtra:** `visibleEvents` má voliteľný `eventFilter` – pin (ikona, farba, `+N`), karta miesta, šípky ‹ › a úvodný pohľad podľa polohy berú len akcie, ktoré prešli filtrom. Snímka: 9 pinov → 4 po vypnutí Koncertu (`docs/tasks/075/mapa-piny.json`).
- **Odznak** na tlačidle Filter (biely, počet štítkov vrátane podtypov a zadarmo + 1 pri vypnutých typoch); hláška „Filter pripravujeme“ odstránená.
- **Prázdny výsledok:** karta nad spodnou lištou s textom podľa dňa/obdobia, „Najbližšie: <deň> ›“ (prvý neskorší deň s výsledkom) a „Zrušiť filter“. „Zrušiť filtre“ v doterajšom prázdnom stave Akcií ruší aj filter.

### Rozhodnutia (samostatne, zapísané v `docs/decisions.md`, 3 riadky 2026-11-19)
1. Počet pri čipe = výsledky čipu pri výbere ostatných skupín (nie zjednotenie so zapnutými čipmi skupiny) – inak by čísla pri čipoch v skupine so zapnutým čipom nič nehovorili.
2. Ponuka žánrov/charakteru zo všetkých načítaných dát (preto existujú 0-čipy); zapnuté čipy vždy viditeľné; „Všetky (N) ›“ po rozbalení zmizne.
3. **Na potvrdenie:** žánre `film`, `theatre`, `dance` (zastrešenia filmových/scénických žánrov) sa v sekcii Žáner neukazujú – pokrývajú ich podtypy. Kultúra tak vo filtri žánrový čip prakticky nemá. Príklad `drama` zo 7b je podžáner a podľa pravidla „len zastrešujúce“ sa neukáže.
4. Veľkosť miesta ako prepínač s tromi časťami podľa `09-filter.html`, viacnásobný výber, počet v každej časti.
5. Panel od 114 px zhora (ako kresba), prekrýva spodnú lištu; zatvorenie potiahnutím > 90 px.
6. Karta prázdneho výsledku v Akciách len keď výsledok vyprázdnil filter; na mape vždy pri nepredvolenom filtri bez miest. Štýl tlačidiel karty a odznaku (kresba ich nemá) v štýle appky.

### Overenie
- `npm test`: **231 passed** (15 súborov), z toho nové `src/core/filter.test.ts` – ALEBO/A, rodič zahŕňa podžáner, žánre len zapnutých typov, podtypy (nič = všetko, pamätanie pri vypnutej kultúre), zadarmo, odznak, počty mapa (miesta) vs. Akcie (akcie), poradie podľa počtu, uloženie a načítanie cez `store.ts`, neplatné uložené dáta, posledný typ sa nedá vypnúť, podtyp = pravidlo ikony.
- `npm run build`: OK.
- Playwright `tests/playwright/screenshots-075.spec.ts` (dáta a obrázky z Pages, čas 2026-11-19 17:00): 3 passed; overuje aj, že systémové Späť panel zavrie a odznak po výbere `theatre` ukáže 1.
- Snímky (JPEG 390 × 844) v `docs/tasks/075/`: `filter-akcie.jpg` (Akcie, Najbližších 7 dní, predvolený stav), `filter-kultura.jpg` (blok podtypov, vybraté `theatre`), `filter-mapa.jpg`, `mapa-po-filtri.jpg` (vypnutý Koncert), `akcie-prazdny.jpg` (Dnes + kultúra/`quiz`). Snímky som neprezeral (pravidlo kreditov).
- **Plynulosť** (`docs/tasks/075/plynulost.json`): posun obsahu panela po rozbalení všetkých žánrov (69 tlačidiel, obsah 1358 px v okne 549 px), 80 krokov posunu – 83 snímok, **najdlhšia medzera 18 ms, p95 17 ms** (60 fps, bez zaseknutia). Otvorenie: od kliku po dobehnutie panela 326 ms vrátane réžie Playwrightu (animácia 220 ms). Merané v desktopovom Chromiu, nie na telefóne.

### Otvorené
- Potvrdiť rozhodnutie 3 (žánre kultúry vo filtri) a výklad počtov pri čipoch (rozhodnutie 1).
- Plynulosť na skutočnom telefóne neoverená (len Chromium v Playwright).
- `SelectorSheet` (obdobie, deň) má rovnaký vzor histórie, ktorý v dev režime s React StrictMode môže panel hneď zavrieť (v produkcii sa StrictMode neprejavuje); vo Filtri je to ošetrené, `SelectorSheet` som nemenil.
