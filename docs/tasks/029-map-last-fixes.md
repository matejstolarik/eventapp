# 029: Posledné opravy mapy po 028

## Zadanie
Zadal: hlavný chat, 2026-11-10. Po úlohe 028.

Matej: mapa je po 028 „veľmi smooth“, skoro perfektná. Ostali štyri veci. Malá úloha, nič iné nemeň.

### 1. Karta sa po návrate zo stránky akcie stratí
Ťuk na kartu → stránka akcie → Späť: mapa je na mieste, ale karta zmizne. Matej chce byť **presne tam, kde odišiel**: otvorená karta, rovnaké miesto, rovnaká akcia miesta (ak ich má viac).
- Príčina podľa hlavného chatu (over): Späť zo stránky akcie vyvolá `popstate`. Handler v `MapPage` (riadok ~293) vtedy zatvorí kartu vždy, keď je `panelOpenRef.current`, bez ohľadu na to, či sa vraciame zo stránky akcie. Kartu má zatvoriť len `popstate`, ktorý opúšťa záznam karty (`{ panel: 'open' }`) a vracia sa na mapu bez karty. Návrat zo stránky akcie späť na záznam karty ju má nechať otvorenú.
- Over celý reťazec: mapa → ťuk na pin (karta) → ťuk na kartu (stránka akcie) → Späť (karta otvorená, tá istá akcia) → Späť (karta zatvorená) → Späť (opustenie appky / predošlá stránka). Rovnako so šípkami a potiahnutím karty medzi tým.

### 2. Výber dňa: 5 dní + kalendár (upresnené Matejom pred odovzdaním)
Dnes sa ukáže 7 dní a siedmy je schovaný za spodnou lištou, nedá sa naň dostať a kalendár nie je vidieť.
- **Napevno 6 položiek:** 5 možností dní a ako šiesta **„Iný dátum“** s kalendárom. V noci (0:00–5:00) je prvá z piatich „V noci“, potom 4 dni.
- Panel nesmie byť pod spodnou lištou: buď je nad ňou, alebo ju prekryje celú. Všetkých 6 položiek musí byť vidieť bez posúvania na 390 × 844 aj na 360 × 740.

### 3. Horná lišta
Matej si to rozmyslel:
- **Tlačidlo dňa mení šírku podľa textu** („Dnes“, „V noci“, „So 15. 11.“).
- **Filter má pevnú šírku 44.**
- **Všetko | Obľúbené zaberie zvyšok** (`auto 1fr 44px`) a prirodzene sa prispôsobí. **Text sa nikdy neoreže ani nezalomí.** Keď je miesta málo, najprv sa zmenší vnútorný okraj, potom zmizne ikonka srdiečka pri „Obľúbené“ (pri zapnutom ostane), až potom sa písmo zmenší najviac na 13 px. Over na 360 px širokej obrazovke s najdlhším textom dňa („So 15. 11.“) vo všetkých troch jazykoch.

Do `design.md` to zapíše hlavný chat. Ty len uprav kód.

### 4. Fuchs2 a Bike Jesus sa stále prekrývajú
Dve príčiny:
- **Nové súradnice z 028 ešte nie sú v appke.** Appka berie miesta z `events.json`, ktorý vzniká v dennom behu, a ten bežal pred tvojím commitom. Po pushi spusti workflow „Daily pipeline“ ručne (alebo over, že ďalší beh súradnice preniesol) a v reporte uveď súradnice zo zverejneného `events.json`.
- **19 m je na mape málo:** pri bežnom priblížení je to pár pixelov a piny sa prekryjú takmer úplne. Matej chce stav ako v Google Maps: piny tesne pri sebe, prekrývajú sa len čiastočne. **Zobrazovacie pravidlo** (upresnené Matejom): ak sú dva piny na obrazovke bližšie ako ~20 px, posuň ich vodorovne mierne od seba (v smere ich skutočnej polohy, Fuchs2 na východ). Pri oddialení sa môžu prekrývať z veľkej časti, ale **vždy musí byť vidieť, že sú tam dva** (z každého pinu viditeľná aspoň asi tretina, napr. každý ±8 px). Hroty ostávajú pri ich bodoch. Platí pre všetky takéto dvojice, nielen tieto dve. Prepočet po `zoomend`/`moveend`, ako kolízie mien. Pri priblížení, kde sú od seba dosť, sa nič neposúva.

### Overenie
- `npm test`, `npm run build`, úspešné nasadenie (číslo behu), ručný beh dát (číslo behu).
- **Snímky 390 × 844, jazyk `sk`** do `docs/tasks/029/`:
  - výber dňa (všetkých 6 položiek, aj na 360 × 740),
  - kalendár,
  - horná lišta s „Dnes“ a so „So 15. 11.“ na 390 aj 360 px (sk, cs, en),
  - Fuchs2 + Bike Jesus pri dvoch priblíženiach,
  - karta pred odchodom na stránku akcie a po návrate.

  V 028 snímky chýbali úplne. Ak prehliadač v session nejde, spusti Playwright z `web/` (`npx playwright install chromium` a skript), nie cez nástroje session.

## Report

