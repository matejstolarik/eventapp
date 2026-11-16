# 042: Akcie – zbaliteľná hlavička, šípka navrch, návrat Späť, drobnosti

## Zadanie

**Čítaj:** `design.md` časť 2 riadok „Noc (nočný režim…)“ a odsek „Kedy akcia beží“, časť 4 (riadky „Riadok pod lištou“, „Pri scrolle“, „Zmena = navrch“, „Šípka navrch“, „Ťuk na aktívnu záložku“, „alt“) a časť 5 (prvý riadok); snímka `docs/design/screens/13-akcie-zbalene.png` a HTML `docs/design/html/13-akcie-zbalene.html`. V kóde: `web/src/App.tsx` (`parseHash`, `navigate`, `goBack`, `handleTabChange`, vykreslenie záložiek), `pages/EventsPage.tsx`, `pages/PlacesPage.tsx`, `components/BottomNav.tsx`, `core/events.ts` (`isEventFinished`, `isEventPulsing`), `core/visible.ts`, `core/night.ts`, `core/period.ts`, `pages/MyAccountPage.tsx` (zoznam Jdu), `docs/data-model.md` (časť o venue), miesto, kde sa vykresľujú štítky (`grep -rn "character" web/src --include=*.tsx`).

Matejove poznámky po teste 041. Malé, samostatné časti; každá s vlastným commitom.

### 1. Späť zo stránky akcie → mapa (chyba)
Príčina (hlavný chat z kódu): záložky `events` a `account` nemajú vlastný hash. `parseHash` pre prázdny hash vráti `map`; po `history.back()` zo `#/akcia/…` sa hash vráti na prázdny a `onHashChange` prepne na mapu. Navyše `EventsPage` sa pri otvorenej stránke akcie odmontuje (`activeTab === 'events' && !isOverlay`), takže by sa stratil text hľadania aj scroll.
- Pridaj routy `#/akcie` a `#/ucet` (parseHash, navigate, handleTabChange, onHashChange). Prepnutie záložky nastaví hash; Späť zo stránky akcie/miesta vráti na záložku, z ktorej prišiel používateľ.
- `EventsPage` (a `MyAccountPage`) ostávajú namontované aj pod stránkou akcie (skryté, ako mapa), aby sa zachoval stav: obdobie, Pre teba/Nové, otvorené hľadanie s textom, zoradenie a **pozícia scrollu**.
- Test: `parseHash` pre nové routy; prechod Akcie → akcia → Späť = Akcie.

### 2. Kedykoľvek bez počtu
Pri období Kedykoľvek sa vľavo nad mriežkou nezobrazuje počet (ani „· N pre teba“); vpravo ostáva Zoradiť.

### 3. Zbaliteľná hlavička
Podľa `design.md` 4 „Pri scrolle“ a snímky `13`: pri scrolle nadol odíde nadpis a riadok s počtom/zoradením; prilepená ostane kompaktná lišta (obdobie, Pre teba, Nové, lupa, miesto pre Filter). Prechod plynulý (hlavička scrolluje normálne so zoznamom, kompaktná lišta je `position: sticky` – žiadne skoky obsahu, žiadne prepočítavanie pri každom pixeli scrollu v Reacte; ak treba sledovať scroll, `IntersectionObserver` na hlavičke). Ťuk na lupu v kompaktnej lište: navrch + rozbalenie + otvorenie hľadania. Animácia hľadania z 041 sa nesmie rozbiť.
Poznámka k 041: roztiahnutie poľa hľadania je urobené cez `scaleX`; ak sa pri ňom text alebo ikona v poli počas animácie deformuje, zmeň na animáciu šírky (`width` / `clip-path`).

### 4. Zmena = navrch
Po akejkoľvek zmene obdobia, Pre teba, Nové, zoradenia alebo textu hľadania (po debounce) sa zoznam plynulo vyroluje navrch (`scrollTo({top:0, behavior:'smooth'})`) a hlavička sa rozbalí.

