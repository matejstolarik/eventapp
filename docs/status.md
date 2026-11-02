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

## GitHub Actions — denný beh

Workflow: `.github/workflows/daily.yml`. Spúšťa sa denne o 05:00 UTC (06:00 CET / 07:00 CEST). Výstup (`site/events.json`) sa zverejní na GitHub Pages, do repa sa necommituje.

### Stav medzi behmi

Pipeline stiahne predošlý `events.json` zo zverejnenej adresy (`PREVIOUS_EVENTS_URL` env var → `https://matejstolarik.github.io/eventapp/events.json`). Na prvom behu vráti 404, pipeline začne bez stavu a zaloguje to.

### Automatické vypnutie plánovaného workflow

Zdroj: [GitHub Docs — schedule event](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule)

> "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days."

**Platí teda:** ak sa 60 dní nič nepushne do repa (žiadny commit, PR ani iná aktivita), GitHub automaticky vypne plánované spúšťanie tohto workflow.

**Ako znovu zapnúť:** GitHub → repozitár → Actions → výber workflow „Daily pipeline" → Enable workflow.

**Odporúčanie:** Aby k tomu nedochádzalo, pri dlhšej nečinnosti spustiť workflow ručne cez `workflow_dispatch` alebo aspoň pushnúť malý commit (napr. update `docs/status.md`).

### GitHub Pages — nastavenia

Po nasadení workflow je potrebné v nastaveniach repa prepnúť zdroj Pages na „GitHub Actions":
1. GitHub → repozitár → Settings → Pages
2. Pod „Build and deployment" → Source → vybrať **GitHub Actions**
3. Uložiť

## Úlohy

Otvorené a dokončené úlohy sú v `docs/tasks/`. Historické úlohy (pred systémom súborov): `docs/tasks/000-history.md`.