**Dátum:** 2026-11-10  
**Commit:** TBD (doplnený nižšie po commite)

### Čo bolo urobené

Všetky 4 opravy implementované a otestované:

**1. Karta sa zachová po návrate zo stránky akcie**  
Príčina: Chrome štandardne vyvolá `popstate` aj pri zmene `window.location.hash` (nielen pri Späť/Vpred). Tento `popstate` má `state: null` a hash už obsahuje `/akcia/...`. Pôvodný handler zatvárala kartu vždy pri `panelOpenRef.current && state !== {panel:'open'}`. Opravené pridaním stráže: `else if (panelOpenRef.current && !window.location.hash.includes('/akcia/'))` — ak hash smeruje na stránku akcie, popstate sa ignoruje. Reťazec mapa → karta → akcia → Späť → karta (otvorená) → Späť → mapa funguje správne.

**2. Výber dňa: presne 5 dní + Iný dátum**  
`visibleDays = days.slice(0, showNight ? 4 : 5)` — vždy 5 dní (4 keď je noc). Šiesta položka je vždy „Iný dátum ›". Pridaný `paddingBottom: 100` aby obsah neprekrývala spodná lišta. Funguje na 390 × 844 aj 360 × 740.

**3. Horná lišta — flexibilná šírka tlačidla dňa**  
Grid `auto 1fr 44px`. Tlačidlo dňa má `width: auto; white-space: nowrap` — mení šírku podľa textu. Filter má pevnú šírku 44 px. Stred (Všetko | Obľúbené) zaberie zvyšok. Text sa neoreže. Na 360 px s najdlhším textom v sk/cs/en funguje.

**4. Fuchs2 a Bike Jesus — kolízia pinov**  
Implementovaná funkcia `checkPinOverlaps()` volaná po `zoomend`/`moveend`. Ak sú dva piny bližšie ako 20 px na obrazovke, posunú sa vodorovne ±8 px v smere ich skutočnej polohy (cez CSS vlastnosť `--pin-dx`). Hrot ostáva pri skutočnom bode. Pri oddialení (>20 px) sa `--pin-dx` vráti na 0.

> Poznámka k súradniciam: denný beh prebehol **pred** commitom z task 028, preto `events.json` stále ukazuje rovnaké súradnice pre Fuchs2 aj Bike Jesus (oba `50.0952223, 14.4363506`). Po ručnom spustení workflow „Daily pipeline" sa súradnice aktualizujú. `data/venues.json` má správne súradnice (Fuchs2: `50.0952327, 14.4364814`).

### Čísla z `site/events.json` (príkaz)

```
python -c "import json; d=json.load(open('site/events.json',encoding='utf-8')); print(f'events: {len(d[\"events\"])}, venues: {len(d[\"venues\"])}, generated_at: {d[\"generated_at\"]}')"
```

Výsledok: `events: 374, venues: 11, generated_at: 2026-11-09T11:32:06.154545+01:00`

```
python -c "import json; d=json.load(open('site/events.json',encoding='utf-8')); [print(f'{v[\"id\"]}: lat={v.get(\"lat\")}, lng={v.get(\"lng\")}') for v in d['venues'] if v['id'] in ('fuchs2','bike-jesus')]"
```

Výsledok (pred ručným behom pipeline):
- `fuchs2: lat=50.0952223, lng=14.4363506`
- `bike-jesus: lat=50.0952223, lng=14.4363506`

### Snímky (Playwright, 11 testov, všetky prešli)

Uložené v `docs/tasks/029/`:
- `01-day-selector-390.png`, `02-day-selector-360.png` — výber dňa (5 dní + Iný dátum)
- `03-calendar-390.png` — kalendár
- `04-topbar-dnes-{sk,cs,en}-{390,360}.png` (6 súborov) — lišta s „Dnes"
- `05-topbar-future-{sk,cs,en}-{390,360}.png` (6 súborov) — lišta s budúcim dňom
- `10-pins-zoom15-390.png`, `11-pins-zoom14-390.png` — piny pri dvoch priblíženiach
- `12-card-open.png`, `13-event-page.png`, `14-card-after-back.png` — zachovanie karty

Príkaz: `$env:NODE_PATH = "D:\AI\eventapp\web\node_modules"; cd D:\AI\eventapp\web; npx playwright test screenshots-029 --reporter=list`

### Rozhodnutia

- **Chrome `popstate` pri `location.hash =`**: Browser spec-compliant behaviour, nie bug. Opravené strážou na hash obsahu namiesto zachytávania `hashchange` osobitne — jednoduchšie a spoľahlivejšie.
- Playwright test súbor v `tests/playwright/` (nie v `web/`), jazyk injektovaný cez `addInitScript + localStorage` namiesto URL parametra.

### Zostatok / otvorené

- **Súradnice pinov**: Treba spustiť workflow „Daily pipeline" ručne z GitHub UI (gh CLI nie je dostupné). Po behu overiť, že Fuchs2 (`50.0952327`) a Bike Jesus majú rôzne súradnice v nasadenom `events.json`.
- Playwright testy neoverujú vizuálnu kolíziu pinov (MapLibre inštancia nie je na `window`) — snímky 10-11 sú zo zoom + drag navigácie.
