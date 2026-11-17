# 052: Oprava AI cache, meranie prírastku akcií, pilot AI doplnenia s hľadaním (Claude vs. Gemini)

## Zadanie

**Schválené Matejom 2026-11-17:** AI s hľadaním na internete smie určovať a overovať typ a žánre, dopĺňať cenu, čas, popis a interpretov/Spotify odkaz (nový spôsob získavania dát – výnimka z pravidla v `CLAUDE.md` je týmto odsúhlasená **len pre pilot**; nasadenie do denného behu až po ďalšom súhlase). Obrázky z internetu **nie**. Resident Advisor (`ra.co`) sa nesmie použiť ani cez výsledky hľadania.

**Čítaj:** `docs/decisions.md` – `grep -n "AI vrstva\|classify_ai\|party" docs/decisions.md`; `docs/data-model.md` – len časť o akcii (polia `formats`, `genres`, `price_text`, `start_time`, `description`, `description_source`, `classification`); kód `pipeline/classify_ai.py`, `pipeline/detail_enrich.py` (ak existuje pod iným menom, nájdi cez `grep -rn "detail_enrich" pipeline`), `.github/workflows/daily.yml`.

Každá časť vlastný commit. Časti 1–3 sa robia prvé; pilot (4) beží len ručne.

### 1. Oprava AI cache (chyba)
Príčina (hlavný chat z kódu): `_build_ai_cache` v `classify_ai.py` vynecháva hudobné akcie klasifikované LLM bez `party` („one-time trigger“). Lenže tie akcie `party` nedostanú nikdy, takže sa posielajú do AI pri **každom** behu – logy 12.–16. 11.: 83–131 akcií na beh, aj dva behy v ten istý deň.
- Oprav tak, aby sa akcia s nezmeneným názvom a výsledkom LLM znova neposielala (napr. značka `party_checked` v `classification`, alebo trigger len pre výsledky staršie ako zavedenie `party`).
- Test. Po nasadení ručne spusti denný beh dvakrát za sebou; druhý beh musí mať `to classify via API` ≈ 0 (len nové/zmenené akcie). Čísla oboch behov do reportu.

### 2. Meranie prírastku akcií
Zisti, koľko **nových** akcií (nové `id`) pribúda za deň a podnik. Zdroj: história behov (artefakty / `events.json` z Pages / git história – použi, čo je dostupné). Ak história nestačí, pridaj do denného behu riadok do job summary „new events: N (per venue …)“ a v reporte uveď, odkedy sa meria. Príkaz/zdroj čísel do reportu.

### 3. Návrh zmeny dátového modelu (len návrh, neimplementovať)
Do reportu (nie do `data-model.md`) navrhni, ako pri každom údaji doplnenom AI uložiť **pôvod** a **odkaz na zdroj**: typ/formáty, žánre, cena, čas, popis (už existuje `description_source` – nadviaž), interpreti, Spotify odkaz. Napr. pole `enrichment: { field: { by: "ai_web", source_url, model, checked_at } }` alebo podobne. Musí platiť: údaj zo zdroja podniku má prednosť; AI hodnota bez `source_url` sa neukladá (okrem žánru/typu z textu, ktorý je označený ako odhad). Matej návrh schváli pred implementáciou.

### 4. Pilot na 20 akciách (Claude aj Gemini)
- **Spustenie:** nový workflow `.github/workflows/enrich-pilot.yml`, len `workflow_dispatch`, kľúče z GitHub Secrets `ANTHROPIC_API_KEY` a `GEMINI_API_KEY`. Skript napr. `pipeline/enrich_pilot.py`. **Nemení `events.json` ani denný beh**; výsledky uloží ako artefakt (JSON) a zhrnutie do job summary.
- **Výber 20 akcií** z aktuálnych dát: rôzne podniky (aspoň Cross Club, Fuchs2, Bike Jesus, Akropolis, MeetFactory, EPIC, Archa+), rôzne typy, aspoň 6 akcií, kde je dnešný typ alebo žáner podozrivý (napr. `party` pri akcii, ktorá vyzerá ako koncert kapely, alebo prázdne žánre), aspoň 5 bez popisu a všetky bez ceny. Zoznam s dôvodom výberu do reportu.
- **Čo AI pre každú akciu vráti** (štruktúrovaný výstup, jedno volanie na akciu, najviac 3 hľadania):
  - typ/formáty a žánre (len z pevného zoznamu v `data-model.md`), s `source_url` a istotou; pri neistote prázdne,
  - interpreti (mená) a Spotify odkaz `open.spotify.com/artist/…` **len ak sa objavil vo výsledkoch hľadania** a zhoda je jasná,
  - cena alebo rozsah cien **len výslovne uvedená pri tejto akcii a dátume**, so `source_url`,
  - čas začiatku len ak chýba a je výslovne uvedený, so `source_url`,
  - popis 2–3 vety v češtine vlastnými slovami (nekopírovať), len ak chýba; so zdrojmi.
  - Najprv použi text detailu akcie, ktorý pipeline už sťahuje (režim A); hľadaj len to, čo v ňom nie je.
- **Definícia `party` (Matej 2026-11-17, nahrádza „klubová noc alebo tematická párty“ v `data-model.md`; zmenu dokumentu a produkčného promptu rieši úloha 053):** `party` = veľká komerčná/mainstreamová párty, kam ľudia idú kvôli atmosfére, nie kvôli konkrétnej hudbe či interpretovi (komerčné kluby, Erasmus/študentské, hity 80./90., open bar, mainstreamové tematické večery). Klubová noc zameraná na hudbu/DJ-ov je `dj`, nie `party`. `party` len pri jasnom signáli a s uvedeným dôvodom. V pilote použi túto definíciu v prompte oboch poskytovateľov a pri porovnaní s dnešným stavom ju ber ako správnu.
- **Claude:** `claude-haiku-5-5` + web search tool (`max_uses: 3`, zakázaná doména `ra.co`).
- **Gemini:** najlacnejší aktuálny model s Grounding with Google Search na **bezplatnej úrovni** (over v dokumentácii, ktorý model a aké limity; nič neplatené nezapínaj). Ak sa doména `ra.co` nedá vylúčiť, výsledky s `ra.co` zahoď a napíš to do reportu. Ak bezplatná úroveň hľadanie nepodporuje alebo narazí na limit, **zastav Gemini časť a napíš presne, čo vrátilo** (chyba, limit).
- **Strop pilotu:** najviac 60 hľadaní na poskytovateľa.

### 5. Drobnosť z 051
Testovacie JPEG presuň z `web/public/` mimo nasadzovaný priečinok (len pre test server Playwrightu), aby sa nedostali na Pages.

## Report (povinné)
- Časť 1: čísla dvoch po sebe idúcich behov.
- Časť 2: nové akcie za deň (spolu a po podnikoch), zdroj a príkaz.
- Časť 3: návrh modelu.
- Časť 4: **tabuľka akcia po akcii**: dnešný typ/žánre → Claude → Gemini, cena, čas, interpreti/Spotify, či bol popis doplnený; pri každom údaji `source_url`. **Ručne over aspoň 10 akcií** proti webu (URL + čo tam je) a označ, kto mal pravdu. Súhrn presnosti oboch poskytovateľov.
- Cena pilotu pre každého poskytovateľa: počet hľadaní, tokeny, dolárov; pre Gemini aj to, či išlo z bezplatnej úrovne a aké limity platili.
- Odhad mesačných nákladov pri dnešných 11 podnikoch a pri 50 podnikoch (z nameraného prírastku z časti 2).
- Čo nefungovalo / čo ostalo otvorené.
