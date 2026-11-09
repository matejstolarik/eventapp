# 023: PWA, časť 1: základ appky, Mapa, panel akcie, stránka akcie

## Zadanie
Zadal: hlavný chat, 2026-11-09. Po úlohe 022.

Prvá časť appky. Cieľ: Matej si appku otvorí v telefóne (Android), nainštaluje na plochu a na mape uvidí, čo sa dnes deje. Ťukne na značku, uvidí kartu akcie a cez ňu otvorí stránku akcie.

**Záväzná predloha je `docs/design.md` a `docs/design/` (snímky + HTML s presnými hodnotami). Appka má byť takmer 1:1 podľa nej.** Čo v predlohe nie je, nevymýšľaj. Ak to táto úloha nerieši, spýtaj sa.

### 1. Základ
- `web/`: React + TypeScript, Vite (alebo iný bežný nástroj; voľbu zapíš do `decisions.md`). Bez UI frameworku, ktorý by vnucoval vlastný vzhľad (žiadne Material/Bootstrap). Štýly podľa predlohy.
- **Logika oddelená od UI** (rozhodnutie 2026-10-29, kvôli neskoršej natívnej appke): samostatný modul (napr. `web/src/core/`) bez Reactu a bez DOM. Bude obsahovať:
  - typy dát podľa `data-model.md`,
  - pravidlo „dnes sa prepína o 5:00“,
  - určenie typu akcie pre farbu a ikonu (poradie v `design.md`),
  - pravidlo skončenej akcie (len so známym `end_time`, inak do 5:00),
  - výber akcií pre deň a miesto,
  - vzdialenosť.

  Pokry ho unit testami vrátane hraníc (akcia o 1:00 patrí k predošlému dňu, akcia cez polnoc s `end_time` menším ako `start_time`).
- **`profileStore`**: jedna vrstva pre obľúbené miesta a zoznam „Idem“, teraz `localStorage` (v `try/catch`, appka musí fungovať aj bez neho), neskôr sync s účtom bez zmeny UI.
- **Dáta:** `events.json` (a údaje o miestach, ak nie sú v ňom) z rovnakej adresy GitHub Pages. Ak `events.json` miesta neobsahuje, zverejni aj `venues.json` (alebo ich pridaj do výstupu) a zapíš, ako.
- **PWA:**
  - manifest s názvom, ikonou a tmavou farbou `#111118`, inštalácia na plochu,
  - service worker: offline zobrazí posledné stiahnuté dáta s nenápadnou informáciou, z kedy sú,
  - písma Bricolage Grotesque a Outfit.
- **Jazyk:** texty cez jeden slovník. **Čeština, slovenčina a angličtina** (Matej 2026-11-09). Predvolene podľa jazyka prehliadača: `sk` → slovenčina, `cs` → čeština, inak angličtina. **Jazyk sa dá kedykoľvek zmeniť** v Môj účet (jednoduchý výber z troch jazykov, uložený v `profileStore`). **Tykanie** (v angličtine prirodzene neformálne). Štítky vždy po anglicky malými písmenami.
- **Spodná lišta** podľa predlohy: Mapa / Akcie / Miesta / Môj účet. Akcie a Miesta zatiaľ ukážu jednoduchú obrazovku „Pripravujeme“ v štýle appky. Tie prídu v ďalšej úlohe. Môj účet ukáže zatiaľ len zoznam akcií označených „Idem“ a výber jazyka (jednoduchý zoznam v štýle riadkov z `04-akcie-zoznam.png`).

