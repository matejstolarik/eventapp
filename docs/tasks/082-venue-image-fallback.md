# 082: Obrázok miesta ako náhrada za chýbajúci obrázok akcie

## Zadanie

**Schválené Matejom 2026-11-20 14:21–14:34** (vrátane **zmeny dátového modelu** – nové polia miesta). Mení dáta (obrázky miest v pipeline) aj appku → **jeden beh pipeline na konci**, raz počkaj (`CLAUDE.md`). Čo nie je jasné, spýtaj sa.

**Pravidlo (Matej):** keď akcia nemá obrázok, appka ukáže obrázok miesta. Akcia v dátach ostáva bez obrázka (`image_url: null` – nevymýšľame dáta), náhradu robí appka. Miesto bez obrázka (dnes Roxy) → ako doteraz ikona typu.

**Čítaj:** `docs/data-model.md` (miesto: `image_url`, `image_thumb`; akcia: `image_thumb`, `image_detail`, `image_detail_size`); `pipeline/thumbs.py` (`generate_thumbs`, `make_event_thumb`, `generate_event_images`, `event_detail_size`), `pipeline/main.py` (kde sa volajú); `.github/workflows/daily.yml` a `deploy-app.yml` (kopírovanie `img/venues`, `img/events` – **nasadenie appky nesmie nové súbory zmazať**, pozor na chybu z `5cd07ad`); v appke `web/src/components/EventRow.tsx` (`hasImg`), `EventPanel.tsx`, `pages/EventPage.tsx` (`heroCandidates`, „Plagát“), Môj účet a program miesta (`grep -rn "image_thumb" web/src`).

### 1. Dátový model a pipeline
- `docs/data-model.md`, miesto – nové polia (popis ako pri akcii):
  - `image_card`: `img/venues/card/<id>.jpg`, 640×480 JPEG, **rovnaký algoritmus ako náhľad akcie** (`make_event_thumb`: na výšku celý na rozmazanej výplni, inak stredový výrez 4 : 3);
  - `image_detail`: `img/venues/detail/<id>.jpg`, dlhšia strana najviac 1200 px, bez orezu, menší sa nezväčšuje;
  - `image_detail_size`: `[šírka, výška]` alebo `null`.
  - Všetky `null`, keď `image_url` je `null` alebo stiahnutie zlyhalo. `image_thumb` (160×160) ostáva bez zmeny.
- Generuje pipeline z `image_url` miesta spolu s doterajším náhľadom (**jedno stiahnutie**, cache podľa URL – pri nezmenenej adrese sa nesťahuje znova; pri zmene adresy sa prerobí). Limit pokusov a timeout ako pri obrázkoch miest; chyba = varovanie, beh pokračuje.
- `daily.yml` aj `deploy-app.yml` prenesú nové priečinky (`img/venues/card`, `img/venues/detail`) rovnako ako ostatné obrázky.

### 2. Appka – náhrada všade, kde sa ukazuje obrázok akcie
- Riadok v Akciách, karta na mape (panel akcie), stránka akcie, Môj účet (Idem), program miesta, onboarding/Hotovo nie (tam sú abstraktné ukážky).
- Poradie: obrázok akcie (`image_thumb` / `image_detail`) → obrázok miesta (`image_card` v náhľadoch, `image_detail` + `image_detail_size` na stránke akcie) → ikona typu. Pri chybe načítania obrázka akcie (`onError`) skús obrázok miesta, potom ikonu typu.
- **Stránka akcie s obrázkom miesta (návrh hlavného chatu, Matej k nemu nepovedal nie):** bez tlačidla „Plagát“ (zoom), bez označenia „foto miesta“. Rezervácia miesta podľa `image_detail_size` miesta (bez posunu rozloženia).
- Odznaky na obrázku (new, ✦ pre teba) aj na obrázku miesta, rovnako ako na obrázku akcie.

