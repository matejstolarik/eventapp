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
