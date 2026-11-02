# 004: Denný beh pipeline (GitHub Actions) a zverejnenie na GitHub Pages

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02. Začni až po dokončení úloh 002 a 003.

Cieľ: pipeline beží každý deň sama a `events.json` je na verejnej adrese pre PWA. Od prvého behu sa zbiera história (týždeň prevádzky).

1. Workflow `.github/workflows/daily.yml`:
   - spúšťanie: denne ráno (cron v UTC, cieľ okolo 06:00 pražského času) + ručne (`workflow_dispatch`)
   - checkout, Python, `pip install -r requirements.txt`, `python -m pipeline.main`, testy pred behom (ak testy padnú, nezverejňuj)
   - dev cache v CI vypnutá
2. **Denný beh nič necommituje do repa.** Výstup sa zverejní len na GitHub Pages (`actions/upload-pages-artifact` + `actions/deploy-pages`). Dôvod: commity „denná aktualizácia“ by sa zrážali s lokálnou prácou a zahltili históriu.
3. Stav medzi behmi: predošlý `events.json` (pre `first_seen`, `last_seen`, `gone`) si beh stiahne zo zverejnenej adresy na Pages. Ak tam nie je (prvý beh, 404), začne bez stavu a zaloguje to. Riešenie navrhni sám, adresa nesmie byť natvrdo len v kóde (konfigurácia alebo premenná prostredia).
4. `site/events.json` prestaň commitovať (`.gitignore` + `git rm --cached`, bežný commit, žiadny prepis histórie). Lokálny beh ho naďalej vytvára.
5. Súhrn behu do GitHub job summary: počet akcií podľa podniku, varovania (zdroj s 0 akciami, minutý `max_requests`, timeout), príznaky kvality. Zlyhanie jedného zdroja nesmie zastaviť ostatné (už platí), ale musí byť v súhrne viditeľné.
6. GitHub Pages treba v nastaveniach repa prepnúť na zdroj „GitHub Actions“. Ak to nevieš spraviť sám, napíš do reportu presný postup pre Mateja (kde kliknúť) a zastav sa pred overením.
7. Poznámka do `docs/status.md`: GitHub vypína plánované workflow vo verejnom repe po 60 dňoch bez aktivity v repe. Over túto informáciu v dokumentácii GitHubu a zapíš, čo platí.
8. Do `docs/project.md` (Poradie práce) a `docs/decisions.md`: denný beh + Pages zaradené pred test LLM (rozhodnutie 2026-11-02, dôvod: história prevádzky od začiatku, PWA potrebuje verejnú adresu dát).

Do reportu: URL zverejneného `events.json`, výsledok ručne spusteného behu (odkaz na beh v Actions, počty podľa podniku zo zverejneného súboru), ako sa rieši stav medzi behmi.

## Report

Dátum: 2026-11-02. Commit: po pushi (doplniť).

### Čo je hotové

**1. Workflow `.github/workflows/daily.yml`** — vytvorený. Spúšťanie: denne o 05:00 UTC + `workflow_dispatch`. Kroky: checkout → Python 3.12 → pip install → pytest (ak padnú, job zastaví a nič sa nezverejní) → `python -m pipeline.main` → `configure-pages` → `upload-pages-artifact` (adresár `site/`) → `deploy-pages`. Dev cache (`EVENTAPP_DEV_CACHE`) sa v CI nenastavuje → cache je prirodzene vypnutá.

**2. Denný beh nič necommituje** — výstup ide len na GitHub Pages. `site/events.json` odstránený z git trackingu (`git rm --cached`) a pridaný do `.gitignore`.

**3. Stav medzi behmi** — `pipeline/main.py` rozšírený: `load_previous_events()` najprv skúsi URL z env premennej `PREVIOUS_EVENTS_URL`. V workflow nastavené na `https://matejstolarik.github.io/eventapp/events.json`. Na prvom behu (404) zaloguje a pokračuje bez stavu. Lokálne (bez env var) funguje rovnako ako predtým — načíta `site/events.json` ak existuje.

**4. GitHub job summary** — `pipeline/main.py` píše do `$GITHUB_STEP_SUMMARY` (ak je nastavená): počet akcií podľa podniku, varovania (0 eventov zo zdroja, chyba zdroja), quality flags. V lokálnom behu (bez env var) sa summary nevygeneruje.

**5. GitHub Pages nastavenia** — `gh` CLI nie je k dispozícii v tomto prostredí. Postup pre Mateja:
1. GitHub → repozitár `matejstolarik/eventapp` → **Settings** → **Pages**
2. Pod „Build and deployment" → Source → vybrať **GitHub Actions**
3. Uložiť

Bez tohto kroku prvý beh workflow zlyhá pri `deploy-pages`.

**6. Pozn. v `docs/status.md`** — pridaná sekcia „GitHub Actions — denný beh" s odkazom na GitHub Docs a presnou citáciou pravidla 60 dní. Zdroj: [GitHub Docs — schedule event](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule): *"In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days."*

**7. `docs/decisions.md`** — pridané 3 nové riadky (2026-11-02): denný beh pred LLM testom, no-commit politika, stav medzi behmi.

### URL zverejneného events.json

`https://matejstolarik.github.io/eventapp/events.json`

(Dostupné po prvom úspešnom behu workflow a po prepnutí Pages na GitHub Actions source.)

### Výsledok ručne spusteného behu

Workflow ešte nebežal (Pages nie sú prepnuté na GitHub Actions source). Matej musí najprv prepnúť Pages zdroj (postup vyššie), potom spustiť workflow ručne cez Actions → Daily pipeline → Run workflow. Odkaz na výsledok behu doplniť po prvom behu.

### Ako sa rieši stav medzi behmi

CI pipeline stiahne predošlý `events.json` zo `PREVIOUS_EVENTS_URL` (env var v workflow). Ak vrátí 404 alebo iná chyba, pipeline začne bez stavu — `first_seen` všetkých eventov bude dátum tohto behu. Na ďalší deň si beh stiahne včerajší výstup a stav sa postupne buduje.

### Čísla (lokálny beh po implementácii, 2026-11-02)

Príkaz: `python -m pipeline.main` (lokálny beh bez PREVIOUS_EVENTS_URL, site/events.json generovaný 2026-11-02T21:05)

| Podnik | Počet eventov |
|---|---|
| citarna-unijazz | 17 |
| cross-club | 15 |
| kasarna-karlin | 2 |
| meetfactory | 42 |
| palac-akropolis | 83 |
| **Celkom** | **159** |

### Otvorené

- GitHub Pages treba manuálne prepnúť na „GitHub Actions" source (Matej, postup vyššie). Bez toho `deploy-pages` step zlyhá.
- Prvý CI beh začne bez histórie (404 na Pages URL) — `first_seen` všetkých eventov bude dátum prvého behu.
- Job summary zachytáva len varovania viditeľné z `main.py` (0 eventov, chyba zdroja). Varovania z adaptérov (minutý `max_requests`, timeout) sú v CI logu, nie v summary — doladenie v budúcej úlohe.
- Workflow sa automaticky vypne po 60 dňoch bez aktivity v repe. Ak Matej dlho nič nepushne, treba ho ručne znovu zapnúť (Actions → Daily pipeline → Enable).
