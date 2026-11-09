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