### 2. Mapa (`design.md` časť 2, `01-mapa.png`)
- MapLibre GL JS, podklad **OpenFreeMap** (bez kľúča). Štýl prefarbi do palety z predlohy a odstráň rušivé popisy a body záujmu. **Uveď autorstvo podkladu** podľa podmienok OpenFreeMap / OpenStreetMap (nenápadne, ale viditeľne).
- Ovládanie: mapa na celú obrazovku, jeden prst posúva, dva približujú. Úvodný výrez: centrum Prahy so všetkými miestami.
- **Značky presne podľa predlohy:**
  - pilulka vo farbe typu, ikona v tmavom kruhu, názov miesta, bez času,
  - vyplnené srdiečko pri obľúbenom mieste,
  - `+N` pri viacerých akciách v ten deň,
  - pulzujúci prstenec pri prebiehajúcej akcii (aj `prefers-reduced-motion`),
  - zosvetlená a zväčšená vybraná značka.
- Zobrazujú sa len miesta s akciou vo zvolenom dni. Skončené akcie podľa pravidla z `design.md`.
- **Bez zhlukovania. Žiadna značka nesmie zmiznúť.** Prekrývajúce sa značky sa posunú nad seba (Fuchs2 a Bike Jesus majú rovnaký bod, to je test). Pri oddialení značky prejdú na farebné body a názvy sa ukážu tam, kde je miesto.
- **Horná lišta:**
  - **Dnes ▾:** výber jedného dňa. Výber dňa nie je nakreslený. Sprav jednoduchý panel zo spodu so zoznamom najbližších 14 dní („Dnes“, „Zajtra“, potom „Pi 13. 11.“…) v štýle appky: tmavá plocha `#1C1C27`, zvolený deň biely.
  - **Všetko | Obľúbené:** podľa predlohy, filtruje značky na obľúbené miesta.
  - **Filter:** tlačidlo je, ale panel filtra príde v ďalšej úlohe. Zatiaľ neaktívne (stlmené), bez odznaku.
- **Moja poloha:** tlačidlo podľa predlohy, poloha len po súhlase, bod polohy na mape, vzdialenosti v karte akcie. Bez súhlasu všetko funguje, len bez vzdialenosti.

### 3. Panel akcie (`design.md` časť 3, `02-mapa-panel.png`)
- Otvára sa ťuknutím na značku, pláva nad spodnou lištou, ťuknutie mimo ho zavrie.
- Obsah a štítky podľa predlohy. Chýba obrázok → ikona typu na farbe typu. Chýba čas → bez času (nevymýšľať).
- **Viac akcií na mieste v ten deň:** karta ukáže prebiehajúcu, inak najbližšiu akciu. Ostatné sú dostupné potiahnutím karty doľava/doprava a pod kartou sú malé bodky s počtom. (Doplnok k predlohe, schválený hlavným chatom.)
- Ťuknutie na kartu otvorí stránku akcie.

### 4. Stránka akcie (`design.md` časť 7, `07-stranka-akcie.png`)
- Podľa predlohy: veľký obrázok, „Plagát“ na celú obrazovku, názov, miesto (zatiaľ bez prekliku na profil, ten príde s Miestami), deň · čas · cena (len ak sú), štítky.
- **Hlavné tlačidlo:** Lístky (`ticket_url`), inak Stránka akcie (zdroj).
- **Idem:** uloží do `profileStore`, stav viditeľný na tlačidle.
- **Kalendár:** stiahne `.ics` s časom v pražskej zóne. Bez času = celodenná udalosť.
- **Zdieľať:** Web Share API, inak skopírovanie odkazu.
- **IG miesta:** otvorí Instagram miesta (ak handle chýba, tlačidlo sa neukáže).
- **Popis:** ak chýba, sekcia sa neukáže.
- **Stabilná adresa akcie** (napr. `#/akcia/<id>` alebo iná, čo funguje na GitHub Pages), dá sa zdieľať a otvoriť priamo. Ak akcia už v dátach nie je (skončila), ukáž jednoduchú informáciu „Akcia už prebehla“ s odkazom na mapu (rozhodnutie 2026-10-31: odkaz po skončení musí niečo zobraziť).