### 5. Šípka navrch + ťuk na aktívnu záložku (Akcie aj Miesta)
- Okrúhle tlačidlo podľa `design.md` 4 (44 px, `#23232F`, šípka nahor, vpravo 16 px, spodok 116 px), objaví sa po odscrollovaní ~2 výšok obrazovky, ťuk → plynulý scroll navrch, potom zmizne. V Akciách aj v Miestach.
- Ťuk na už aktívnu záložku Akcie alebo Miesta v `BottomNav` vyroluje zoznam navrch.

### 6. `alternative` → `alt`
Štítok `alternative` sa všade v UI (karty Akcií, profil miesta, karta na mape, filter) zobrazuje ako `alt`. Len zobrazenie (jedna mapovacia funkcia pre popisky štítkov), dáta sa nemenia.

### 7. Plynulé animácie (Matej 2026-11-15)
Všetko z bodov 3–5 a zmeny obsahu mriežky majú ísť plynulo, nič nesmie skočiť:
- **Lupa** sa pri zbalení hlavičky presunie z hlavičky do kompaktnej lišty plynulo (napr. prelínanie + posun, ~200 ms), pri rozbalení naspäť. Nadpis a riadok s počtom pri odchode stmavnú/vyblednú spolu so scrollom, nie naraz.
- **Karty pri zmene filtra** (obdobie, Pre teba, Nové, hľadanie, zoradenie): odchádzajúce karty krátko vyblednú (opacity + scale 1 → 0,96, ~120 ms), nové sa objavia (opacity 0 → 1, scale 0,96 → 1, ~180 ms, `ease-out`), v štýle objavovania pinov na mape. Animuj len karty vo viditeľnej časti (prvé ~12), ostatné bez animácie. Súčasne s plynulým scrollom navrch (bod 4), bez trhania.
- **Šípka navrch** sa objaví/zmizne prelínaním (~150 ms).
- Len `opacity` a `transform` (žiadne animácie výšky/šírky v zozname), `prefers-reduced-motion` = bez animácií.
- Over na pomalšom zariadení: v DevTools CPU 4× spomalenie, scroll a zmena filtra bez viditeľného trhania; v reporte jedna veta, ako to dopadlo.

### 8. Kedy akcia beží – skončené akcie zmiznú (Matej 2026-11-16)
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

### 9. „Teraz v noci“ na mape aj v Akciách
- Mapa: v paneli dňa „V noci“ → „Teraz v noci“ (tlačidlo ostáva „V noci“), EN „Late night now“. Sivý text „do 5:00“ vpravo pri tejto položke (z 040) odstráň – koniec nočného režimu už nie je pevný.
- **Nočný režim – zmena dohody z 2026-11-10 (Matej 2026-11-16):** už nie pevne 0:00–5:00, ale **medzi 0:00 a 7:00 len kým beží aspoň jedna akcia z noci** (funkcia z bodu 8); ak nebeží nič, nočný režim nie je (mapa aj Akcie rovno Dnes, „Teraz v noci“ sa v ponuke neukáže); o 7:00 vždy koniec. Jedna čistá funkcia `isNightMode(data, now)` v `core/night.ts` pre mapu aj Akcie; `useNightMode` prestane používať pevný časovač na 5:00 a prepočíta režim pri každom prepočte (60 s, `visibilitychange`, `focus`). Akcia z predošlého dňa sa zobrazuje najneskôr do 7:00. **Hranica „dneška“ sa mení: `getToday` = kalendárny dnešok (Praha) od polnoci** (nahrádza „Dnes sa prepína o 5:00“ z 2026-11-03; aj na to pridaj nový riadok do `decisions.md`). Akcie z noci berie nočný režim výslovne z predošlého kalendárneho dňa (nová funkcia napr. `getYesterday`), nie cez `getToday`. Prejdi všetky použitia `getToday` a `isNightTime` (`grep -rn "getToday\|isNightTime" web/src`: `DaySelector`, `useNightMode`, `MapPage`, `VenuePage`, `period.ts`, `events.ts`, `night.ts`, `visible.ts`, `day.ts`) a uprav ich na nové pravidlo; `isNightTime` (pevné 0–5) nahraď `isNightMode`. Existujúce testy, ktoré stavajú na hranici 5:00, uprav na nové pravidlo (v reporte vymenuj, ktoré). Do `docs/decisions.md` pridaj nový riadok, ktorý nahrádza riadok o „V noci“ 0:00–5:00 (starý riadok nemeň).
- Akcie: počas nočného režimu prvá a predvolená možnosť obdobia „Teraz v noci“ (tlačidlo „V noci“), obsah rovnaký ako na mape (rovnaká funkcia); Dnes = nový kalendárny deň, Zajtra ďalší. Keď nočný režim skončí, možnosť zmizne, ak bola vybraná → Dnes (na mape rovnako).
- Testy `isNightMode`: pondelok 1:00 bez bežiacich akcií = nie (predvolené Dnes, v ponuke bez „Teraz v noci“); pondelok 1:00 s bežiacou párty = noc; párty skončí o 2:00 → o 2:01 sa mapa aj Akcie prepnú na Dnes; sobota 5:30 s párty v Cross Club bez konca (`closing.sat = "07:00"`) = noc a párty je viditeľná; sobota 7:01 = nie." Pri zapamätanom období: ak si používateľ pamätá „Dnes“ a otvorí appku v noci, predvolená je „Teraz v noci“.
- Zoradenie pri „Teraz v noci“ = „čas“.

