# 062: DeepSeek v dennom behu, poistky žánrov, prepočítanie

## Zadanie

> **ZMENA 2026-11-17 (Matej, pred spustením):** v časti 3 sa **nezastavuje** (ani pri typ pod 46/50, ani pri veľa zahodených žánroch). Meranie urob a výsledky daj do reportu, potom pokračuj časťou 4. Iný poskytovateľ nie je, chyby sa riešia po nasadení. Pravidlo kreditu v časti 4 (pri nízkom zostatku len 30 dní) platí.

**Schválené Matejom 2026-11-17** po reporte 061: AI doplnenie a AI zaradenie v dennom behu = **DeepSeek variant A** (`pipeline/deepseek.py`). Nahrádza pôvodné časti 1, 2, 5 úlohy 060 (Gemini D). Gemini s hľadaním sa nepoužíva (060 poistka ostáva).

**Čítaj:** `docs/ai-rules.md` (celé, zmenené B7 a F 2026-11-17); report 061 (Časť 2, tabuľka, Zahodené poistkami, Otvorené); zadanie 060 časť 2 (poistky – žánre a cena bez opory, nesplnené); `pipeline/deepseek.py`, `pipeline/enrich_ai.py` (`process_result`, `description_problems`), `pipeline/classify_ai.py`, `pipeline/research_store.py`, `.github/workflows/daily.yml`; `docs/decisions.md` (`grep -n "061\|060"`).

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`.

### 1. Poistky v kóde (pred zapnutím)
- **Žánre (`ai-rules.md` C2, C3):** každý žáner musí mať v prieskume fakt (citát), v ktorom je názov žánru alebo jeho schválené synonymum / pravopisný variant (`genre_aliases`). Inak sa zahodí (`dropped`). Nadradený žáner bez vlastnej opory (`electronic` k `edm`, `metal` k `metalcore`, `pop`, `indie` …) sa zahodí. Testy na prípadoch z 061: Warhaus `indie`, Student Wednesday `electronic`, SLVL `hardcore` (fakt „hard techno“), Allt `death-metal` (fakt „death-core“), Keo `indie` (fakt „alt-rock“) → zahodené; Amphibian `ambient` z „atmosférické poslouchání“ → zahodené. Pri synonymách si daj pozor, aby `hard techno` neprešlo ako `hardcore`.
- **Cena bez opory** (060 časť 2, ak ešte nie je): vo faktoch ani na stránke podniku nie je suma ani „zdarma/dobrovoľné“ → prázdna; „Tba“ a podobné → prázdne. Ak už platí, len to napíš.
- **Výkričník:** `description_problems` nesmie zahodiť popis, keď je „!“ súčasťou názvu akcie alebo mena interpreta (FIRE!). Test.
- **Popis:** prompt podľa nového `ai-rules.md` F (približne 5 viet podľa interpreta; bez ceny, času, miesta, sály a organizátora). V kóde: popis, ktorý obsahuje názov podniku alebo sály, ide na kontrolu (`needs_review`), nezahadzuje sa.
- **Preklad:** prompt prekladu výslovne: nemeniť fakty, rod, čísla, mená. Test na Amphibian (A Strange Wedding: rod podľa CZ).
- **Typ:** prompt podľa nového B7 (Tinlicker = `concert`, `dj` doplnkový).

### 2. Zapnutie v dennom behu
- `ENRICH_PROVIDER: deepseek` v `daily.yml` pre AI doplnenie **aj** AI zaradenie (`classify_ai`) – denný beh nesmie potrebovať Claude ani Gemini. Claude provider ostáva v kóde ako záloha jednou premennou.
- Kľúč len z `secrets.DEEPSEEK_API_KEY`. Pri HTTP 401/402 alebo výpadku API: AI sa zastaví, beh dobehne bez nej, **cache a doterajšie AI hodnoty (vrátane žánrov z `classify_ai`) sa nestratia** (test; 060 Otvorené: lokálne bez kľúča 208 → 152 žánrov).
- Rozpočet v kóde: **0,30 $ za beh**, **3 $ za kalendárny mesiac** (súčet z uložených záznamov o cene); po prekročení AI stop, beh pokračuje. Limity 3 hľadania + 2 načítania na akciu ostávajú.
- Prieskum ukladať cez `research_store.py` (krok rozhodnutia sa dá zopakovať bez hľadania; vstup `reenrich_from_research` do workflow, ak ešte nie je).
- Denný beh ostáva mimo špičky DeepSeek (04:17 UTC je mimo; napíš, ak by sa to v lete zmenilo).

### 3. Meranie na 50 akciách (pred prepočítaním)
- Tie isté akcie ako 061, s poistkami z časti 1 (rozhodnutie z uloženého prieskumu 061, kde sa dá, bez nového hľadania).
- Súhrn v reporte: typ X/50, nepodložené žánre (porovnaj s 13 v 061), zahodené poistkami (zoznam), počet popisov na kontrolu kvôli miestu, cena. **Ak typ klesne pod 46/50 alebo poistky zahodia viac ako polovicu žánrov, zastav pred časťou 4 a napíš to.**

### 4. Prepočítanie 60 dní
- Všetky akcie v najbližších 60 dňoch cez DeepSeek (ignorovať AI cache, údaje zo stránok podnikov majú prednosť ako doteraz). Odhad ~245 akcií × ~0,0051 $ ≈ 1,25 $. **Kredit DeepSeek je ~1,76 $** – pred spustením over zostatok (ako v 061); ak by po prepočítaní ostalo menej ako 0,40 $, prepočítaj len najbližších 30 dní, zvyšok nechaj dennému behu a napíš to. Rozpočet behu pre prepočítanie 1,40 $.
- `docs/tasks/062/genres-review.md`: všetky mapovania žánrov a kandidáti (`genre_candidates`) po prepočítaní, na schválenie Matejom (pôvodne 058 časť 3 / 060 časť 5).

### 5. Výsledky testov Gemini s hľadaním z repa preč (Matej 2026-11-17)
- `git rm` (normálny commit, **bez prepisu histórie**): `docs/tasks/058/gemini-test.xlsx`, `058/gemini_test.json`, `059/gemini-tuning.xlsx`, `059/tune.json`, `059/tune_a10.json`; `058/verdicts.json` a `059/verdicts.json`, ak obsahujú výstupy Gemini (inak ponechať a napísať).
- V `docs/tasks/061/deepseek-test.json` a `.xlsx` odstrániť stĺpce Gemini D (pregenerovať bez nich). Súhrnné čísla D v textoch reportov ostávajú.
- Kód `_Gemini2` a `gemini_test.py` ostávajú (Gemini bez hľadania je povolený).
- Drobnosť: `docs/data-model.md` `image_url` – odstrániť náhradu z GoOut (rozhodnutie 2026-11-17 po 060: obrázky z GoOut nie).

## Overenie a report
- `pytest -q` OK; CI beh denného workflow (číslo) po zapnutí.
- Čísla z `events.json` posledného behu (príkaz): akcie, s typom od AI, so žánrami, s cenou (od AI overené / neoverené), s časom, s popisom, na kontrolu; zahodené poistkami podľa druhu; cena behu a mesiaca v $; zostatok kreditu.
- Ručne over 5 akcií na webe (URL + čo tam je), aspoň 2 z nich s cenou od AI.
- Otvorené body.
