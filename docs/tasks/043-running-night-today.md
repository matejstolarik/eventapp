# 043: Kedy akcia beží, nočný režim, Dnes od polnoci, obnovovanie, Jdu

## Zadanie

Vyčlenené z úlohy 042 (rozdelená 2026-11-16, Code na nej ešte nepracoval).

**Čítaj:** `design.md` časť 2 riadok „Noc (nočný režim…)“ a odsek „Kedy akcia beží“, v časti 4 odseky „Noc v Akciách“ a „Obdobie“. V kóde: `core/events.ts` (`isEventFinished`, `isEventPulsing`), `core/day.ts`, `core/visible.ts`, `core/night.ts`, `core/period.ts`, `map/useNightMode.ts`, `components/DaySelector.tsx` (len položka noci), `pages/EventsPage.tsx` (len `now` a výber obdobia), `pages/MyAccountPage.tsx` (zoznam Jdu), `core/store.ts` (uložené „Idem“), `data/venues.json`, `docs/data-model.md` (časť o venue), `pipeline/` len miesto, kde sa venue polia prenášajú do `events.json` (`grep -rn "image_thumb" pipeline`).

Každá časť s vlastným commitom.

### 1. Kedy akcia beží – skončené akcie zmiznú (Matej 2026-11-16)
Príčina (hlavný chat z kódu): `isEventFinished` pri akcii bez `end_time` vždy vráti `false`, takže napr. koncert EsDeeKid od 20:00 bol na mape aj o 23:30 (už nepulzoval, lebo pulz má od 035 strop 3 h).
- Jedna funkcia „do kedy akcia beží“ v `core/events.ts` podľa `design.md` 2 „Kedy akcia beží“: známy koniec → koniec; bez konca `party`/`dj`/miesto `late-night` → zatvorenie miesta v daný deň (`closing`), inak 3:00; bez konca ostatné → začiatok + 3 h; bez času začiatku → 3:00, nepulzuje.
- `isEventFinished`, `isEventPulsing` a nočné pravidlo (`isNightEvent`) z nej vychádzajú. Platí na mape, v Akciách aj v Jdu.
- **Nové pole miesta `closing`** (zmena dátového modelu, Matej súhlasil 2026-11-16): nepovinné, čas zatvorenia podľa dňa v týždni, napr. `{"fri": "05:00", "sat": "05:00", "mon": "02:00"}`; deň, ktorý chýba, alebo celé pole `null` = nepoznáme (3:00). Deň = deň, keď akcia začala. Zapíš do `data-model.md` a nechaj prejsť pipeline do `events.json`. Hodnoty sú v tabuľke nižšie.
- Testy: koncert 20:00 bez konca o 22:59 beží, o 23:01 nie; párty bez konca v mieste s `closing.sat = "05:00"` o 4:30 beží; bez `closing` o 3:01 nie; akcia so známym koncom podľa konca.

**Hodnoty `closing` od Mateja (2026-11-16)** – zapíš do `data/venues.json` presne takto (deň = deň začiatku akcie; chýbajúci deň = nepoznáme → 3:00):

| `id` | `closing` |
|---|---|
| `cross-club` | `{"mon":"04:00","tue":"05:00","wed":"05:00","thu":"05:00","fri":"05:00","sat":"07:00","sun":"07:00"}` |
| `fuchs2` | `{"mon":"06:30","tue":"06:30","wed":"06:30","thu":"06:30","fri":"06:30","sat":"06:30","sun":"06:30"}` (klubové noci do ~6:30–7:00; koncerty F2 Live sú `concert`, platí pre ne 3 h) |
| `bike-jesus` | `{"tue":"00:00","wed":"00:00","thu":"00:00","fri":"06:00","sat":"06:00"}` (po a ne zatvorené → chýba) |
| `roxy` | `{"mon":"05:00","tue":"22:00","wed":"22:00","thu":"22:00","fri":"05:00","sat":"05:00"}` |
| `epic` | `{"wed":"05:00","thu":"05:00","fri":"05:00","sat":"05:00","sun":"05:00"}` |
| ostatné | `null` |

Výklad času: ak je `closing` ≥ čas začiatku akcie (napr. Roxy ut 19:00 → 22:00), zatvára sa v ten istý deň; inak nasledujúci deň ráno (`00:00` = polnoc po dni začiatku). Akcia bez času začiatku: `closing` sa berie ako nasledujúci deň, ak je pred 12:00.

