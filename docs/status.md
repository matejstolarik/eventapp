# Pipeline status

Posledná aktualizácia: 2026-10-31

| Podnik | Typ zdroja | URL zdroja | Stav | Akcií (posledný beh) | Zvláštnosti webu | Otvorené problémy |
|--------|-----------|-----------|------|---------------------|-----------------|------------------|
| Cross Club | `rss` | https://www.crossclub.cz/cs/rss/program/ | ✅ hotovo | 14 | — | — |
| MeetFactory | `jsonld` | /cs/program/hudba + /cs/program/divadlo | ✅ hotovo | 20 (10+10) | `doorTime` → `doors_time`; `start_time` vždy null; dve sekcie | — |
| Kasárna Karlín | `jsonld` | https://kasarnakarlin.cz/en/program | ✅ hotovo | 2 | Čas v JSON-LD je posunutý o 5–6 h (TZ bug servera) → parsujeme z textu stránky; dátumy v HTML sú MM. DD. (nie DD. MM.) — ignorujeme; statické HTML `/program` má CS linky s `/index.php/` → používame `/en/program` | — |
| Čítárna Unijazz | `jsonld/mec_ajax` | https://citarna.unijazz.cz/program/ | ✅ hotovo | TBD | Stránka je JS-renderovaná (statický HTML 413 znakov). Mesiace sa načítavajú cez `POST /wp-admin/admin-ajax.php` s parametrami `mec_tile_load_month` + skin ID. JSON-LD v odpovedi: len dátum (bez času), title, URL eventu. **Riziko: pri zmene skin ID (aktuálne 47) adaptér vráti 0 eventov** — zachytí to varovanie o nulovom počte. | Čas začiatku nie je dostupný v listingu (`start_time = null`) |

## Čítárna Unijazz — technické detaily

### Ako stránka načítava dáta

- `/program/` je JS-renderovaná stránka. Statický HTML má len ~413 znakov (WordPress shell bez obsahu).
- MEC plugin (Modern Events Calendar, skin ID 47) načítava každý mesiac zvlášť cez `POST /wp-admin/admin-ajax.php`:
  - `action=mec_tile_load_month`, `mec_year=YYYY`, `mec_month=MM`, `atts[id]=47`
  - Odpoveď: JSON s kľúčom `month` obsahujúcim HTML so `<script type="application/ld+json">` blokmi
- Použitý prístup: `jsonld` adaptér, strategy `mec_ajax` — POST pre aktuálny + 2 nasledujúce mesiace (3 requesty/beh)

### Čo je k dispozícii

| Pole | Dostupné | Zdroj |
|------|----------|-------|
| Názov | ✅ | JSON-LD `name` |
| Dátum | ✅ (len dátum, bez času) | JSON-LD `startDate` |
| URL eventu | ✅ | JSON-LD `url` |
| Čas začiatku | ❌ | Nie je v listingu — len na individuálnych stránkach (`.event-time`) |
| Obrázok | ❌ | Prázdne v JSON-LD |
| Cena | ❌ | Prázdne v JSON-LD |

### Riziká

- **Skin ID**: ak site rebuild zmení skin ID (aktuálne 47), adaptér vráti 0 eventov — zachytí to varovanie v logu.
