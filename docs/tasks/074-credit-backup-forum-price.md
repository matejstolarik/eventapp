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