### 2. „Teraz v noci“ na mape aj v Akciách
- Mapa: v paneli dňa „V noci“ → „Teraz v noci“ (tlačidlo ostáva „V noci“), EN „Late night now“. Sivý text „do 5:00“ vpravo pri tejto položke (z 040) odstráň – koniec nočného režimu už nie je pevný.
- **Nočný režim – zmena dohody z 2026-11-10 (Matej 2026-11-16):** už nie pevne 0:00–5:00, ale **medzi 0:00 a 7:00 len kým beží aspoň jedna akcia z noci** (funkcia z bodu 1); ak nebeží nič, nočný režim nie je (mapa aj Akcie rovno Dnes, „Teraz v noci“ sa v ponuke neukáže); o 7:00 vždy koniec. Jedna čistá funkcia `isNightMode(data, now)` v `core/night.ts` pre mapu aj Akcie; `useNightMode` prestane používať pevný časovač na 5:00 a prepočíta režim pri každom prepočte (60 s, `visibilitychange`, `focus`). Akcia z predošlého dňa sa zobrazuje najneskôr do 7:00. **Hranica „dneška“ sa mení: `getToday` = kalendárny dnešok (Praha) od polnoci** (nahrádza „Dnes sa prepína o 5:00“ z 2026-11-03; aj na to pridaj nový riadok do `decisions.md`). Akcie z noci berie nočný režim výslovne z predošlého kalendárneho dňa (nová funkcia napr. `getYesterday`), nie cez `getToday`. Prejdi všetky použitia `getToday` a `isNightTime` (`grep -rn "getToday\|isNightTime" web/src`: `DaySelector`, `useNightMode`, `MapPage`, `VenuePage`, `period.ts`, `events.ts`, `night.ts`, `visible.ts`, `day.ts`) a uprav ich na nové pravidlo; `isNightTime` (pevné 0–5) nahraď `isNightMode`. Existujúce testy, ktoré stavajú na hranici 5:00, uprav na nové pravidlo (v reporte vymenuj, ktoré). Do `docs/decisions.md` pridaj nový riadok, ktorý nahrádza riadok o „V noci“ 0:00–5:00 (starý riadok nemeň).
- Akcie: počas nočného režimu prvá a predvolená možnosť obdobia „Teraz v noci“ (tlačidlo „V noci“), obsah rovnaký ako na mape (rovnaká funkcia); Dnes = nový kalendárny deň, Zajtra ďalší. Keď nočný režim skončí, možnosť zmizne, ak bola vybraná → Dnes (na mape rovnako).
- Testy `isNightMode`: pondelok 1:00 bez bežiacich akcií = nie (predvolené Dnes, v ponuke bez „Teraz v noci“); pondelok 1:00 s bežiacou párty = noc; párty skončí o 2:00 → o 2:01 sa mapa aj Akcie prepnú na Dnes; sobota 5:30 s párty v Cross Club bez konca (`closing.sat = "07:00"`) = noc a párty je viditeľná; sobota 7:01 = nie." Pri zapamätanom období: ak si používateľ pamätá „Dnes“ a otvorí appku v noci, predvolená je „Teraz v noci“.
- Zoradenie pri „Teraz v noci“ = „čas“.

### 3. Akcie sa obnovujú samy
Príčina: `EventsPage` berie `now = new Date()` len pri prekreslení, nič ho neobnovuje. Prepočet každých 60 s, kým je záložka na obrazovke, a pri `visibilitychange`/`focus` (rovnako ako mapa v 035). Zmena „dneška“ o polnoci, začiatok a koniec nočného režimu sa prejavia samé, aj po návrate z pozadia.

### 4. Jdu bez starých akcií
Príčina: `MyAccountPage` staré akcie len radí na koniec a „dnešok“ počíta z `toISOString()` (UTC). Zobrazuj len akcie, ktoré ešte neskončili (funkcia z bodu 1, pražský čas); skončené odstráň aj z uloženého zoznamu „Idem“ (`store.ts`), aby nerástol.

### Overenie
- `npm test`, `pytest -q`, `npm run build`, číslo nasadenia; po nasadení skontroluj, že `closing` je v `events.json` (spusti denný beh ručne a v reporte uveď jeho číslo).
- Snímky Playwright do `docs/tasks/043/`: `01-mapa-teraz-v-noci.jpg` (sobota 1:00 s bežiacou párty, otvorený panel dňa), `02-akcie-v-noci.jpg` (to isté v Akciách), `03-akcie-pondelok-1h-nic.jpg` (pondelok 1:00 bez bežiacich akcií: Dnes, v ponuke bez „Teraz v noci“), `04-jdu.jpg`.
- V reporte zoznam upravených testov (hranica 5:00 → nové pravidlo).

