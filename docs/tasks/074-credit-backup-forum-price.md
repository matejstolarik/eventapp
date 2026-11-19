# 074: Upozornenie na nízky kredit DeepSeek, záloha prieskumu AI, chýbajúce ceny Forum Karlín

## Zadanie

**Schválené Matejom 2026-11-19** (doplnky k 057). **Záložný ranný beh sa nerobí** (Matej 11:16: „nechaj tak“ – plánované behy GitHub posúva o 8–9 h, dáta budú od ~14:00). Čo nie je jasné, spýtaj sa.

**Čítaj:** report 057; `pipeline/alerts.py`, `pipeline/run_summary.py`, `pipeline/classify_ai.py` (DeepSeek, `ProviderStop`), `.github/workflows/daily.yml` (kroky prieskumu `research/`, cache), `docs/decisions.md` (`grep -n -i "research\|záloh\|cache"`), `pipeline/adapters/html_forum_karlin.py`, `docs/venue-capacity.md` (riadok Kasárna).

### 1. Upozornenie na nízky kredit DeepSeek
- Po AI kroku zisti zostatok kreditu DeepSeek z ich API (endpoint zostatku; **over v oficiálnej dokumentácii DeepSeek**, ak taký endpoint nie je alebo sa správa inak, stop a napíš).
- Zostatok zapíš do denného zhrnutia (057) a do týždenného reportu (časť s výdavkami AI).
- **Upozornenie (issue `alert`) pri zostatku pod 0,20 $**, kľúč napr. `ai:low-credit`; zavrie sa po dobití (zostatok ≥ 0,20 $). Existujúce upozornenie pri HTTP 402 ostáva.
- Zlyhanie zistenia zostatku nesmie zastaviť beh (len varovanie v logu).

### 2. Týždenná záloha prieskumu AI do repa
- Prieskum (`research/`) je dnes na Pages a v `actions/cache` (065); obe sa už raz ukázali ako nespoľahlivé (065: 243 → 1). Pridaj **týždennú zálohu do repa** (napr. pri pondelkovom `weekly-report.yml` alebo v nedeľu v `daily.yml`): commit len ak sa obsah zmenil, správa `chore: research backup`.
- Ak denný beh načíta z Pages a cache menej záznamov ako je v zálohe v repe, použije zálohu z repa (a varuje). Nadväz na existujúcu logiku z 065, nepíš druhú.
- V zálohe len to, čo je dnes v `research/` (text a odkazy); **žiadne obrázky ani iné cudzie súbory**.

### 3. Forum Karlín: prečo chýba cena pri 96 % akcií
- Diagnostika na 5 akciách: čo je na stránke akcie a na stránke lístkov (cena v HTML, v JSON-LD, len cez JavaScript, u predajcu?), čo z toho adaptér číta.
- Ak sa cena dá vziať **tým istým spôsobom ako doteraz** (rovnaké stránky, bez prehliadača, bez nového predajcu), oprav adaptér a over na 5 akciách proti webu.
- Ak by to vyžadovalo **nový zdroj alebo spôsob sťahovania** (iný predajca lístkov, JavaScript, GoOut), **stop a napíš**, čo by bolo treba – podľa `CLAUDE.md` rozhoduje Matej.

### 4. Drobnosť
- `kasarna-karlin.notes` vo `venues.json`: doplň plnú adresu zdroja kapacity z `docs/venue-capacity.md`.

### 5. Pipeline
- Úloha mení dáta → **jeden beh na konci** (`CLAUDE.md`), raz počkaj.

## Overenie a report
- `pytest -q` (testy: upozornenie pod 0,20 $ otvorí a po dobití zavrie, zlyhanie zistenia zostatku nezastaví beh, záloha sa použije pri menšom počte záznamov), číslo behu.
- Report: zostatok DeepSeek z behu, počet záznamov v zálohe prieskumu, výsledok diagnostiky Forum Karlín (URL a hodnoty na 5 akciách), koľko cien Forum Karlín pribudlo, otvorené body.

## Report

**2026-11-19** · commit `40d9cb1` (práca), report v ďalšom commite. Beh pipeline: run 44506788022 (success, `generated_at` 2026-11-19T11:44:10+01:00).

### Hotovo
1. **Zostatok DeepSeek** – `deepseek.balance_usd()`: `GET https://api.deepseek.com/user/balance`, `total_balance` položky `USD`. Endpoint overený v oficiálnej dokumentácii (api-docs.deepseek.com/api/get-user-balance, cez vyhľadávanie – stránka bola z lokálnej siete nedostupná, reset spojenia). Volá sa po AI kroku v `main.py`; chyba/timeout/zlá odpoveď = `null` + varovanie, beh pokračuje. Zapisuje sa do zhrnutia (`ai.balance_usd`, `docs/data-model.md`) a do týždenného reportu (časť 7, „Zostatok DeepSeek: $x (dátum)“). Upozornenie `ai:low-credit` pri < 0,20 $; zavrie ho beh so zisteným zostatkom ≥ 0,20 $. `ai:limit` (HTTP 402) ostáva samostatné. Pravidlá v `docs/report-rules.md`.
2. **Záloha prieskumu** – `python -m pipeline.research_store backup` → `data/research_backup/<YYYY-MM>.json` (len záznamy prieskumu: text, dotazy, odkazy na zdroje; žiadne obrázky). Krok v `weekly-report.yml` (pondelok, po reporte, `if: always()`), obnoví cache `research-`, commit `chore: research backup` len pri zmene. `research_store.load` (logika 065) pridá zálohu, keď Pages + cache dali menej záznamov, a zaloguje varovanie. Prvá záloha vytvorená lokálne z Pages a commitnutá v `40d9cb1`.
3. **Forum Karlín – diagnostika** (nižšie). Adaptér sa **nemenil**: cena nie je na stránkach Forum Karlín, len u predajcov → nový zdroj, rozhoduje Matej.
4. **Kasárna** – `kasarna-karlin.notes` obsahuje plnú adresu PDF z `docs/venue-capacity.md`.

