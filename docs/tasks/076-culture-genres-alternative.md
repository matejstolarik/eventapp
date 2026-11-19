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