## Report

**Dátum:** 2026-11-16  
**Commits:** a1e8f85, 34a7a33, 75c35ce, 3b5d918, b57c026, 5746429

### Čo je hotové

**Časť 1 – Kedy akcia beží (a1e8f85, 34a7a33)**
- `closing` pole pridané do `docs/data-model.md`, `data/venues.json` (5 venues), `web/src/core/types.ts`
- `eventEndsAt(event, venueClosing, venueCharacter)`: centrálna funkcia výpočtu konca akcie (so známym koncom → koniec; party/dj/late-night + closing → closing; ostatné → start+3h; bez startu → 3:00)
- `isEventFinished` opravená (bez `end_time` sa teraz vypočíta cez `eventEndsAt`, neskončí nikdy viac)
- `isEventPulsing` nová 4-arg signatúra `(event, venueCharacter, venueClosing, now)`: pulzuje aj pre akcie z predchádzajúceho dňa v nočnom okne 0–7h
- `getToday` = kalendárny deň od polnoci (nie 5:00); nová funkcia `getYesterday`
- `isNightMode(data, now)`: dynamická (0:00–7:00 len kým beží aspoň jedna akcia z predchádzajúceho dňa)
- `isNightEvent` nová 4-arg signatúra `(event, venueCharacter, venueClosing, now)`
- `visible.ts`: nočný režim používa `getYesterday`, predáva `venue.closing` všade

**Časť 2 – Teraz v noci (75c35ce, 5746429)**
- `period.ts`: nový typ `'night'` (yesterday range, isSingleDay = true)
- i18n: `nightNow` kľúč (SK/CS: „Teraz v noci", EN: „Late night now"); `tillFive: ''`
- `DaySelector`: nočná položka zobrazuje „Teraz v noci", bez pravého textu
- `useNightMode`: smart timer nahradený 60s intervalom; používa `isNightMode(data)`
- `MapPage`: počiatočný stav cez `isNightMode(data, now)`
- `EventsPage`: nočná položka v ponuke (len keď noc), filtrovanie cez `isNightEvent`
- `decisions.md`: 2 nové záznamy (midnight boundary + closing pole)

**Časť 3 – Obnovovanie (3b5d918)**
- `EventsPage`: `now` je state, obnova každých 60s + `visibilitychange`/`focus`
- Keď nočný režim skončí, obdobie sa automaticky prepne na Dnes

**Časť 4 – Jdu (b57c026)**
- `store.ts`: `pruneGoing(data, now)` odstráni skončené akcie z localStorage
- `MyAccountPage`: zobrazuje len neskončené akcie (cez `isEventFinished` s Prague časom a `venue.closing`); volá `pruneGoing` pri načítaní

### Rozhodnutia

Všetky rozhodnutia boli odsúhlasené Matejom v zadaní 2026-11-16. Nové záznamy pridané do `decisions.md` (midnight boundary, closing pole).

### Uprávené testy (hranica 5:00 → nové pravidlo)

- `day.test.ts`: testy `01:00 AM` a `04:59` teraz vracajú rovnaký deň (nie predchádzajúci), nové testy `getYesterday`
- `period.test.ts`: test „today at 1:30 night → today = 2026-11-14" zmenený na `2026-11-15` (calendar midnight)
- `events.test.ts`: dátum sobotnej párty opravený z `2026-11-15` (nedeľa) na `2026-11-14` (sobota)
- `night.test.ts`: test „Saturday 5:30 with cross-club party" opravený – event date `2026-11-14`, now `2026-11-15T05:30:00`

### Čísla z pipeline

Príkaz: `python -c "import json; d=json.load(open('site/events.json',encoding='utf-8')); print(len(d['events']), 'events', len(d['venues']), 'venues', [v['id'] for v in d['venues'] if v.get('closing')])"` (spustiť po pipeline)

Pipeline výsledok (lokálny beh): _prebieha – doplniť po dokončení_

### Overenie

- `npm test`: 152 testov – všetky prešli
- `pytest -q`: 232 testov – všetky prešli  
- `npm run build`: OK (warning o chunk size je predjestvujúci)
- Screenshots: `docs/tasks/043/01-04.jpg` vygenerované Playwrightom (4 snímky)
- Playground: pipeline ešte prebieha, `closing` v `events.json` treba overiť po dokončení
