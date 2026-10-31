# Pipeline status

Posledná aktualizácia: 2026-10-31

| Podnik | Typ zdroja | URL zdroja | Stav | Akcií (posledný beh) | Zvláštnosti webu | Otvorené problémy |
|--------|-----------|-----------|------|---------------------|-----------------|------------------|
| Cross Club | `rss` | https://www.crossclub.cz/cs/rss/program/ | ✅ hotovo | 14 | — | — |
| MeetFactory | `jsonld` | /cs/program/hudba + /cs/program/divadlo | ✅ hotovo | 20 (10+10) | `doorTime` → `doors_time`; `start_time` vždy null; dve sekcie | — |
| Kasárna Karlín | `jsonld` | https://kasarnakarlin.cz/en/program | ✅ hotovo | 2 | Čas v JSON-LD je posunutý o 5–6 h (TZ bug servera) → parsujeme z textu stránky; dátumy v HTML sú MM. DD. (nie DD. MM.) — ignorujeme; statické HTML `/program` má CS linky s `/index.php/` → používame `/en/program` | — |
| Čítárna Unijazz | — | https://citarna.unijazz.cz/program/ | 🔍 preskúmané, čaká na rozhodnutie | 0 | Program sa načítava cez JS (MEC plugin skin #47); statický HTML má len 413 znakov; JSON-LD eventy sú embednuté v skrytých div-och per mesiac; čas nie je v JSON-LD ani v listingu | Zdroj preskúmaný, prístup neschválený — pozri nižšie |

## Čítárna Unijazz — zistenia a návrhy

### Ako stránka načítava dáta

1. **Aktuálny mesiac + nasledujúci mesiac** sú server-side renderované priamo do HTML stránky `/program/` ako skryté `<div id="mec_tile_month_47_YYYYMM">` kontajnery.
   - Každý event má `<script type="application/ld+json">` priamo v kontajneri.
   - JSON-LD obsahuje: `name`, `startDate` (len dátum, napr. `"2026-11-03"`), `url` (stránka eventu).
   - **Čas v JSON-LD nie je** — `startDate` je date-only.

2. **Ďalšie mesiace** sa načítavajú cez `POST /wp-admin/admin-ajax.php` s akciou `mec_tile_load_month`:
   - Povinné parametre: `action=mec_tile_load_month`, `mec_year=YYYY`, `mec_month=MM`, `atts[id]=47`
   - Odpoveď: JSON s kľúčom `month` obsahujúcim HTML (ten istý formát ako v stránke, vrátane JSON-LD scriptov keď sú eventy)
   - Skin ID (47) sa číta z DOM elementu `id="mec_skin_47"` — robustne parsovateľné zo stránky

3. **WP REST API** (`/wp-json/wp/v2/mec-events`) existuje, ale `date` pole je dátum *publikácie*, nie konania eventu — nevhodné.

### Čo je k dispozícii v listingu

| Pole | Dostupné | Zdroj |
|------|----------|-------|
| Názov | ✅ | JSON-LD `name` |
| Dátum | ✅ (len dátum, bez času) | JSON-LD `startDate` |
| URL eventu | ✅ | JSON-LD `url` / `offers.url` |
| Čas začiatku | ❌ | Nie je v listingu |
| Obrázok | ❌ | Prázdne v JSON-LD |
| Cena | ❌ | Prázdne v JSON-LD |

Čas je dostupný len na individuálnych stránkach eventov (element `.event-time`).

### Navrhované prístupy

#### Možnosť A — JSON-LD z listingu + AJAX pre ďalšie mesiace (odporúčané)
- **Postup**: 1× GET `/program/` → parse JSON-LD zo všetkých načítaných mesiacov; POST `admin-ajax.php` pre každý mesiac v okne, ktorý ešte nie je načítaný
- **Počet requestov za beh**: ~6 (1 GET + ~5 POST pre mesiace nov–apr)
- **Výhoda**: pokrytie celého 180-dňového okna; čisté JSON-LD dáta; žiadne individuálne stránky eventov
- **Nevýhoda**: `start_time = null` (čas v listingu nie je); POST telo citlivé na skin ID; pri rebuild webu treba update
- **Typ adaptéra**: nový `jsonld` prístup s `follow_months: true` alebo nový `html` strategy

#### Možnosť B — len listing stránka (najjednoduchšie)
- **Postup**: 1× GET `/program/` → parse JSON-LD z pre-loadnutých mesiacov (zvyčajne aktuálny + nasledujúci)
- **Počet requestov za beh**: 1
- **Výhoda**: extrémne jednoduché; 0 AJAX závislostí
- **Nevýhoda**: pokrytie len ~1–2 mesiacov dopredu; `start_time = null`
- **Poznámka**: Čítárna plánuje eventy typicky 1–2 mesiace dopredu, takže praktické pokrytie môže byť dostatočné

#### Možnosť C — listing + individuálne stránky pre čas
- **Postup**: Možnosť A + pre každý event GET individuálnej stránky → parsovať `.event-time`
- **Počet requestov za beh**: 6 + N eventov (≈6 + 20 = ~26)
- **Výhoda**: dostaneme čas; kompletné dáta
- **Nevýhoda**: 26 requestov za beh; pomalé; individuálne stránky sa môžu zmeniť

**Odporúčanie**: Možnosť B na začiatok (1 request, jednoduché); ak bude pokrytie nedostatočné, prejsť na A.
