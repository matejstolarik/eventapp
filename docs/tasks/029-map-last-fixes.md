# 029: Posledné opravy mapy po 028

## Zadanie
Zadal: hlavný chat, 2026-11-10. Po úlohe 028.

Matej: mapa je po 028 „veľmi smooth“, skoro perfektná. Ostali štyri veci. Malá úloha, nič iné nemeň.

### 1. Karta sa po návrate zo stránky akcie stratí
Ťuk na kartu → stránka akcie → Späť: mapa je na mieste, ale karta zmizne. Matej chce byť **presne tam, kde odišiel**: otvorená karta, rovnaké miesto, rovnaká akcia miesta (ak ich má viac).
- Príčina podľa hlavného chatu (over): Späť zo stránky akcie vyvolá `popstate`. Handler v `MapPage` (riadok ~293) vtedy zatvorí kartu vždy, keď je `panelOpenRef.current`, bez ohľadu na to, či sa vraciame zo stránky akcie. Kartu má zatvoriť len `popstate`, ktorý opúšťa záznam karty (`{ panel: 'open' }`) a vracia sa na mapu bez karty. Návrat zo stránky akcie späť na záznam karty ju má nechať otvorenú.
- Over celý reťazec: mapa → ťuk na pin (karta) → ťuk na kartu (stránka akcie) → Späť (karta otvorená, tá istá akcia) → Späť (karta zatvorená) → Späť (opustenie appky / predošlá stránka). Rovnako so šípkami a potiahnutím karty medzi tým.

### 2. Výber dňa: 6 dní + kalendár
Dnes sa ukáže 7 dní a siedmy je schovaný za spodnou lištou, nedá sa naň dostať a kalendár nie je vidieť.
- Vždy **6 možností dní** (v noci: „V noci“ + 5 dní) a ako siedma položka **„Iný dátum“** s kalendárom.
- Panel nesmie byť pod spodnou lištou: buď je nad ňou, alebo ju prekryje celú. Všetkých 7 položiek musí byť vidieť bez posúvania na obrazovke 390 × 844 aj na menšej 360 × 740.

### 3. Horná lišta
Matej si to rozmyslel:
- **tlačidlo dňa má meniť šírku podľa textu** („Dnes“, „V noci“, „So 15. 11.“),
- **Všetko | Obľúbené** zaberie zvyšok (`auto minmax(…,1fr) 44px`), s rozumnou minimálnou šírkou, aby sa „Obľúbené“ vždy zmestilo,
- texty dňa ostávajú krátke.

Do `design.md` to zapíše hlavný chat. Ty len uprav kód.

### 4. Fuchs2 a Bike Jesus sa stále prekrývajú
Dve príčiny:
- **Nové súradnice z 028 ešte nie sú v appke.** Appka berie miesta z `events.json`, ktorý vzniká v dennom behu, a ten bežal pred tvojím commitom. Po pushi spusti workflow „Daily pipeline“ ručne (alebo over, že ďalší beh súradnice preniesol) a v reporte uveď súradnice zo zverejneného `events.json`.
- **19 m je na mape málo:** pri bežnom priblížení je to pár pixelov a piny sa prekryjú takmer úplne. Matej chce stav ako v Google Maps: piny tesne pri sebe, prekrývajú sa len čiastočne. **Zobrazovacie pravidlo:** ak sú dva piny na obrazovke bližšie ako ~20 px, posuň ich vodorovne od seba tak, aby sa prekrývali približne do polovice (každý ±12 px, v smere ich skutočnej polohy, Fuchs2 na východ). Hroty ostávajú pri ich bodoch. Platí pre všetky takéto dvojice, nielen tieto dve. Prepočet po `zoomend`/`moveend`, ako kolízie mien. Pri priblížení, kde sú od seba dosť, sa nič neposúva.

### Overenie
- `npm test`, `npm run build`, úspešné nasadenie (číslo behu), ručný beh dát (číslo behu).
- **Snímky 390 × 844, jazyk `sk`** do `docs/tasks/029/`:
  - výber dňa (všetkých 7 položiek),
  - kalendár,
  - horná lišta s „Dnes“ a so „So 15. 11.“,
  - Fuchs2 + Bike Jesus pri dvoch priblíženiach,
  - karta pred odchodom na stránku akcie a po návrate.

  V 028 snímky chýbali úplne. Ak prehliadač v session nejde, spusti Playwright z `web/` (`npx playwright install chromium` a skript), nie cez nástroje session.

## Report
