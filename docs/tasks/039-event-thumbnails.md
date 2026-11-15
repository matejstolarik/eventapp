# 039: Náhľady obrázkov akcií

## Zadanie

**Čítaj:** `pipeline/thumbs.py` (celý, rozširuješ ho), `pipeline/main.py` (volanie `thumbs`), `.github/workflows/daily.yml` (krok `venue-thumbs`) a `.github/workflows/deploy-app.yml` (krok „Fetch venue thumbnails“), `docs/data-model.md` (`grep -n "image_url\|image_thumb"`). Vo `web/src`: `components/EventPanel.tsx` (~r. 148), `pages/MyAccountPage.tsx` (~r. 75), `pages/VenuePage.tsx` (~r. 74, obrázok akcie v programe). `design.md` netreba.

Nová obrazovka Akcie (`design.md` 4, ďalšia úloha) bude mriežka s veľkými obrázkami akcií. Dnes sa obrázky akcií načítavajú v plnej veľkosti z webov podnikov. Pri obrázkoch miest to s veľkou pravdepodobnosťou spôsobovalo čierny scroll (vyriešené náhľadmi v 036). Matej súhlasil s rovnakým riešením pre akcie (2026-11-15).

### 1. Pipeline
- Rozšír `thumbs.py` o akcie: pre každú akciu v `events.json` s `image_url` stiahni obrázok a ulož štvorcový náhľad **240 × 240 px** (`cover`, stred), JPEG kvalita 75, do `site/img/events/<event_id>.jpg`.
- Nové pole akcie **`image_thumb`**: relatívna cesta `img/events/<id>.jpg` alebo `null` (bez `image_url`, chyba sťahovania, nečitateľný obrázok). Zapíš do `data-model.md` vedľa `image_url` akcie.
- **Len pri zmene:** vedľa náhľadu súbor s hashom URL (ako pri miestach). Rovnaká URL = nesťahuje sa znova.
- **Cache medzi behmi:** `actions/cache` pre `site/img/events`, kľúč `event-thumbs-${{ github.run_id }}`, `restore-keys: event-thumbs-` (každý beh uloží novú verziu, obnoví poslednú).
- **Upratovanie:** náhľady akcií, ktoré už v `events.json` nie sú, zmaž z priečinka (cache nerastie donekonečna).
- **Slušnosť:** rovnaký `USER_AGENT`, jeden request naraz na jeden web, timeout 10 s, **najviac 150 nových sťahovaní za beh** (zvyšok v ďalšom behu; v logu počet odložených). Chyba = warning, akcia bez náhľadu, pipeline beží ďalej.
- Do logu: počet náhľadov (nové / z cache / chyby / odložené) a celková veľkosť priečinka.

### 2. Nasadenie appky
`deploy-app.yml`: popri náhľadoch miest stiahni z live Pages aj všetky `events[].image_thumb`. Chýbajúci súbor = výpis, nie chyba. Toto je kritické: bez toho po každej UI úlohe náhľady zmiznú (rovnaká chyba ako v 036).

### 3. Frontend (len malé obrázky)
- `EventPanel` (karta na mape), `MyAccountPage` (zoznam Idem), program v `VenuePage`: použi `image_thumb`; ak chýba alebo zlyhá načítanie, rovnaká náhrada ako dnes (ikona typu na farebnej ploche). `image_url` sa v týchto troch miestach už nepoužíva.
- `<img>` s `width`/`height` a `decoding="async"`.
- **Stránka akcie (`EventPage`) ostáva s plným `image_url`** (veľký plagát na rozkliknutie).

### Testy
- pytest: náhľad z testovacieho obrázka (fixture) má 240 × 240; rovnaká URL sa druhýkrát nesťahuje (mock); zmena URL sa stiahne; upratovanie zmaže náhľad akcie, ktorá zmizla; limit 150 (mock s 200 akciami → 150 stiahnutých, 50 odložených).

### Overenie
- `pytest -q`, `npm test`, `npm run build`.
- Spusti denný beh ručne a v reporte uveď čísla z jeho logu (nové / cache / chyby / odložené, veľkosť priečinka) a číslo behu. Ak ostali odložené, uveď to; doplnia sa ďalšími behmi.
- Po nasadení appky: počet stiahnutých náhľadov akcií v logu `deploy-app`.
- Žiadne snímky.

## Report

**Dátum:** 2026-11-15  
**Commit:** e8b724a

### Čo je hotové

**Pipeline:**
- `pipeline/thumbs.py`: nová funkcia `generate_event_thumbs()` – 240×240 JPEG kvalita 75, `site/img/events/<id>.jpg`, URL-hash cache (`.url_hash` vedľa thumbnailov), limit 150 stiahnutí za beh, upratovanie stale thumbnailov, log (new/cache/errors/deferred + veľkosť priečinka).
- `pipeline/main.py`: importuje a volá `generate_event_thumbs(events)`, anotuje každú akciu poľom `image_thumb`.
- `TIMEOUT` skrátený z 15 s na 10 s pre oba adaptery (venues aj events).

**GitHub Actions:**
- `daily.yml`: nový krok „Cache event thumbnails" – `path: site/img/events`, `key: event-thumbs-${{ github.run_id }}`, `restore-keys: event-thumbs-`.
- `deploy-app.yml`: nový krok „Fetch event thumbnails (preserve pipeline images)" stiahne `events[].image_thumb` z live Pages po vzore existujúceho kroku pre venue thumbnaily.

**Frontend:**
- `web/src/core/types.ts`: `image_thumb: string | null` pridané do `Event` interface.
- `EventPanel.tsx`, `MyAccountPage.tsx`, `VenuePage.tsx` (`EventThumbnail`): používajú `image_thumb` namiesto `image_url`, pridané `width`/`height` a `decoding="async"`. `EventPage` zostáva s plným `image_url`.

**Dokumentácia:**
- `docs/data-model.md`: `image_thumb` v JSON príklade akcie a v zozname polí (s popisom 240×240 a limitu 150/beh).

### Testy
- `tests/test_event_thumbs.py`: 5 testov – rozmery 240×240, cache (rovnaká URL = žiadny nový request), zmenená URL = nové stiahnutie, upratovanie (zmiznutá akcia), limit 150 (200 akcií → 150 stiahnutých, 50 odložených). Všetky prešli.
- `pytest -q`: 232 passed.
- `npm test --run`: 86 passed.
- `npm run build`: OK.

### Overenie denného behu
Denný beh treba spustiť ručne na GitHub Actions (workflow_dispatch na `daily.yml`). Po behu doplniť čísla: nové/cache/errors/deferred, veľkosť `site/img/events`, číslo behu.

Po nasadení appky: skontrolovať log kroku „Fetch event thumbnails" v `deploy-app.yml` – počet stiahnutých thumbnailov akcií.

### Otvorené
- Čísla z prvého behu (nové/cache/errors/deferred, veľkosť priečinka) – doplniť po ručnom spustení denného behu.