### 10. Akcie sa obnovujú samy
Príčina: `EventsPage` berie `now = new Date()` len pri prekreslení, nič ho neobnovuje. Prepočet každých 60 s, kým je záložka na obrazovke, a pri `visibilitychange`/`focus` (rovnako ako mapa v 035). Zmena „dneška“ o polnoci, začiatok a koniec nočného režimu sa prejavia samé, aj po návrate z pozadia.

### 11. Jdu bez starých akcií
Príčina: `MyAccountPage` staré akcie len radí na koniec a „dnešok“ počíta z `toISOString()` (UTC). Zobrazuj len akcie, ktoré ešte neskončili (funkcia z bodu 8, pražský čas); skončené odstráň aj z uloženého zoznamu „Idem“ (`store.ts`), aby nerástol.

### 12. Štítky na obrázku (Matej 2026-11-16)
Štítky karty v Akciách sa presunú zo samostatného riadku pod obrázkom **na spodok obrázka**: 6 px od ľavého a spodného okraja, jeden riadok, štítky s tmavým pozadím `rgba(17,17,24,0.85)` a textom `#F4F2FF` (aj obrysové štítky charakteru dostanú rovnaké tmavé pozadie, obrys rovnakej farby), na pravom okraji obrázka sa strácajú. Pod obrázkom ostáva dátum · čas, názov, miesto. Odznaky hore (pre teba, nové) bez zmeny. Zapíš do `design.md` 4 (odsek Karta) a uprav `docs/design/html/10-akcie-mriezka.html` len ak je to jednoduché; inak stačí text v `design.md`.

### Overenie
- `npm test`, `npm run build`, číslo nasadenia.
- Snímky Playwright do `docs/tasks/042/`: `01-akcie-kedykolvek.jpg` (bez počtu), `02-akcie-zbalene.jpg` (odscrollované, kompaktná lišta + šípka), `03-miesta-sipka.jpg`, `04-akcie-v-noci.jpg` (zmrazený čas pondelok 0:45, otvorený panel obdobia), `05-akcie-stitky-na-obrazku.jpg`.
- V reporte postup, ako si Matej overí bod 1 v telefóne.

## Report

**Zrušené 2026-11-16 (Matej): úloha bola príliš veľká, Code ju zastavil pred začiatkom práce. Rozdelená na `043-running-night-today.md` (časti 8–11) a `044-akcie-scroll-back-anim.md` (časti 1–7 a 12). Táto úloha sa nerobí.**
