# 076: Žánre kultúry v bloku kultúry, štítok `alternative` celý

## Zadanie

**Schválené Matejom 2026-11-19 12:32.** Len frontend (`web/`) → **pipeline nespúšťaj**, over nasadenie `deploy-app`. **Záväzné:** podľa `docs/design.md` 7b (blok „Zmena 2026-11-19 12:32“) a 4 (štítky); nič nevymýšľaj, drž štýl Filtra z 075. Čo nie je jasné, spýtaj sa.

**Čítaj:** report 075; `docs/design.md` 7b (bloky 12:32 a 075); `web/src/core/filter.ts`, `filter.test.ts`, `web/src/components/FilterSheet.tsx`, `data/genre_hierarchy.json`; pre štítok `web/src/i18n/index.ts`, `PlacesPage.tsx`, `VenuePage.tsx` (`grep -n "'alt'"`).

### 1. Žánre kultúry vo Filtri
- Žánre, ktorých rodič v hierarchii je `film`, `theatre` alebo `dance`, sa **nezobrazujú v sekcii Žáner**. Rodičia `film`/`theatre`/`dance` tiež nie (pokrývajú ich podtypy – rozhodnutie 3 z 075 potvrdené).
- V bloku kultúry pod čipmi podtypov: pre **každý vybratý podtyp, ktorý má žánre**, riadok s malým nadpisom podtypu (štýl ako popisky v paneli, napr. 11 px `#8E8AA6`) a čipmi jeho žánrov – vzhľad, počty, 0-čipy a poradie podľa počtu ako ostatné čipy. Bez vybratého podtypu žiadne žánre kultúry. Rovnaký názov pod dvoma podtypmi = dva samostatné čipy (kľúč podtyp + žáner).
- **Hudobné žánre** (sekcia Žáner) platia len pre akcie typu koncert, párty, DJ; kultúrna akcia sa hudobným žánrom nevyberá. V bloku kultúry sa hudobné žánre nezobrazujú.
- **Jedna logická skupina Žáner (ALEBO):** hudobné žánre aj žánre kultúry. Príklad: `techno` + film/`horror` = techno akcie (koncert/párty/DJ) aj hororové filmy.
- Odznak ráta aj zapnuté žánre kultúry. Voľby žánrov kultúry sa pamätajú (aj keď sa zruší výber podtypu alebo vypne Kultúra), ale vtedy neplatia.
- Uložený filter z 075 musí ostať platný (migrácia/ignorovanie neznámych kľúčov ako v `parseFilter`).

### 2. Štítok `alternative`
- Zruš skracovanie `alternative` → `alt` všade (i18n, Miesta, profil podniku, Filter). Zobrazí sa celé `alternative`.

## Overenie a report
- `npm test` – testy: žáner kultúry len pri vybratom podtype, film + theatre = dva riadky bez miešania, `drama` vo filme ≠ `drama` v divadle, hudobný žáner nevyberie kultúrnu akciu, `techno` + `horror` = zjednotenie, odznak, starý uložený filter sa načíta. `npm run build`; číslo nasadenia.
- Snímky JPEG 390 × 844 do `docs/tasks/076/`: `filter-film-divadlo.jpg` (Akcie, Najbližších 30 dní, vybraté `film` aj `theatre` – dva riadky žánrov), `miesto-alternative.jpg` (profil podniku so štítkom `alternative`).
- Report: čo hotové, otvorené body.

## Report

**2026-11-19**, kód + testy + snímky v commite uvedenom nižšie (report v tom istom commite). Len frontend – pipeline sa nespúšťala (`CLAUDE.md`).

### Hotové
- **Žánre kultúry** (`web/src/core/filter.ts`): nové pole `cultureGenres` (`podtyp:žáner`), `eventCultureGenres` (žáner, ktorého priamy rodič je podtyp akcie), `activeCultureGenres` (platí len pri zapnutej Kultúre a vybratom podtype), `availableCultureGenres` (riadky v poradí podtypov). Skupina Žáner = jedno ALEBO: hudobné žánre (len akcie koncert/párty/DJ) + platné žánre kultúry. Počty pri čipoch `counts.cultureGenres`, odznak ráta platné žánre kultúry. `parseFilter` načíta starý filter z 075 (bez poľa → `[]`), neplatné kľúče zahodí.
- **Panel** (`FilterSheet.tsx`): v bloku kultúry pod čipmi podtypov riadok pre každý vybratý podtyp so žánrami – nadpis podtypu 11 px `#8E8AA6`, čipy `NeutralChip` (vzhľad, počty, 0-čipy ako ostatné), poradie podľa počtu. Sekcia Žáner ponúka len hudobné žánre z koncertov/párty/DJ.
- **Štítok `alternative`** celý: zrušené skracovanie na `alt` v `i18n/index.ts` (`tagLabel` – Filter aj štítky akcií), `PlacesPage.tsx`, `VenuePage.tsx` (2 miesta).

### Rozhodnutia (samostatne, v `docs/decisions.md`)
1. Odznak a „nepredvolený filter“ rátajú len žánre kultúry, ktoré práve platia (zapamätané neplatné nie).
2. Poradie čipov v riadku sa určí, keď sa riadok prvýkrát ukáže, potom sa nemení.
3. Riadky žánrov kultúry bez „Všetky (N) ›“ – všetky čipy.
4. Kultúrna akcia sa hudobným žánrom už nevyberá (zadanie) – napr. film so žánrom `jazz` sa v sekcii Žáner neukáže ani nevyberie.

### Overenie
- `npm test`: **240 passed** (15 súborov); nové testy v `filter.test.ts` (blok „culture genres (task 076)“): riadky len pri vybratom podtype, film + theatre = dva riadky bez miešania, `film:drama` ≠ `theatre:drama`, hudobný žáner nevyberie kultúrnu akciu, `techno` + `horror` = zjednotenie, platnosť len pri vybratom podtype/zapnutej Kultúre (pamätá sa), odznak, počty, starý uložený filter z 075 sa načíta. Upravený test `tagLabel('alternative')`.
- `npm run build`: OK.
- Playwright `tests/playwright/screenshots-076.spec.ts` (dáta z Pages, čas 2026-11-19 17:00): 2 passed. `docs/tasks/076/riadky.json`: Akcie, Najbližších 30 dní, film + theatre → riadok film 9 čipov (animation 5, comedy 4, drama 2, family 2, …), riadok theatre 1 čip (physical theatre 1); po zapnutí jedného žánru filmu odznak **3**. Profil `cross-club` ukazuje `alternative`, text `alt` sa nenachádza.
- Snímky (JPEG 390 × 844) v `docs/tasks/076/`: `filter-film-divadlo.jpg`, `miesto-alternative.jpg` (neprezerané – pravidlo kreditov).
- Nasadenie `deploy-app`: doplnené nižšie po pushi.

### Otvorené
- Rozhodnutia 1–3 na potvrdenie Matejom.
- Plynulosť na telefóne neoverená (rovnako ako 075).
