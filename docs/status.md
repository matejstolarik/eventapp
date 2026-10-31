# Pipeline status

Posledná aktualizácia: 2026-10-31

| Podnik | Typ zdroja | URL zdroja | Stav | Akcií (posledný beh) | Zvláštnosti webu | Otvorené problémy |
|--------|-----------|-----------|------|---------------------|-----------------|------------------|
| Cross Club | `rss` | https://www.crossclub.cz/cs/rss/program/ | ✅ hotovo | 14 | — | — |
| MeetFactory | `jsonld` | /cs/program/hudba + /cs/program/divadlo | ✅ hotovo | ~47 (paginated) | `doorTime` → `doors_time`; `start_time` vždy null; dve sekcie; stránkovanie cez `?page=N` + `a.endless_more` | — |
| Kasárna Karlín | `jsonld` | https://kasarnakarlin.cz/en/program | ✅ hotovo | 2 | Čas v JSON-LD je posunutý o 5–6 h (TZ bug servera) → parsujeme z textu stránky; čas je na riadku ~374 surového textu (nie v prvých 50); dátumy v HTML sú MM. DD. (nie DD. MM.) — ignorujeme; statické HTML `/program` má CS linky s `/index.php/` → používame `/en/program` | — |
| Čítárna Unijazz | `jsonld/mec_ajax` | https://citarna.unijazz.cz/program/ | ✅ hotovo | 19 | Stránka je JS-renderovaná (statický HTML 413 znakov). Mesiace sa načítavajú cez `POST /wp-admin/admin-ajax.php` s parametrami `mec_tile_load_month` + skin ID. JSON-LD v odpovedi: len dátum (bez času), title, URL eventu. **Riziko: pri zmene skin ID (aktuálne 47) adaptér vráti 0 eventov** — zachytí to varovanie o nulovom počte. | Čas začiatku nie je dostupný v listingu (`start_time = null`) |

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

## Otvorené úlohy

| # | Úloha | Stav |
|---|-------|------|
| 1 | Kasárna čas: `_parse_time_line` limitovaná na 50 riadkov; reálne stránky majú čas na riadku ~374 → odstrániť limit | ✅ hotovo |
| 2 | MeetFactory stránkovanie: obe sekcie majú `endless_more` link; hudba má 4 strany, divadlo 2 → implementovať `_fetch_listing_pages` | ✅ hotovo |
| 3 | Odstrániť `eventapp-repo.zip` z git histórie (omylom commitnutý) | ✅ hotovo |
| 4 | Aktualizovať počty v status.md (Cross 14, MeetFactory ~47, Kasárna 2, Čitárna 19) | ✅ hotovo |
| 5 | Testy, pipeline beh, commit, push | 🔄 prebieha |
