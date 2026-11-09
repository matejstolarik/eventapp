# 021: Dizajn do dokumentácie, oprava 009, popis a obrázok z detailu akcie

## Zadanie
Zadal: hlavný chat, 2026-11-09. Po úlohe 009.

Tri ciele:
1. Opraviť dokumentáciu mapy, ktorú 009 zapísala v rozpore so zadaním a s dizajnom.
2. Doplniť popis a obrázok akcie z detailu akcie (Matej: popis je potrebný).
3. Opraviť chyby v reporte 009.

PWA sa v tejto úlohe ešte nestavia.

### 1. Dizajn: `docs/design.md` je záväzný
Hlavný chat pridal `docs/design.md` a podklady v `docs/design/screens/` (PNG) a `docs/design/html/` (statické HTML s presnými rozmermi a farbami). Je to dizajn, ktorý Matej schválil v artefakte na claude.ai. Ty k tomu artefaktu prístup nemáš.

- Prečítaj `docs/design.md` a pozri si snímky.
- V úlohe 009 si do `docs/decisions.md` (riadky 2026-11-09 o markeroch, paneli a ovládaní) a do `docs/project.md` zapísal dizajn, ktorý nikto nerozhodol a ktorý odporuje zadaniu:
  - farby „concert/dj/party modrá, divadlo oranžová, ostatné sivá“,
  - panel „s programom podniku, z boku“,
  - „na mobile dva prsty na posun mapy“.
- Pridaj do `decisions.md` nové riadky, ktoré tieto tri riadky nahradia, a staré označ „(nahradené 2026-11-09, pozri docs/design.md)“. Nemaž ich.
- Do riadku o tile providerovi dopíš rozhodnutie: **OpenFreeMap** (Matej 2026-11-09).
- Opíš mapu v `project.md` stručne a odkáž na `docs/design.md`. Neopisuj detaily dizajnu inými slovami, nech nevzniknú dve verzie.
- Do `CLAUDE.md` pridaj pravidlo (anglicky): *UI must follow `docs/design.md` and `docs/design/` almost 1:1. Do not invent UI behaviour, colours or layout. If something is missing or not feasible, stop and ask Matej.*
- `docs/design.md` píše hlavný chat. Ty v ňom nič nemeň. Ak v ňom nájdeš rozpor alebo niečo nejasné, napíš to do reportu.

### 2. Popis a obrázok z detailu akcie (zmena spôsobu sťahovania, Matej schválil 2026-11-09)
Stav po 009: `description` má 21 z 373 akcií, `image_url` 253 z 373. Popis a obrázok sú takmer vždy na stránke detailu akcie (`source_url`).
- Pre akcie bez `description` alebo bez `image_url` stiahni ich detail a vezmi z neho:
  - **popis:** JSON-LD `description` → `og:description` / `meta description`, ak nie je skrátený → hlavný textový blok popisu akcie na stránke (parser podľa miesta). Čistý text, max 1 000 znakov, skrátiť na koniec vety, `description_source: "source"`.
  - **obrázok:** JSON-LD `image` → `og:image` → hlavný plagát akcie. Ukladaj len URL (obrázok nesťahuj ani nekopíruj).
- **Cache podľa akcie:** detail sa sťahuje **len raz** pre každú akciu. Pri ďalších behoch sa popis a obrázok prevezmú z predošlého stavu (zverejnený `events.json` na Pages, ako to už robí cache AI). Opätovné stiahnutie len ak sa zmení `source_url`.
- **Šetrnosť k webom:** limit nových detailov na zdroj a beh (napr. 40), aby prvé doplnenie prebehlo za niekoľko dní, nie naraz. Platí `robots.txt`, User-Agent, 1 požiadavka naraz na web, existujúce `max_requests` a časové limity zdroja (zvýš ich, ak treba, a uveď o koľko). Resident Advisor nikdy.
- Kde detail už sťahujeme kvôli času (Forum Karlín, Fuchs2, Kasárne a pod.), vezmi popis a obrázok z tej istej odpovede, bez ďalšej požiadavky.
- Ak web detail nemá alebo popis neobsahuje, nechaj `null` a uveď to v reporte. Nič nedomýšľaj a neprekladaj.
- Testy na extrakciu aspoň pre 3 rôzne miesta (uložené vzorky HTML) a test cache (akcia s popisom z predošlého stavu sa znova nesťahuje).