### 3. Nové obrázky miest (Matej, pred spustením)
- Matej zmenil `image_url` (a `image_source`) vo `venues.json`: **Bike Jesus** (`d1b37a3`), **Čitárna Unijazz**, **Palác Akropolis** (Wikimedia Commons), **Roxy** (prvý obrázok vôbec; zo stránky firmy.cz) (`d700202`). Pipeline ich spracuje ako ostatné (cache podľa URL → stiahnu sa znova).
- Akropolis: adresa má na konci sledovacie parametre (`?utm_source=…`) – ak prekážajú (cache, sťahovanie), odstráň ich vo `venues.json`; obrázok je ten istý.
- Ak niektorý obrázok nejde stiahnuť (napr. obmedzenie CDN pri Roxy), zapíš to do reportu, nič nevymýšľaj ani nehľadaj náhradu – Matej vyberie inú.
- Autora ani licenciu pri obrázkoch neriešiť (Matej 2026-11-20).

## Overenie a report
- `pytest -q`, `npm test -- --reporter=dot` (náhrada: akcia bez obrázka + miesto s obrázkom → obrázok miesta; miesto bez obrázka → ikona; chyba načítania → miesto → ikona; „Plagát“ sa pri obrázku miesta neukáže), `npm run build`; **jeden beh pipeline** (číslo), nasadenie `deploy-app` (číslo). Over na Pages, že `img/venues/card/*` a `img/venues/detail/*` existujú aj po nasadení appky.
- Z publikovaného `events.json` (príkaz uveď): koľko akcií nemá obrázok (spolu a po miestach) a koľko z nich teraz dostane obrázok miesta; ktoré miesta nemajú `image_card` a prečo.
- **Prehľad obrázkov miest pre Mateja:** jedna mriežka JPEG `docs/tasks/082/venue-images.jpg` – každé miesto: `image_card` 640×480 zmenšený, pod ním id miesta, rozmery originálu (`image_detail_size`) a typ súboru (napr. logo PNG). Neposudzuj vhodnosť, len vypíš; Matej vyberie, čo vymeniť. Upozorni na originály menšie ako 640 px na šírku (napr. MeetFactory 320×426).
- Snímky JPEG 390 × 844 do `docs/tasks/082/`: `events-bike-jesus.jpg` (Akcie s akciami Bike Jesus – obrázok miesta v riadkoch), `event-page-venue-image.jpg` (stránka akcie Bike Jesus).

## Report

**2026-11-20** · commity `17a62e4` (práca), report v nasledujúcom commite · pipeline `daily` run **44748943631** (OK, `generated_at` 2026-11-20T15:07:27+01:00) · `deploy-app` runy **44748575840** (automaticky po pushi) a **44750600257** (po pipeline, overenie obrázkov) – oba OK.

### Hotové
- **Dátový model** (`docs/data-model.md`, miesto): `image_card`, `image_detail`, `image_detail_size`; `image_thumb` bez zmeny.
- **Pipeline** (`pipeline/thumbs.py` `generate_venue_images`, volané v `pipeline/main.py`): z jedného stiahnutia `image_url` miesta zapíše 160×160 náhľad, `img/venues/card/<id>.jpg` (640×480, `make_event_thumb`) a `img/venues/detail/<id>.jpg` (dlhšia strana ≤ 1200 px, nezväčšuje sa) + `image_detail_size` z JPEG súboru. Cache = hash súbor pri každom výstupe (pri nezmenenej URL sa nesťahuje). Jeden pokus, timeout 10 s ako doteraz; chyba = varovanie, polia `null`, beh pokračuje. Testy `tests/test_venue_images_082.py`.
- **Workflowy:** `deploy-app.yml` preberá z Pages `image_thumb`, `image_card` a `image_detail` miest (log runu 44750600257: „Venue thumbnails fetched: 33“ = 11 miest × 3). `daily.yml`: cache `site/img/venues` (s podpriečinkami) má kľúč aj z `pipeline/thumbs.py`.
- **Appka:** poradie v `web/src/core/eventImage.ts` (obrázok akcie → obrázok miesta → ikona typu; po `onError` ďalší kandidát). Napojené: riadok v Akciách a karta na mape (`EventImage43`, odznaky new/✦ ostávajú), stránka akcie (venue `image_detail` + rezervácia podľa venue `image_detail_size`, bez „Plagát“ a bez popisu), program miesta (`VenuePage`), Môj účet – Idem. Onboarding bez zmeny.
- **venues.json:** z `image_url` Akropolis odstránené `?utm_*` (obrázok ten istý).

