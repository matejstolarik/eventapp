# Pipeline status

Posledná aktualizácia: 2026-10-31

| Podnik | Typ zdroja | URL zdroja | Stav | Akcií / s časom (posledný beh) | Zvláštnosti webu | Otvorené problémy |
|--------|-----------|-----------|------|-------------------------------|-----------------|------------------|
| Cross Club | `rss` | https://www.crossclub.cz/cs/rss/program/ | ✅ hotovo | 13 / 0 | Detail stránky nemajú čas začiatku | `start_time` vždy null |
| MeetFactory | `jsonld` | /cs/program/hudba + /cs/program/divadlo | ✅ hotovo | 42 (31+11) / 0 | `doorTime` → `doors_time`; `start_time` vždy null; dve sekcie; stránkovanie `?page=N` | `start_time` vždy null (zámer) |
| Kasárna Karlín | `jsonld` | https://kasarnakarlin.cz/en/program | ✅ hotovo | 2 / 2 | TZ bug v JSON-LD → čas z textu stránky (riadok ~374); `/en/program` nie `/program` | — |
| Čítárna Unijazz | `jsonld/mec_ajax` + detail | https://citarna.unijazz.cz/program/ | ✅ hotovo | 19 / 19 | JS-render, AJAX listing + detail pre každú akciu (`.event-time`); skin ID 47 | — |
| Fuchs2 | `jsonld/wix_sitemap` | https://www.fuchs2.cz/event-pages-sitemap.xml | ✅ hotovo | 21 / 21 | Wix; sitemap 855 URL; okno rozšírené na 365 dní (178 URL, max_requests=200); čas overený (no TZ shift) | `ticket_url` null (JSON-LD nemá `offers`) |
| Bike Jesus | `api/strapi` | https://bikejesus.com/api/events | ✅ hotovo | 34 / 0 | Strapi v5 API; len dátum, bez času; pageSize=100 = všetko na 1 stranu | `start_time` vždy null |
| Archa+ | `html/archa` | https://archa-plus.cz/cz/program/ | ✅ hotovo | 64 / 64 | Pagination cez load-more JSON API; dátum z URL (ISO); GoOut widget → ticket_url null; free akcie z tagu „vstup zdarma" | Externé podniky (7 unikátnych v aktuálnom behu) sa nefiltrujú — listing nemá info o mieste |
| Forum Karlín | `html/forum_karlin` | https://www.forumkarlin.cz/program/ | ✅ hotovo | 29 / 29 | Dátum DD.MM.YYYY z listingu; čas + doors_time z detail (max 50 requestov); ticket_url z #sellers | — |
| ROXY | `html/roxy` | https://www.roxy.cz/club/ | ✅ hotovo | — | `data-hashtags` → formats; celý program na jednej stránke; `<time datetime>`, `h2.title` | — |
| EPIC Prague | `html/epic` | https://www.epicprague.com/program | ✅ hotovo | — | Bez hashtagov → všetky akcie do AI vrstvy 2; `time.program__item-datetime`, `h2.program__item-heading` | — |

## Poznámky pre PWA

- **Fuchs2 a Bike Jesus majú rovnaké súradnice** (`lat: 50.0952223, lng: 14.4363506`, ostrov Štvanice). Overené na OSM: oba podniky sú na rovnakom mieste. Na mape sa body prekryjú — PWA musí počítať s viacerými podnikmi na jednom bode (napr. clustrovanie alebo tooltip s viacerými podnikmi).

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

Workflow: `.github/workflows/daily.yml`. Spúšťa sa denne o **04:17 UTC** (05:17 CET / 06:17 CEST). Výstup (`site/events.json`) sa zverejní na GitHub Pages, do repa sa necommituje.

### Ako overiť, že ranný beh prebehol

1. **GitHub → repozitár → Actions → „Daily pipeline"** — posledný beh by mal mať čas ~04:17 UTC a v stĺpci „Event" hodnotu `schedule`.
2. V detaile behu → krok „Log run metadata" → v **job summary** aj v **logu** je riadok `Trigger: schedule, Started: YYYY-MM-DD 04:1x UTC`.
3. Ak je posledný beh starší ako 26 hodín a event nie je `schedule`, beh sa nevykonal.

**Po prvej zmene cron-u:** prvé plánované behy po zmene treba sledovať aspoň 3 dni (GitHub môže spustiť prvý beh s oneskorením do 24 hodín).

### Stav medzi behmi

Pipeline stiahne predošlý `events.json` zo zverejnenej adresy (`PREVIOUS_EVENTS_URL` env var → `https://matejstolarik.github.io/eventapp/events.json`). Na prvom behu vráti 404, pipeline začne bez stavu a zaloguje to.

### Zlyhanie workflow — e-mailové notifikácie

GitHub posiela e-mail vlastníkovi repozitára (Matejovi) pri každom zlyhaní plánovaného (`schedule`) behu. Toto je **zámerné správanie**: testy sú súčasťou pipeline a ich zlyhanie (napr. dátumovo-závislé testy) zablokuje publikovanie dát. Zlyhanie = pipeline nepublikovala — e-mail je správny poplach.

**Dôsledky pre CI behy:**
- Ak testy zlyhajú, `events.json` sa nezverejní (GitHub Actions zastaví pri zlyhaní kroku).
- Stará verzia `events.json` zostáva na GitHub Pages, kým beh neuspeje.
- Fix je commit s opravou + push → GitHub automaticky spustí nový beh pri ďalšom plánovanom čase alebo manuálne cez `workflow_dispatch`.

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

## robots.txt (overené 2026-11-02)

Pipeline kontroluje `robots.txt` pri každom behu (`urllib.robotparser`, výsledok cachovaný na beh). Aktuálny stav pre naše URL:

| Podnik | Host | URL (pipeline) | Povolené? | Crawl-delay |
|--------|------|----------------|-----------|-------------|
| Cross Club | crossclub.cz | `/cs/rss/program/` | ✅ áno | — |
| MeetFactory | meetfactory.cz | `/cs/program/hudba`, `/cs/program/divadlo` | ✅ áno | — |
| Kasárna Karlín | kasarnakarlin.cz | `/en/program` | ✅ áno | — |
| Čítárna Unijazz | citarna.unijazz.cz | `/wp-admin/admin-ajax.php`, `/program/` | ✅ áno | — |
| Palác Akropolis | palacakropolis.cz | `/work/33298`, `/pub/vstupne_6` | ✅ áno | — |

Žiadny zdroj nie je v `robots.txt` zakázaný. Ak sa to zmení, pipeline zaloguje varovanie a vyhodí `LimitExceeded` pre danú URL (adaptér túto akciu zachytí a pokračuje bez nej).

## Úlohy

Otvorené a dokončené úlohy sú v `docs/tasks/`. Historické úlohy (pred systémom súborov): `docs/tasks/000-history.md`.