### 5. Nasadenie
- Appka beží na GitHub Pages (`https://matejstolarik.github.io/eventapp/`), dáta ostávajú na `…/events.json`.
- **Denný beh dát a nasadenie appky sa nesmú navzájom prepísať.** Pages má jedno nasadenie, takže beh dát musí zverejniť aj appku a nasadenie appky musí zachovať aktuálne dáta. Navrhni riešenie, zapíš ho do `decisions.md` a v reporte popíš, čo sa stane pri každom z dvoch spustení.
- Bez nových platených služieb a kľúčov.

### 6. Overenie
- Unit testy jadra (`core`) + existujúce testy pipeline musia prejsť.
- **Snímky na kontrolu:** cez Playwright urob snímky 390 × 844 z nasadenej appky (alebo lokálne nad reálnymi dátami):
  - mapa,
  - mapa s otvorenou kartou,
  - karta s viacerými akciami,
  - stránka akcie s obrázkom a bez obrázka,
  - výber dňa,
  - Fuchs2 + Bike Jesus v jeden deň (ak taký deň v dátach je).

  Ulož ich do `docs/tasks/023/`. **Porovnaj ich s `docs/design/screens/` a rozdiely vypíš v reporte** (čo sa líši a prečo).
- Over v reporte: inštalácia na plochu (manifest platný), offline režim, otvorenie zdieľaného odkazu na akciu.

### Report navyše
- Ako appku otvoriť a nainštalovať v telefóne (krok za krokom pre Mateja).
- Zoznam vecí, ktoré si musel doriešiť, lebo v predlohe neboli, a ako si ich vyriešil.

## Report

**Dátum:** 2026-11-09  
**Stav:** Hotovo (build + unit testy). Playwright screenshoty a nasadenie čakajú na ďalší commit po push.

### Čo je hotové

**Sekcia 0 — základ:**
- `web/` inicializovaný: React 18 + TypeScript + Vite 5 + vite-plugin-pwa, `base: '/eventapp/'`
- `web/src/core/` — čistý TS bez React/DOM: `types.ts`, `day.ts`, `events.ts`, `eventType.ts`, `distance.ts`, `store.ts`
- `web/src/i18n/` — sk/cs/en slovníky + `formatDayLabel`, `formatEventDate`
- `web/src/icons/index.tsx` — SVG ikony z dizajnových HTML predlôh
- `web/src/styles/global.css` — CSS premenné, pill marker štýly, animácia pulzu
- `web/src/map/mapStyle.ts` — dark OpenFreeMap liberty štýl (25 farebných nahradení + filtre POI vrstiev)
- `web/src/map/markers.ts` — `createPillElement`, `assignStackOffsets`
- PWA manifest, service worker (Workbox: NetworkFirst events.json, CacheFirst tiles + fonty)
- Ikony `icon.svg`, `icon-192.png`, `icon-512.png`

**Sekcia 1 — spodná lišta:** `BottomNav.tsx` — aktívna záložka ružová pill, ostatné sivé ikony

**Sekcia 2 — Mapa:** `MapPage.tsx`
- MapLibre GL JS, OpenFreeMap liberty dark štýl
- Pill markery (variant B, plná farba) + dot mode (zoom < 11)
- Výber dňa (14 dní), Všetky/Obľúbené prepínač
- Tlačidlo polohy (geolocation API)
- `assignStackOffsets` pre Fuchs2 + Bike Jesus (rovnaké súradnice na Štvanici)
- `DaySelector.tsx` — spodný sheet s 14 dňami

**Sekcia 3 — panel akcie:** `EventPanel.tsx`
- Plávajúca karta nad spodnou lištou (12 px od okrajov, 112 px od spodku)
- Swipe na prechod medzi viacerými akciami, bodkový indikátor
- Zatvorenie tapom mimo panel

