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
