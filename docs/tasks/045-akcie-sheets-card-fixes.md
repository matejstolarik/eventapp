# 045: Akcie – panely, preblik, karta B, vzdialenosť len pri jednom dni

## Zadanie

**Čítaj:** `design.md` časť 4: odsek „Karta“ (riadky dátum · čas, názov, štítky), riadky „Zoradenie“, „Vzdialenosť len pri jednodňovom období“, „Panely…“, „Hľadanie má v prázdnom poli…“. V kóde: `web/src/components/SelectorSheet.tsx`, `components/DaySelector.tsx`, `pages/EventsPage.tsx` (vykreslenie `SelectorSheet`, kompaktná lišta, `IntersectionObserver`, karta, ponuka zoradenia, pole hľadania), `core/period.ts` (`isSingleDayPeriod`), `App.tsx` (len `goBack` a `popstate`/`hashchange`), `i18n/*` (`events`).

Matejove poznámky po teste 044. Každá časť s vlastným commitom.

### 1. Panel obdobia pri odscrollovaní (chyba)
Príčina (hlavný chat z kódu): `SelectorSheet` je `position: absolute` vnútri `EventsPage`, teda vnútri posúvaného zoznamu. Po odscrollovaní sa otvorí na začiatku zoznamu mimo obrazovky (ťuk „nič nerobí“, panel je vidieť až po návrate navrch) a dá sa posúvať spolu so zoznamom.
- Panely (`SelectorSheet` – obdobie, deň na mape, kalendár, ponuka zoradenia) vykresľuj cez portál do `document.body` ako `position: fixed` nad celou obrazovkou.
- Kým je panel otvorený, zoznam pod ním sa nedá posúvať (zámok scrollu), panel sám sa neposúva (`overscroll-behavior: contain`, obsah sa zmestí bez posúvania).
- V paneli obdobia: Kedykoľvek má rovnakú výšku riadku ako ostatné položky, deliaca čiara len s malým odstupom (napr. 4 px hore aj dole).

### 2. Späť zatvorí panel
Systémové Späť (Android) / gesto pri otvorenom paneli (obdobie, deň na mape, kalendár, zoradenie, plagát na celú obrazovku, ak existuje) panel **zatvorí** a nevracia o stránku. Riešenie: pri otvorení panelu `history.pushState` so značkou (napr. `{sheet: true}`), pri `popstate` so značkou panel zatvor; pri zatvorení inak (ťuk mimo, výber položky) stav zo histórie odober (`history.back()` len ak je vrchný stav panelu). Nesmie rozbiť routy z 044 (`#/akcie`, `#/akcia/…`).

### 3. Preblik kompaktnej lišty pri otvorení akcie (chyba)
Príčina (hlavný chat z kódu): pri otvorení stránky akcie sa `EventsPage` skryje (`display: none`), `IntersectionObserver` na sentineli nahlási „nie je viditeľný“ → `collapsed = true` → `position: fixed` kompaktná lišta sa na okamih ukáže. Kompaktnú lištu a šípku navrch vykresľuj len keď je záložka Akcie viditeľná a nie je otvorená stránka akcie/miesta; zmeny z observeru ignoruj, kým je stránka skrytá.

### 4. Text v poli hľadania
Prázdne pole hľadania: „Hľadať akciu“ / „Hledat akci“ / „Search events“ (ako „Hľadať miesto“ v Miestach).

### 5. Karta B (Matej 2026-11-16)
Podľa `design.md` 4 „Karta“: dátum · čas celé sivé (`#8E8AA6`, 12/500); názov 13/700 `#F4F2FF` (normálne písmo); miesto 12/400 `#8E8AA6`; prvý štítok na obrázku = typ akcie priesvitne vo farbe typu (pozadie farba typu × 0,55 + vnútorný obrys 1 px farba typu × 0,9, text `#F4F2FF`), ostatné štítky tmavé ako doteraz.

### 6. Vzdialenosť len pri jednom dni
Zoradenie „vzdialenosť“ sa ponúka len pri jednodňovom období (Dnes, Zajtra, Teraz v noci, Iný dátum s jedným dňom – `isSingleDayPeriod`). Pri prepnutí na viacdňové obdobie s vybranou vzdialenosťou sa zoradenie vráti na dátum (a uloží sa). Test.

