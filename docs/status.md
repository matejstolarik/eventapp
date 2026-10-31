# Pipeline status

Posledná aktualizácia: 2026-10-31

| Podnik | Typ zdroja | URL zdroja | Stav | Akcií / s časom (posledný beh) | Zvláštnosti webu | Otvorené problémy |
|--------|-----------|-----------|------|-------------------------------|-----------------|------------------|
| Cross Club | `rss` | https://www.crossclub.cz/cs/rss/program/ | ✅ hotovo | 13 / 0 | Detail stránky nemajú čas začiatku | `start_time` vždy null |
| MeetFactory | `jsonld` | /cs/program/hudba + /cs/program/divadlo | ✅ hotovo | 42 (31+11) / 0 | `doorTime` → `doors_time`; `start_time` vždy null; dve sekcie; stránkovanie `?page=N` | `start_time` vždy null (zámer) |
| Kasárna Karlín | `jsonld` | https://kasarnakarlin.cz/en/program | ✅ hotovo | 2 / 2 | TZ bug v JSON-LD → čas z textu stránky (riadok ~374); `/en/program` nie `/program` | — |
| Čítárna Unijazz | `jsonld/mec_ajax` + detail | https://citarna.unijazz.cz/program/ | ✅ hotovo | 19 / 19 | JS-render, AJAX listing + detail pre každú akciu (`.event-time`); skin ID 47 | — |

## Čítárna Unijazz — technické detaily

### Ako stránka načítava dáta

- `/program/` je JS-renderovaná stránka. Statický HTML má len ~413 znakov (WordPress shell bez obsahu).
- MEC plugin (Modern Events Calendar, skin ID 47) načítava každý mesiac zvlášť cez `POST /wp-admin/admin-ajax.php`:
  - `action=mec_tile_load_month`, `mec_year=YYYY`, `mec_month=MM`, `atts[id]=47`
  - Odpoveď: JSON s kľúčom `month` obsahujúcim HTML so `<script type="application/ld+json">` blokmi
- Použitý prístup: `jsonld` adaptér, strategy `mec_ajax` — POST pre aktuálny + 2 nasledujúce mesiace (3 requesty) + GET na detail každej akcie pre čas (max 30 requestov celkom)

### Čo je k dispozícii

| Pole | Dostupné | Zdroj |
|------|----------|-------|
| Názov | ✅ | JSON-LD `name` |
| Dátum | ✅ (len dátum, bez času) | JSON-LD `startDate` |
| URL eventu | ✅ | JSON-LD `url` |
| Čas začiatku | ✅ | `.event-time` na detaile akcie (`DD. MM. YYYY HH:MM`) |
| Obrázok | ❌ | Prázdne v JSON-LD |
| Cena | ❌ | Prázdne v JSON-LD |

### Riziká

- **Skin ID**: ak site rebuild zmení skin ID (aktuálne 47), adaptér vráti 0 eventov — zachytí to varovanie v logu.

## Otvorené úlohy

| # | Úloha | Stav |
|---|-------|------|
| 1 | Kasárna čas: `_parse_time_line` limitovaná na 50 riadkov → odstrániť limit | ✅ hotovo |
| 2 | MeetFactory stránkovanie: `?page=N` + `a.endless_more` → `_fetch_listing_pages` | ✅ hotovo |
| 3 | Odstrániť `eventapp-repo.zip` z git histórie | ✅ hotovo |
| 4 | Aktualizovať počty v status.md | ✅ hotovo |
| 5 | Čitárna `start_time` z detailu akcie (`.event-time`); Cross Club — čas nie je k dispozícii | ✅ hotovo |
