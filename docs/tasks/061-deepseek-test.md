# 061: Test DeepSeek ako náhrady Gemini/Claude (hľadanie + rozhodnutie + preklad)

## Zadanie

> **ZMENA 2026-11-17 večer (Matej, pred spustením) – platí pred všetkým nižšie.**
> - Kredit DeepSeek je **2 $** (nie ~5 $). Rozpočet v kóde: **zastaviť pri 1 $ za beh** (nahrádza 2 $), HTTP 402 → stop. Pred celým testom pusti 3 akcie a z nich odhadni cenu 50; ak odhad presahuje 1 $, zastav a napíš to.
> - Model `deepseek-flash`, endpoint Search/Fetch (`/v1/tools/search`) a ich parametre sú v zadaní z prieskumu hlavného chatu, nie overené v kóde. **Ak sa oficiálne docs DeepSeek (časť 1) líšia (iný názov modelu, endpoint, chýbajúci Fetch, iný spôsob hľadania), zastav po časti 1 a napíš rozdiely.** Neimprovizuj náhradu.

**Schválené Matejom 2026-11-17.** Gemini s Google hľadaním nesmieme použiť (podmienky, pozri hlavičku 060). DeepSeek: výstup patrí nám, podmienky API ukladanie výsledkov ani dávkový beh nezakazujú, publikovaný AI obsah treba označiť ako AI (Terms of Use). Tento test zistí, či DeepSeek dosiahne kvalitu Gemini D na Matejových 50 označených akciách. **Len test, nič do denného behu.**

**Predpoklad (Matej):** účet na `platform.deepseek.com`, predplatený kredit (~5 $), GitHub Secret `DEEPSEEK_API_KEY`. Bez kľúča zastav a napíš to.

**Čítaj:** `docs/ai-rules.md` (celé); report 058 (Časť 1) a 059 (tabuľka variantov, Časť 3); `pipeline/gemini_test.py` (testovací rámec, výber 50 akcií, Excel); `pipeline/enrich_ai.py` (`_Gemini2`, pravidlá v kóde – `apply_rules`); `pipeline/research_store.py`; `docs/tasks/056/labels-matej.csv`; oficiálne docs DeepSeek: `api-docs.deepseek.com/guides/search/`, `/quick_start/pricing`, `/guides/json_mode`, `/guides/tool_calls`.

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`.

### 1. Overenie oficiálnych údajov (pred kódom)
- Z oficiálnych stránok DeepSeek do reportu (URL + citát): ceny `deepseek-flash` (vstup cache hit/miss, výstup), **kedy je špička a mimo špičky** (v pražskom čase), cena Search a Fetch, limity, či Search/Fetch API alebo podmienky (`cdn.deepseek.com/policies/…`) obmedzujú ukladanie výsledkov alebo vyžadujú citácie. Ak niečo nenájdeš, napíš „nenájdené“.

### 2. Provider `_DeepSeek` (variant A, celý DeepSeek)
- Model `deepseek-flash` s **tool calls**: nástroje `search(query)` a `fetch(url)` vykonáva náš kód cez `POST https://api.deepseek.com/v1/tools/search` a Fetch API (DeepSeek docs). Limit na akciu: najviac **3 hľadania + 2 načítania** (pri koncertoch/DJ). Do každého dotazu pridať `-site:ra.co -site:instagram.com`; výsledky z `ra.co` a `instagram.com` zahodiť aj v kóde. Facebook povolený.
- Postup a výstup podľa `docs/ai-rules.md` A–H (typ, `primary_format`, žánre s citátom z faktov, cena, čas, interpreti, popis CZ); **Spotify sa nehľadá** (G). Výstup JSON (JSON mode) v rovnakom tvare ako `_Gemini2`, aby išiel cez tie isté poistky (`apply_rules`: citát žánru, URL len z výsledkov, cena bez opory → prázdna, „Tba“ → prázdne).
- Preklad CZ → SK, EN: `deepseek-flash`, samostatné lacné volanie (alebo v tom istom, ak je lacnejšie – zdôvodni).
- Prieskum (fakty + URL) ukladať cez `research_store.py`, aby sa dal neskôr znova rozhodnúť bez hľadania.
- Rozpočet v kóde: zastaviť pri 2 $ za beh; HTTP 402 → stop. Zapisovať tokeny, hľadania, načítania a cenu na akciu.
- Ručný workflow `deepseek-test.yml` (`workflow_dispatch`), kľúč len z `secrets.DEEPSEEK_API_KEY`.

### 3. Test na 50 akciách
- Tie isté akcie ako v 058/059 (Matejove označenia). Výsledok do `docs/tasks/061/deepseek-test.xlsx` + `.json`: na akciu Matejove označenie, Gemini D (z `059/tune.json`), DeepSeek A; stĺpce typ (zhoda áno/nie), žánre, cena (+ overenie), čas, interpreti, popis CZ, zdroje (URL), hľadania, cena v $.
- Súhrn v reporte: typ správne X/50 (D mal 47/50), žánre (zhoda s Matejovým `expected` a s D), počet cien (a koľko overených otvorením stránky), počet akcií, kde hľadanie nenašlo nič relevantné, zahodené poistkami, **priemerná a celková cena na akciu**, odhad mesačne pri 280 a 1 300 nových akciách (špička vs. mimo špičky).
- 10 popisov CZ + ich SK/EN preklad vypíš do reportu na Matejovo posúdenie češtiny.
- Ručne over 5 akcií na webe (URL + čo tam je).

### Mimo rozsahu
- Variant B (hľadanie DeepSeek + rozhodnutie Gemini bez hľadania) – len ak to Matej po reporte schváli.
- Denný beh, `events.json`, appka (označenie „AI“ pri popise rozhodne Matej po teste).

## Overenie a report
- `pytest -q` OK (testy providera na uložených odpovediach, bez siete).
- Číslo behu workflow, príkaz na súhrn z `docs/tasks/061/deepseek-test.json`.
- Otvorené body a odporúčanie: A, B, alebo nepoužiť.
