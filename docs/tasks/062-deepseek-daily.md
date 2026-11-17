# 062: DeepSeek v dennom behu, poistky žánrov, prepočítanie

## Zadanie

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


## Report

**Dátum:** 2026-11-17. **Stav: hotové (časti 1–5).** Denný beh odteraz používa DeepSeek pre AI zaradenie aj AI doplnenie.

**Commity:**
- `4a15cf9` – časť 1 (poistky, prompty);
- `8f39b54` – časť 2 (DeepSeek v dennom behu, rozpočet, cache);
- `1574d97` – časť 5 (súbory Gemini preč);
- `2b4bc14` – nástroj merania (`redecide`);
- `1e1a1da` – časť 3 (meranie + oprava poistok);
- `d1bc4ec` – časť 4 (`genres-review.md`, log zahodených);
- report je v commite s týmto textom.

**Behy workflow:**
- meranie 50 akcií (`deepseek-test.yml`, mode `redecide`): [44155163300](https://github.com/matejstolarik/eventapp/actions/runs/44155163300);
- prepočítanie 60 dní (`daily.yml`, `reenrich_days=60`, `ai_budget_usd=1.30`): [44156896473](https://github.com/matejstolarik/eventapp/actions/runs/44156896473), úspešný, aj testy v CI prešli;
- zostatok po prepočítaní (mode `balance`): [44162002641](https://github.com/matejstolarik/eventapp/actions/runs/44162002641).

`pytest -q`: **388 passed** (nové: `tests/test_guards_062.py`, `tests/test_daily_deepseek_062.py`).

### Časť 1 – poistky v kóde (`pipeline/ai_guards.py`, `validate`)
- **Žánre:** žáner ostane, len ak jeho citát v `genre_facts` **aj** prieskum (fakty kroku 1 + text stránky podniku) obsahujú názov žánru, schválený alias alebo pravopisný variant ako celé slovo.
  - Názvy iných žánrov sa pred hľadaním vymažú, takže nadradený žáner nemá oporu v podžánri („tech house“ ≠ house, „electronic dance music“ ≠ electronic).
  - „hard techno“ nie je `hardcore` (test).
  - Testy na prípadoch z 061 – všetky zahodené: Warhaus `indie`, Student Wednesday `electronic`, SLVL `hardcore`, Allt `death-metal`, Keo `indie`, Amphibian `ambient`.
- **Cena bez opory:** predtým neplatila, teraz áno. Zahodí sa cena bez sumy a bez slova zdarma/dobrovoľné („Tba“, „bude upřesněno“). Zahodí sa aj cena, ktorej suma nie je vo faktoch ani na stránke podniku.
- **Výkričník:** „!“ v názve akcie alebo v mene interpreta (FIRE!) a „!“ vnútri vety (názvy albumov „Exit!“, „Hello Mom!“) popis nezahodia. „!“ na konci vety ho zahodí.
- **Miesto v popise:** popis CZ s názvom podniku alebo so slovom sály („sál“, „stage“, „čítárna“ …) dostane `needs_review` a nezahadzuje sa.
- **Prompty:**
  - popis podľa F: ≈ 5 viet podľa interpreta, bez ceny, času, miesta, sály a organizátora;
  - preklad: nemeniť fakty, čísla, mená ani rod osôb;
  - typ: pravidlo B7 (Tinlicker).

### Časť 2 – denný beh
- `daily.yml` nastavuje `ENRICH_PROVIDER: deepseek` a `DEEPSEEK_API_KEY` zo secrets. Platí pre `classify_ai` (DeepSeek JSON mode, ten istý prompt a schéma) aj pre `enrich_ai`.
- Claude ostáva ako záloha jednou premennou. `GEMINI_API_KEY` je z denného workflow odstránený.
- **Rozpočet:** 0,30 $ za beh a 3 $ za mesiac (súčet behov v `pipeline_state.json` → `ai_cost`, doplnené v `data-model.md`). Po prekročení sa AI zastaví a beh pokračuje.
- **Limity:** 3 hľadania + 2 načítania na akciu ostávajú. Mesačný limit hľadaní pri DeepSeek je 3 000, skutočný limit je rozpočet v $.
- **Pri HTTP 401/402, rozpočte, výpadku alebo timeoute** dostanú nespracované akcie predchádzajúce AI hodnoty z cache (test). `classify_ai` použije cache aj bez kľúča (test).
  - Overené lokálnym behom bez kľúčov: 208 → **208** akcií so žánrami (v 060 to bolo 208 → 152).
- **Nové vstupy workflow:** `reenrich_days`, `reenrich_from_research`, `ai_budget_usd`, `enrich_timeout_s`. Prieskum sa ukladá cez `research_store` do `site/research/2026-11.json`.
- **Špička:** 04:17 UTC je mimo špičky. Špička DeepSeek aj cron sú v UTC, takže sa v lete nič nemení. Riziko: oneskorenie štartu o viac ako 1 h 40 min by beh posunulo do špičky 06–10 UTC.

### Časť 3 – meranie na 50 akciách
- Rozhodnutie a preklad z uloženého prieskumu 061, bez nového hľadania, so schválenými aliasmi žánrov.
- V CI sa ukázali 2 falošné zahodenia: výkričník v názvoch albumov a české tvary („rockových“, „techna“, „rapper“). Opravil som ich a poistky som znova použil na uložené odpovede modelu (bez API).
- Výsledok: [`062/measure.json`](062/measure.json), [`062/measure.xlsx`](062/measure.xlsx); surové výsledky z CI: `062/redecide-ci.json`.
- Príkazy:
  - `python -m pipeline.revalidate docs/tasks/062/redecide-ci.json docs/tasks/062/measure.json`
  - `python -m pipeline.deepseek_test summary docs/tasks/062/measure.json`

| | 062 | 061 |
|---|---|---|
| typ správne | **48/50** | 47/50 |
| žánre v odpovedi modelu → ponechané | 129 → **104** (zahodených 21) | – |
| nepodložené žánre | 0 bez citátu s názvom; 6 menom len ako variant (napr. „post punk“, „R'n'B“, „techno-house“), všetky v poriadku | 13 |
| ceny od AI | 7, z toho 6 overených GET-om | 8 / 6 |
| na kontrolu (`needs_review`) | 15, z toho 8 kvôli miestu v popise | 9 |
| $ na akciu (len rozhodnutie + preklad) | 0.00109 | – |

- **Chyby typu:**
  - REEAL TIME 3 → `other` (Matej: `performance`);
  - REVO → bez typu (nič nenájdené, pravidlo H).
  - Tinlicker je v teste `concert` (B7 funguje).
- Poistky zahodili spolu 26 položiek; do limitu „viac ako polovica žánrov“ (65) má 21 zahodených žánrov ďaleko:
  - **žánre (21):**
    - Amphibian `ambient`;
    - Warhaus `indie`, `electronic`;
    - Text-appeal `jazz`, `experimental`;
    - Žižkovská benefice `experimental`;
    - Student Wednesday `electronic`;
    - Almost Weekend `electronic`;
    - SLVL `hardstyle`;
    - Video Oldies `pop`;
    - Omah Lay `world`, `pop`;
    - High Speed Fairytales `electronic`;
    - Family Therapy `uk-garage`, `uk-bass` (citát „UK sound … garage“);
    - Tygroo `world` („Balkan music“);
    - Keo `indie`;
    - Arab Strap `experimental`;
    - Asta Hiroki `drum-and-bass` (bez citátu);
    - Colorfactory `indie`, `pop`.
  - **ceny (4):**
    - Bonobo 1 190, Family Therapy 400 a Xzibit 55 € nie sú na stránke;
    - Keo nemá platný zdroj.
  - **`party` bez dôvodu (1):** SLVL.
- **Preklad:** Amphibian SK „francúzsky DJ, producent … ktorý“ – rod je podľa CZ (v 061 bola chyba „producentka“).
- Meranie stálo $0.0544 (zostatok sa zobrazoval stále 1,72 $).

### Časť 4 – prepočítanie 60 dní
- Pred prepočítaním bol zostatok **1,72 $**. Odhad bol 243 akcií × 0,0051 ≈ 1,24 $, teda po prepočítaní ~0,48 $ ≥ 0,40 $, preto **60 dní**.
- Rozpočet behu som dal **1,30 $** namiesto 1,40 $, aby určite ostalo aspoň 0,40 $.
- Výsledok: **243/243 akcií spracovaných, 0 chýb**, 623 hľadaní, **$1.2228**. Zostatok po prepočítaní je **0,46 $**.
- `classify_ai` v tomto behu nevolal API (198 zásahov z cache, 0 nových akcií). Zaradenie cez DeepSeek je teda overené len testami, nie naživo.
- **Zahodené pri prepočítaní:**
  - ceny (z logu behu): 24 – 18× suma nie je na stránke, 4× názov akcie nie je na stránke, 1× chyba GET, 1× slovo „zdarma“ nie je na stránke;
  - žánre a popisy: v tomto behu ešte neboli v logu (job summary sa nedá čítať cez API). Log `enrich_ai dropped by kind` je doplnený v `d1bc4ec`, objaví sa od ďalšieho behu.
- [`062/genres-review.md`](062/genres-review.md) na schválenie Matejom:
  - schválené aliasy;
  - nové mapovania od AI: 0;
  - kandidáti bez žánru zo zoznamu (`maps_to: null`): všetci, s počtom a príkladmi;
  - použité žánre.

### Čísla z `events.json` posledného behu
- Beh 44156896473, `generated_at 2026-11-17T20:44:17+01:00`.
- Príkaz: `python -m pipeline.ai_numbers site/events.json pipeline_state.json` (oba súbory stiahnuté z GitHub Pages).

| | pred (beh 18:51) | po prepočítaní |
|---|---|---|
| akcie | 374 | 374 |
| s AI doplnením (60 dní) | 243 (Claude) | 243 (všetky `deepseek-flash`) |
| typ od AI (`llm` / `llm+web`) | 227 / 119 web | 227 / **173** web (63 so typom zo zdroja, 6 ručne) |
| so žánrami | 208 | **227** |
| s cenou | 146 | **160** |
| cena od AI overená / neoverená (predpredaj, JavaScript) | 16 / 0 | **25 / 5** |
| s časom (z toho od AI) | 331 (32) | **345 (46)** |
| s popisom od AI | 217 | **239** |
| na kontrolu (`needs_review`) | 0 | **85**, z toho 48 kvôli miestu/sále v popise (najčastejšie „stage“ 10, „EPIC Prague“ 6, „Roxy“ 5) |
| kandidáti žánrov | 217 | 121 |

- Cena: beh **$1.2228**, mesiac (`ai_cost`) **$1.2228** (1 beh). Hľadania v mesiaci: 953 / 3 000.
- Zostatok kreditu DeepSeek: **0,46 $**.

### Ručné overenie na webe (2026-11-17, GET stránky a hľadanie hodnôt v texte)
1. **Dekkadancers: Studio 54** – https://archa-plus.cz/cz/program/detail/777/2026-12-14-dekkadancers-studio-54 (cena od AI)
   - na stránke: „Po 14 12, 19:30“, „cena 1 290 Kč“, „cena 890 Kč“, „cena 490 Kč“, „cena 350 Kč“;
   - v dátach: 19:30, Cat.1–4 1 290 / 890 / 490 / 350 Kč – **správne**.
2. **Hentai Corporation – Shirimming tour** – https://goout.net/cs/hentai-corporation-shirimming-tour-krest-alba/szebfly/ (cena od AI)
   - na stránke: „Vstup 19:00 Vstupné 490 Kč“, „pá 18. 12. 20:00“;
   - v dátach: 490 Kč, 20:00 – **správne**.
3. **Žižkovská benefice** – https://citarna.unijazz.cz/events/zizkovska-benefice-banana-split/ (cena od AI)
   - na stránke: „Vstupné … je benefiční a dobrovolné“, „Doporučujeme třeba 200 Kč? 400 Kč?“, „03. 12. 2026 20:00“;
   - v dátach: „benefiční a dobrovolné, doporučeno 200 Kč / 400 Kč“, 20:00 – **správne**.
4. **Stahlzeit** – https://rezervace.ticketportal.cz/event/STAHLZEIT
   - na stránke: „CENA VSTUPENKY 1290 Kč“, „So 21.11. 2026 20:00“;
   - v dátach: 1290 Kč, 20:00 – **správne**.
5. **Tinlicker** – https://www.roxy.cz/events/detail/5077/tinlicker
   - na stránke: „TINLICKER OVLÁDNOU ROXY SVÝM DJ SETEM“, text „místo klasických DJ setů začali vystupovat jako živá kapela“, „So 21/11/2026 23:00“, Early Birds 750 Kč;
   - v dátach: čas a cena správne, ale typ je `dj` a `primary_format` je prázdny – pozri Otvorené.

### Rozhodnutia urobené samostatne (v `decisions.md`)
- Poistka žánrov:
  - citát aj prieskum musia obsahovať názov;
  - maskovanie podžánrov;
  - malý zoznam pravopisných variantov a české tvary.
- Cena bez opory musí mať sumu vo faktoch alebo na stránke podniku.
- Výkričník vnútri vety = názov.
- Miesto v popise → kontrola.
- Rozpočet je spoločný pre zaradenie aj doplnenie a ukladá sa v `pipeline_state.json` (`ai_cost`). Mesačný limit hľadaní pri DeepSeek je 3 000.
- Pri zastavení AI ostávajú predchádzajúce hodnoty. `classify_ai` použije cache vždy.
- Rozpočet prepočítania 1,30 $ (nie 1,40 $) kvôli pravidlu zostatku 0,40 $.
- `058/verdicts.json` a `059/verdicts.json` som tiež odstránil, lebo obsahujú hodnotenia s hodnotami z výstupov Gemini. `061/deepseek-test.json` Gemini neobsahoval, ostal nezmenený.

### Otvorené
- **Tinlicker a typ zo zdroja:** pri 63 akciách má typ zo zdroja podniku (`classification.method: source`) prednosť pred AI, takže B7 sa na ne neuplatní. Tinlicker ostáva `dj` podľa kategórie Roxy, AI dala v teste `concert`. Má B7 prebiť typ zo zdroja? Je to zmena doterajšieho rozhodnutia, preto rozhoduje Matej.
  - 70 akcií s AI doplnením nemá `primary_format` (typ zo zdroja bez hlavného formátu).
- **Kredit DeepSeek 0,46 $:** pri ~280 nových akciách mesačne (~1,4 $) vydrží približne 9–10 dní. Potom príde HTTP 402, AI sa zastaví a beh pokračuje s doterajšími hodnotami. Treba dobiť kredit (Matej). Mesačný strop 3 $ ostáva aj tak.
- **Kontrola:** 85 akcií má `needs_review`; 48 z nich preto, že model napriek promptu píše miesto/sálu.
- **Typ cez `classify_ai`** cez DeepSeek je overený len testami. Nové akcie ho použijú od najbližšieho denného behu.
- Zahodené žánre a popisy pri prepočítaní nie sú zmerané (log až od ďalšieho behu).
- `gemini_test tune-xlsx` po odstránení súborov 058 nefunguje (nepoužíva sa).
- Zvláštny text ceny od AI: „400–600 (presale from 600 CZK)“ (František Skála, neoverená, GoOut). Zobrazenie ide cez parser ceny.