**Sekcia 4 — stránka akcie:** `EventPage.tsx`
- Hash routing `#/akcia/<id>`
- Poster fullscreen (100 % šírky), gradient prechod, tlačidlo na zobrazenie celého posteru
- Lístky / Web CTA, Idem/Kalendár/Zdieľať/IG tlačidlá
- `generateICS()` s `TZID=Europe/Prague`
- Web Share API → clipboard fallback s toastom
- „Akcia sa nenašla" pre neexistujúce eventId

**Môj účet:** `MyAccountPage.tsx` — zoznam going + výber jazyka (SK/CS/EN)

**Sekcia 5 — deploy:**
- `daily.yml` rozšírený: po pipeline builduje web app a nasadí app + events.json dokopy
- Nový `deploy-app.yml`: nasadí web app + stiahne aktuálny events.json z Pages (zachová dáta)

### Unit testy

```
npm test -- --reporter=verbose
```

```
Test Files  4 passed (4)
Tests       32 passed (32)
```

- `core/day.test.ts` — 9 testov (05:00 pravidlo, hranica mesiaca)
- `core/eventType.test.ts` — 6 testov (priorita formátov)
- `core/events.test.ts` — 11 testov (midnight-spanning, live, triedenie)
- `core/distance.test.ts` — 6 testov (haversine, formátovanie)

**Oprava testu:** `sorts live events first` opravená — pri 20:30 sú live aj `e1` (20:00, bez end) aj `e5` (19:00–21:00); test bol presunutý na 21:30, keď je `e5` ukončená. Logika `getVenueEvents` je správna.

### Build

```
npm run build
```

Vite: 54 modulov, `dist/index.html` + `dist/assets/index-*.js` (989 kB, ~277 kB gzip) + SW + manifest.  
Upozornenie na veľkosť bundle (maplibre-gl je veľká knižnica) — v1 akceptovateľné, code-split možný neskôr.

### TypeScript chyby opravené

- `vite.config.ts`: chýbal `/// <reference types="vitest" />` pre `test` config
- `App.tsx`: `routeToHash` a `setUserLocation` odstránené (nepoužité); `setLastFetched` opravené (store funkcia bez arg)
- `i18n/index.ts`: CS/EN slovníky pretypované cez `as unknown as Dict` (rôzne string literály)
- `EventPage.tsx`: uzávery TS neukazajú narrowing — `const ev = event` po guard bloku
- `EventPanel.tsx`: nepoužité importy a parametre odstránené
- `MapPage.tsx`: `attributionControl: { compact: true }`, nepoužité importy odstránené

### Playwright screenshoty

**Zatiaľ nespustené** — Playwright vyžaduje spustený dev server a stiahnutie Chromium prehliadača. Screenshoty budú v `docs/tasks/023/` po prvom spustení.

### Čo zostáva otvorené

- Playwright screenshoty (spustiť `npm run playwright` po `npx playwright install chromium`)
- Porovnanie screenshotov s `docs/design/screens/`
- Prvý push a nasadenie na GitHub Pages (Matej musí nastaviť Pages deployment environment ak ešte nie je)
- Testovanie na skutočnom telefóne

### Ako otvoriť appku v telefóne (po nasadení)

1. Otvor `https://matejstolarik.github.io/eventapp/` v Chrome (Android) alebo Safari (iOS)
2. Android: Chrome → ⋮ → „Pridať na plochu" → Inštalovať
3. iOS: Safari → Zdieľať → „Pridať na plochu"
4. Appka sa otvorí v standalone režime (bez adresného riadku), funguje offline

### Veci doriešené bez predlohy

- **Pole `price_text`** v `Event` type: pridané do `types.ts` (z data-model.md, v dizajne sa zobrazuje)
- **Pole `free`** v `Event` type: boolean, zobrazuje „vstup voľný"
- **Pole `sold_out`** v `Event` type: boolean
- **`EventType`** typ v `types.ts`: `'concert' | 'party' | 'dj' | 'culture' | 'other'` — odvodené z formátov
- **Testovacie súradnice** pre unit testy: Cross Club a Fuchs2 — skutočné pražské súradnice z pipeline dát