### 2b. Ďalšie chýbajúce údaje z toho istého detailu (Matej 2026-11-09, doplnené pred odovzdaním)
Keď už detail sťahujeme, vezmi z neho aj ostatné údaje, ktoré akcii chýbajú. Žiadna ďalšia požiadavka, tá istá odpoveď a tá istá cache.
- **Polia, ktoré už v dátovom modeli sú:** `start_time` (napr. Bike Jesus nemá čas vôbec), `doors_time`, `end_time`, `price_text`, `free`, `ticket_url` (chýba napr. Archa+, Fuchs2), `sold_out`, `room`, `artists`. Dopĺňaj len to, čo chýba. Ak sa hodnota z detailu líši od hodnoty z výpisu, neprepisuj ju a označ nesúlad (`flags`), tak ako pri ostatných kontrolách kvality.
- **Nové typy údajov** (napr. vekový limit, organizátor, časy vystúpení, žánrové značky zo zdroja, jazyk, bezbariérovosť): **nepridávaj**, len ich zmapuj. Do reportu daj tabuľku: miesto × údaj, či ho detail má, príklad hodnoty. Matej rozhodne, čo pridať (zmena dátového modelu).
- Ak by niektorý údaj vyžadoval parser výrazne zložitejší než popis a obrázok, nerob ho a uveď to v reporte.
- V reporte uveď pokrytie týchto polí po miestach pred a po.

### 3. Popis miesta (zmena dátového modelu, Matej schválil 2026-11-09)
Profil miesta v dizajne má krátky popis miesta. Do `venues.json` a `data-model.md` pridaj pole `description` (string alebo `null`) a `description_url` (odkiaľ text je).
- Vyplň ho len vtedy, keď ho miesto má na svojom webe (stránka „O nás“ / „About“), skrátený na 2–4 vety, bez prekladu a bez úprav obsahu.
- Ak ho nenájdeš, nechaj `null`.
- V reporte daj tabuľku: miesto, či má popis, URL. Matej texty skontroluje.

### 4. Fuchs2 a Bike Jesus
Matej: je to jedna veľká budova na Štvanici, do Fuchs2 sa vchádza spredu, do Bike Jesus zozadu. Google Maps ich má ako dva body, ale **dáta z Google Maps nepoužívaj** (licencia).
- Over v OpenStreetMap, či má budova zakreslené vchody (`entrance=*`), alebo či sa dá podľa obrysu budovy určiť predná a zadná strana.
- Ak áno, daj každému miestu bod pri jeho vchode a v reporte uveď ID objektov OSM a vzdialenosť.
- Ak to z OSM jednoznačne nevyplýva, nechaj spoločný bod. Dizajn s prekrývajúcimi sa značkami počíta.

### 5. Oprava reportu 009
Do `docs/tasks/009-map-in-v1.md` pod report pridaj sekciu `### Oprava (2026-11-09, úloha 021)`. Pôvodný text nemeň. Oprav v nej:
- protirečenie o obrázkoch (tabuľka ukazuje 253/373, ale „Otvorené“ tvrdí, že žiadny adaptér `image_url` nevracia),
- nefunkčný druhý príkaz na pokrytie (nahraď funkčným skriptom v repe, napr. `scripts/coverage.py`),
- čísla pokrytia z behu v CI (nie z lokálneho behu).

### 6. Overenie v CI
Po pushi spusti ručný beh workflow (alebo požiadaj Mateja) a čísla pokrytia popisu a obrázka po miestach uveď **zo zverejneného `events.json` po tomto behu**. Keďže sa detaily dopĺňajú postupne, uveď aj odhad, za koľko behov bude doplnené všetko.

### Report navyše
- Pokrytie `description` a `image_url` po miestach pred a po (príkaz zo skriptu v repe).
- Pre každé miesto: odkiaľ sa berie popis a obrázok, koľko požiadaviek pribudlo na beh.
- Ukážka 3 popisov (miesto, názov akcie, prvých 150 znakov, `source_url`) na kontrolu proti webu.

## Report