### Rozhodnutia (samostatne)
- Záloha v pondelňajšom `weekly-report.yml` (už existuje; denný beh by potreboval `contents: write`). Workflow má teraz `contents: write`.
- Záloha je po mesiacoch ako `site/research` (len `KEEP_MONTHS` = 3, staršie súbory sa zmažú) – súbor ~1,2 MB.
- Pri nezistenom zostatku sa `ai:low-credit` nezavrie (nevieme, či bolo dobité).
- `tests/conftest.py`: testy nikdy nečítajú zálohu v repe.
- Zápis do `docs/decisions.md` (3 riadky 2026-11-19).

### Čísla
Príkaz (po `curl -s https://matejstolarik.github.io/eventapp/events.json -o site/events.json`):
`python -c "import json;d=json.load(open('site/events.json',encoding='utf-8'));E=d['events'];F=[e for e in E if e['venue_id']=='forum-karlin'];print(d['generated_at'],len(E));print('forum-karlin',len(F),'with price',sum(1 for e in F if e.get('price_text')))"`
- 372 akcií; Forum Karlín 23, s cenou 1 → **pribudlo 0 cien** (adaptér bez zmeny).
- **Zostatok DeepSeek** z behu: **0,29 $** (log „DeepSeek balance: 0.29 USD“) – nad hranicou, upozornenie nevzniklo; ostáva len ~0,09 $ rezerva.
- **Záloha prieskumu**: 250 záznamov (`data/research_backup/2026-11.json`); beh načítal 250 záznamov, záloha sa nepoužila.
- `pytest -q`: 650 passed (lokálne aj v behu); nové testy `tests/test_074_credit_backup.py` (otvorenie pod 0,20 $ a zavretie po dobití, nezistený zostatok nechá issue otvorené, 402 a nízky kredit zvlášť, zlyhanie zistenia zostatku nevyhodí výnimku, záloha použitá pri menšom počte / nepoužitá pri úplnom, zápis zálohy).

### Diagnostika Forum Karlín (2026-11-19)
Stránka akcie: žiadna cena v texte, žiadny JSON-LD; `#sellers` má len odkazy na Ticketmaster a Ticketportal. Adaptér číta čas, dvere, prvý odkaz na lístky, popis, obrázok – ceny niet odkiaľ.

| Akcia | stránka akcie | cena tam | Ticketportal |
|---|---|---|---|
| STAHLZEIT 21. 11. | https://www.forumkarlin.cz/udalost/stahlzeit/ | nie | https://www.ticketportal.cz/event/STAHLZEIT – „CENA VSTUPENKY 1290 Kč“ len v texte popisu (tu je aj 1 cena v dátach, od AI) |
| SANDRA 6. 12. | https://www.forumkarlin.cz/udalost/sandra/ | nie | https://www.ticketportal.cz/nevent/SANDRA-50-let-na-scene – len cena balíčka Meet & Greet v texte (6 990 Kč) |
| Olympic 9. 12. | https://www.forumkarlin.cz/udalost/olympic/ | nie | https://www.ticketportal.cz/event/Olympic-Bombardak-tour-2026 – nie |
| Kodaline 5. 12. | https://www.forumkarlin.cz/udalost/kodaline/ | nie | https://www.ticketportal.cz/event/Kodaline – nie |
| MIKOLAS 4. 12. | https://www.forumkarlin.cz/udalost/mikolas-forum-karlin/ | nie | https://www.ticketportal.cz/event/MIKOLAS-FORUM-KARLIN – nie |

Ticketportal má na každej stránke rovnaké čísla zo šablóny (1500 / 2600 / 5200 / 7100 Kč – nie sú ceny akcie). Ticketmaster (napr. https://www.ticketmaster.cz/artist/stahlzeit-vstupenky/902104) má ceny len v JavaScriptovej aplikácii (JSON-LD bez ceny).
**Čo by bolo treba:** nový zdroj – Ticketportal (text popisu, len niekedy) alebo Ticketmaster (JavaScript / ich API) → rozhodne Matej. Dnes cenu dopĺňa len AI doplnenie.

### Otvorené
- Rozhodnutie Mateja o cene Forum Karlín (nový zdroj u predajcu, alebo nechať na AI).
- Krok zálohy v `weekly-report.yml` sa naživo spustí prvý raz v pondelok 23. 11. (neoverené v Actions, pokryté testami; prvá záloha je v repe).
- Upozornenie `ai:low-credit` neoverené naživo (zostatok 0,29 $ je nad hranicou); pri dnešnej spotrebe asi skoro príde.
