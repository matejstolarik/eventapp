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

### 3. Obrázok Bike Jesus
- Matej zmenil `image_url` Bike Jesus (`d1b37a3`) na `https://bikejesus.com/uploads/13_14f3d5fee0.jpg`. Ak treba, doplň `image_source` (stránka, kde obrázok je; ak ju nevieš zistiť, nechaj `https://bikejesus.com`).

## Overenie a report
- `pytest -q`, `npm test -- --reporter=dot` (náhrada: akcia bez obrázka + miesto s obrázkom → obrázok miesta; miesto bez obrázka → ikona; chyba načítania → miesto → ikona; „Plagát“ sa pri obrázku miesta neukáže), `npm run build`; **jeden beh pipeline** (číslo), nasadenie `deploy-app` (číslo). Over na Pages, že `img/venues/card/*` a `img/venues/detail/*` existujú aj po nasadení appky.
- Z publikovaného `events.json` (príkaz uveď): koľko akcií nemá obrázok (spolu a po miestach) a koľko z nich teraz dostane obrázok miesta; ktoré miesta nemajú `image_card` a prečo.
- **Prehľad obrázkov miest pre Mateja:** jedna mriežka JPEG `docs/tasks/082/venue-images.jpg` – každé miesto: `image_card` 640×480 zmenšený, pod ním id miesta, rozmery originálu (`image_detail_size`) a typ súboru (napr. logo PNG). Neposudzuj vhodnosť, len vypíš; Matej vyberie, čo vymeniť. Upozorni na originály menšie ako 640 px na šírku (napr. MeetFactory 320×426).
- Snímky JPEG 390 × 844 do `docs/tasks/082/`: `events-bike-jesus.jpg` (Akcie s akciami Bike Jesus – obrázok miesta v riadkoch), `event-page-venue-image.jpg` (stránka akcie Bike Jesus).