### Rozhodnutia samostatne (zapísané v `docs/decisions.md`)
- Cache kľúč `daily.yml` doplnený o `thumbs.py` – inak by sa nové súbory pri nezmenenom `venues.json` neuložili do cache a sťahovali by sa každý deň.
- Môj účet (Idem): bez obrázka akcie aj miesta ostáva doterajší prázdny tmavý štvorec – ikona typu tam nikdy nebola, nevymýšľal som nové UI.
- Card/detail súbory miest bez `image_url` sa pri behu zmažú.

### Čísla (z publikovaného `events.json` po rune 44748943631)
Príkaz: `curl -s https://matejstolarik.github.io/eventapp/events.json -o site/events.json` a Python: akcie bez `image_thumb` po `venue_id`, z nich tie, ktorých miesto má `image_card`.
- Akcií **365**, bez obrázka (`image_thumb` null; zároveň všetky bez `image_url`) **40** → obrázok miesta dostane **40 / 40**.
- Po miestach (bez obrázka / spolu): bike-jesus **24/24**, citarna-unijazz **9/15**, roxy **7/44**; ostatné 0 (cross-club 13, meetfactory 34, kasarna-karlin 11, fuchs2 24, palac-akropolis 85, archa-plus 58, forum-karlin 23, epic 34).
- Miesta bez `image_card`: **žiadne** – všetkých 11 má `image_card` aj `image_detail`; nové obrázky Bike Jesus, Čitárna Unijazz, Akropolis aj Roxy (sdn.cz / firmy.cz) sa stiahli bez chyby.

### Overenie na webe
- Pages po deploy-app 44750600257: všetkých 33 súborov miest (`img/venues/*.jpg`, `card/*`, `detail/*`) vracia 200 (HEAD každého z `events.json`). `img/venues/card/bike-jesus.jpg` = 640×480, `img/venues/detail/bike-jesus.jpg` = 1200×798, `img/venues/detail/meetfactory.jpg` = 320×426 (nezväčšený).
- Bike Jesus: všetkých 24 akcií má v dátach `image_url: null` (napr. `bike-jesus-2026-11-21-gurriers-ie-support-enola-gay`); v appke majú teraz obrázok miesta.

### Testy
- `pytest -q`: **662 passed** (vrátane 4 nových).
- `npm test -- --reporter=dot`: **270 passed** (nový `eventImage.test.ts`: akcia bez obrázka + miesto s obrázkom → miesto; miesto bez obrázka → ikona; chyba → miesto → ikona; obrázok miesta bez „Plagát“).
- `npm run build`: OK.
- Playwright `tests/playwright/screenshots-082.spec.ts` (z `web/`, `NODE_PATH=web/node_modules`, dáta z Pages zúžené na Bike Jesus, čas 20. 11. 15:00): **2 passed**, s kontrolou, že riadky majú `img/venues/card/bike-jesus.jpg`, stránka akcie `img/venues/detail/bike-jesus.jpg` a nemá „Plagát“.

### Snímky a prehľad (`docs/tasks/082/`)
- `events-bike-jesus.jpg`, `event-page-venue-image.jpg` (stránka `bike-jesus-2026-11-21-gurriers-ie-support-enola-gay` – prvá budúca akcia bez obrázka v poradí `events.json`).
- `venue-images.jpg` – mriežka `image_card` všetkých miest s id, `image_detail_size` a typom súboru (skript `tests/venue_images_grid_082.py`). Pozn.: `image_detail_size` je strop 1200 px, takže 1200 = originál môže byť väčší.
  - **Menšie ako 640 px na šírku:** meetfactory **320×426** JPG, cross-club **535×277** JPG.
  - Ďalšie: kasarna-karlin 1200×917 JPEG (kreslená mapa), citarna-unijazz 1200×803 JPG, fuchs2 960×540 JPG, bike-jesus 1200×798 JPG, palac-akropolis 1200×978 JPG, **archa-plus 1200×1200 PNG (logo)**, forum-karlin 1200×630 JPG (facebook obrázok), roxy 1200×799 JPEG, epic 1200×802 JPEG.

### Otvorené
- Nič z úlohy. Výber náhrad obrázkov (napr. MeetFactory, Cross Club, logo Archa+) je na Matejovi.
