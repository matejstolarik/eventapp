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