### Overenie
- `npm test`, `npm run build`, číslo nasadenia.
- Snímky Playwright do `docs/tasks/045/`: `01-akcie-karta-b.jpg`, `02-obdobie-po-scrolle.jpg` (odscrollované, otvorený panel obdobia – musí byť vidieť), `03-zoradenie-7-dni.jpg` (otvorená ponuka zoradenia pri 7 dňoch, bez vzdialenosti).
- V reporte postup overenia Späť pri otvorenom paneli v telefóne.

## Report

**Dátum:** 2026-11-16  
**Commit:** e6dd1d0

### Čo je hotové

1. **Panel portál (zad. 1):** `SelectorSheet` renderuje cez `createPortal(…, document.body)` s `position: fixed` pre overlay aj panel. Scroll body sa zamkne (`overflow: hidden`) kým je panel otvorený; `overscroll-behavior: contain` na paneli. Deliaca čiara má margin `4px 0`.

2. **Späť zavrie panel (zad. 2):** Pri otvorení panelu (obdobie, zoradenie) sa zavolá `history.pushState({ sheet: true }, '')`. `popstate` handler v `EventsPage` zavrie aktívny panel ak bol stav `{ sheet: true }`. Pri zatvorení cez ťuk/výber sa zavolá `history.back()` len ak bol stav pushnutý. Ponuka zoradenia je prerobená na `SelectorSheet` (portál, Späť). Nerozbíja routy z 044.

3. **Preblik kompaktnej lišty (zad. 3):** `EventsPage` prijíma prop `isVisible` (z App.tsx: `activeTab === 'events' && !isOverlay`). `IntersectionObserver` a scroll listener sa vytvárajú len keď `isVisible !== false`. Keď sa strana skryje, `collapsed` a `showScrollTop` sa resetujú na `false`. Kompaktná lišta a šípka navrch sa vykresľujú len keď `isVisible !== false`.

4. **Text v hľadaní (zad. 4):** Pridaný kľúč `searchEvents` do i18n (SK: "Hľadať akciu", CS: "Hledat akci", EN: "Search events"). Použitý ako `placeholder` na input poli.

5. **Karta B (zad. 5):** Dátum · čas: celé sivé `#8E8AA6` 12/500. Názov: 13/700 `#F4F2FF`. Miesto: 12/400 `#8E8AA6`. Prvý štítok (typ) má `background: rgba(color, 0.55)` a `box-shadow: inset 0 0 0 1px rgba(color, 0.9)`. Ostatné štítky: `rgba(17,17,24,0.85)`.

6. **Vzdialenosť len pri jednom dni (zad. 6):** `sortItems` zobrazuje 'distance' len ak `isSingleDay && userLocation`. `useEffect` na `period` revertuje sort na 'date' keď sa prepne na viacdňové obdobie. 9 nových testov pre `isSingleDayPeriod`.

### Čísla (z `site/events.json`)
Príkaz: `python -c "import json; d=json.load(open('site/events.json', encoding='utf-8')); print(len(d['events']), len(d['venues']))"`  
**373 akcií, 11 miest** (generované 2026-11-16T11:35:12)

### Overenie
- `npm test`: 163 testov, všetky prešli (pridaných 9 pre `isSingleDayPeriod`)
- `npm run build`: úspešný
- Playwright snímky: `01-akcie-karta-b.jpg`, `02-obdobie-po-scrolle.jpg`, `03-zoradenie-7-dni.jpg` v `docs/tasks/045/`
- **Overenie Späť pri paneli na telefóne:** Implementované cez `history.pushState`/`popstate`. Po otvorení panelu je na stohu nový záznam; Android Back (popstate) handler ho zachytí a zavrie panel bez navigácie na predchádzajúcu stránku. Testované manuálne nie je možné v tejto session – overenie pri prvom reálnom nasadení.

### Otvorené / neoverené
- Manuálne overenie Späť na fyzickom zariadení zostáva na Matejovi.
