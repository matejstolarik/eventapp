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

## Report

**Dátum:** 2026-11-17. **Stav: čiastočne hotové.** Kód všetkých častí je hotový a pushnutý. Chýbajú čísla z dvoch denných behov (časť 1) a výsledky pilotu (časť 4): z tohto prostredia sa nedajú spúšťať workflowy ani čítať ich logy a artefakty (nie je `gh` ani GitHub token) a lokálne nie sú API kľúče.

**Commity:** `ea69d91` (časť 1), `29187c2` (časť 2), `53c3b2f` (časť 5), `d491472` + `3a90a75` (časť 4), report v tomto commite.

### Časť 1 – AI cache (hotové v kóde, čaká na overenie behom)
- Príčina potvrdená: `_build_ai_cache` vynechával LLM akcie s `dj`/`concert`/`music` bez `party`. V zverejnenom `events.json` (generated 2026-11-16 13:56) je takých **95** zo 199 LLM akcií. Tie išli do API pri každom behu.
- Oprava: jednorazový trigger z task 020 je odstránený. Cache obsahuje každú LLM akciu, do API ide len nová akcia alebo akcia so zmeneným názvom. Bez zmeny dátového modelu (žiadne `party_checked`). Rozhodnutie je v `decisions.md` (2026-11-17, AI cache).
- Test `test_music_event_without_party_is_cached`.
- Offline overenie na zverejnených dátach: 199 akcií potrebuje AI, **199 cache hits, 0 do API** (predtým 104 hits a 95 do API). Príkaz (`pub.json` = stiahnutý `https://matejstolarik.github.io/eventapp/events.json`):
  `python -c "import json; from pipeline.classify_ai import _build_ai_cache,_events_needing_ai; ev=json.load(open('pub.json',encoding='utf-8'))['events']; c=_build_ai_cache(ev); n=_events_needing_ai(ev); print(len(n), sum(1 for e in n if c.get(e['id'],{}).get('title')==e['title']))"`
- **Otvorené:** dva ručné denné behy po sebe a ich `to classify via API`. Treba 2× spustiť `Daily pipeline` (workflow_dispatch) a doplniť čísla.

### Časť 2 – Prírastok akcií
- Zdroj: pole `first_seen` v zverejnenom `events.json` (2026-11-16 13:56). `site/` nie je v git histórii a artefakty Pages sa bez tokenu stiahnuť nedajú.
- Obmedzenie: súbor obsahuje len budúce akcie. Akcie objavené v daný deň, ktoré sa už odohrali, chýbajú, takže čísla sú **dolný odhad**. Dni 11-02, 11-04, 11-08 a 11-16 sú nábeh nových zdrojov a podnikov (11-16: MeetFactory 37), nie bežný prírastok.
- Nové akcie podľa `first_seen` v bežné dni: 11-09: 8, 11-10: 8, 11-11: 6, 11-12: 10, 11-13: 29 (Čitárna 10 + EPIC 15, dávkové zverejnenie programu), 11-14: 3, 11-15: 2, 11-16 bez MeetFactory: 4. **Priemer 11-09 až 11-15: 66/7 ≈ 9,4 akcie za deň** (medián 8).
- Po podnikoch (11-09 až 11-16, bez nábehu MeetFactory): EPIC 18, Čitárna 10, Cross Club 8, Roxy 8, Archa+ 7, Akropolis 7, Kasárna 6, Fuchs2 3, Forum Karlín 1, Bike Jesus 1.
- Príkaz: `python -c "import json,collections; ev=json.load(open('pub.json',encoding='utf-8'))['events']; v=collections.defaultdict(collections.Counter); [v[e['venue_id']].update([e['first_seen'][:10]]) for e in ev]; [print(k, sorted(v[k].items())) for k in sorted(v)]"`
- Odteraz sa meria presne: denný beh píše do job summary riadok **„New events: N (per venue: …)“** a do logu `New events: …` (nové `id` oproti predchádzajúcemu behu). Meria sa od prvého denného behu po commite `29187c2` (2026-11-17).

### Časť 3 – Návrh dátového modelu (len návrh, čaká na schválenie)
Nové nepovinné pole akcie `enrichment`: mapa pole → pôvod. Je len pri údajoch, ktoré nedodal zdroj podniku.
```json
"enrichment": {
  "formats":     { "by": "ai_text", "model": "claude-haiku-5-5", "checked_at": "2026-11-17", "source_url": null, "confidence": 0.7, "reason": "..." },
  "genres":      { "by": "ai_web",  "model": "...", "checked_at": "...", "source_url": "https://...", "confidence": 0.8 },
  "price_text":  { "by": "ai_web",  "model": "...", "checked_at": "...", "source_url": "https://..." },
  "start_time":  { "by": "ai_web",  "model": "...", "checked_at": "...", "source_url": "https://..." },
  "description": { "by": "ai_web",  "model": "...", "checked_at": "...", "source_urls": ["https://...", "https://..."] },
  "artists":     { "by": "ai_web",  "model": "...", "checked_at": "...", "source_url": "https://..." },
  "artist_links":{ "by": "ai_web",  "model": "...", "checked_at": "...", "source_url": "https://..." }
}
```
- `by`: `ai_text` (len z textu akcie, bez hľadania, teda odhad) alebo `ai_web` (overené hľadaním).
- Pravidlá:
  1. Údaj zo zdroja podniku má vždy prednosť. AI vyplní pole len ak je `null`. Ak ho neskôr dodá zdroj, AI hodnota aj záznam v `enrichment` sa zahodia.
  2. `ai_web` hodnota bez `source_url` sa neuloží.
  3. Výnimka: `formats`/`genres` z textu (`ai_text`, `source_url: null`) sa uložia a appka alebo review ich môže ukázať ako odhad.
  4. `ra.co` nikdy nie je `source_url`.
- Nadviazanie: `description_source` dostane hodnotu `"ai"` (už plánovaná v `data-model.md`), podrobný pôvod je v `enrichment.description`. `classification.method` ostáva (`llm`; `llm+web` je už v dokumente spomenuté).
- Spotify: nové pole akcie `artist_links: [{ "name": "...", "spotify_url": "https://open.spotify.com/artist/..." }]`. `artists` ostáva zoznam textov.
- Cache: `checked_at` + názov akcie. Znova hľadať len pri zmene názvu alebo po N dňoch (napr. cenu 7 dní pred akciou).

### Časť 4 – Pilot (kód hotový, beh čaká)
- `pipeline/enrich_pilot.py` a workflow `.github/workflows/enrich-pilot.yml`: len `workflow_dispatch`, vstup `providers`, artefakt `enrich-pilot-<run_id>` s `enrich_pilot.json`, tabuľka v job summary. Nemení `events.json` ani Pages. Testy `tests/test_enrich_pilot.py` (mock, bez siete).
- **Claude:** `claude-haiku-5-5` so server `web_search` (`max_uses` 3, `blocked_domains: ["ra.co"]`). Skúsi `web_search_20260209` a pri odmietnutí prejde na `web_search_20250305`. Výsledok vracia cez nástroj `report_enrichment`. Spotify URL sa prijme len ak bola vo výsledkoch hľadania. Cena: $0.10/$0.50 za MTok + $10 za 1000 hľadaní.
- **Gemini:** `gemini-2.5-flash-lite` + `google_search` grounding cez REST.
  - Overené v cenníku (aistudio.google.com/docs/pricing, 2026-11-17): grounding na bezplatnej úrovni majú len Gemini 2.5 Flash a 2.5 Flash-Lite („Free of charge, up to 500 RPD“, limit spoločný pre oba). Textové modely Gemini 3.x ho na bezplatnej úrovni nemajú.
  - Stránka rate-limits neuvádza free-tier RPM/RPD pre model (odkazuje na AI Studio), preto je medzi volaniami 6 s.
  - Doménu `ra.co` vylúčiť nejde. Hodnoty so zdrojom `ra.co` sa zahodia a zapíše sa `ra_in_grounding`.
  - Pri HTTP 429/403 alebo chybe hľadania sa Gemini časť zastaví a uloží sa presná odpoveď.
  - Či kľúč beží na bezplatnej úrovni, závisí od projektu v AI Studio (bez billingu = free). Overí sa z odpovede.
- Spoločné pravidlá v kóde:
  - formáty a žánre len zo zoznamov v `classify_ai`;
  - cena, čas a popis bez `source_url` sa zahodia;
  - čas a popis sa dopĺňajú len ak chýbajú;
  - `party` bez `party_reason` sa zahodí.
- Prompt používa **novú definíciu `party`** (Matej 2026-11-17). Strop je 60 hľadaní na poskytovateľa.
- **Výber 20 akcií** (deterministický, `select_events`). Náhľad je na dátach z 2026-11-16 13:56. Pri behu sa vyberá z aktuálneho `events.json` a zoznam bude v artefakte. Všetky sú bez ceny (v dátach nemá cenu žiadna akcia), 15 má podozrivý typ alebo žáner, 7 nemá popis, zastúpených je všetkých 11 podnikov.

| # | Podnik | Akcia | Dnes | Dôvod výberu |
|---|---|---|---|---|
| 1 | cross-club | KŘIŽOVATKA | dj,party / electronic | party bez signálu v názve; istota 0.6 |
| 2 | fuchs2 | HIGH SPEED FAIRYTALES: LIIA ☆ Theya ☆ DJ… | concert,dj,party / techno,electro,ebm,post-punk | party+concert; istota 0.6; bez popisu |
| 3 | bike-jesus | ATHENA CHLEBOVÁ - KŘEST PRAHA + GAMBRZ R… | concert,dj / ∅ | prázdne žánre; bez popisu |
| 4 | palac-akropolis | СОЮЗ (SOYUZ)/BY/PL | concert / ∅ | prázdne žánre; bez popisu |
| 5 | meetfactory | Good Times Only: křest desky + Blue Uandi | concert / ∅ | prázdne žánre |
| 6 | epic | STUDENT WEDNESDAY | dj,party / ∅ | prázdne žánre; bez popisu |
| 7 | archa-plus | ROAST slaví narozky | other / ∅ | typ neurčený; istota 0.4 |
| 8 | citarna-unijazz | Text-appeal vol. 28 | talk / ∅ | istota 0.4 |
| 9 | forum-karlin | Omah Lay | concert / pop,hip-hop | nový podnik do vzorky |
| 10 | kasarna-karlin | Transgender Awareness Week: Lola | film / ∅ | nový typ |
| 11 | roxy | COLORFACTORY | concert / ∅ | prázdne žánre |
| 12 | cross-club | KAVÁRNA KŘEST BOLDRIKOVO KNIHY | concert / ∅ | prázdne žánre (krst knihy?) |
| 13 | fuchs2 | FAMILY THERAPY present Asher ☆ Parashoot… | dj,party / techno,electro | party podľa novej definície?; bez popisu |
| 14 | bike-jesus | .THEMAYREVOLUTION - PRAHA KŘEST 1 /live | concert / ∅ | prázdne žánre; bez popisu |
| 15 | palac-akropolis | DIVADLO NIE ►JEŠTĚ JSME TU | theatre / ∅ | istota 0.5 |
| 16 | meetfactory | Pragokoncert: Allt + Avralize + Bite Down | concert / indie,experimental | nový typ do vzorky |
| 17 | epic | ALMOST WEEKEND | dj,party / ∅ | prázdne žánre; bez popisu |
| 18 | archa-plus | Burkicom: Slunce | dance / ∅ | nový typ |
| 19 | kasarna-karlin | ANIMAGLAJZ – animations from Sutnarka | film,opening / ∅ | istota 0.6 |
| 20 | cross-club | UP TONE w/ MARATHON | dj / ∅ | prázdne žánre |

- Z výberu sú vyradené názvy s „CANCEL“, „zrušen“, „VYPRODÁNO“ a „sold out“.
- **Otvorené:** beh pilotu, tabuľka akcia po akcii (Claude vs. Gemini so `source_url`), ručné overenie aspoň 10 akcií proti webu, presnosť a skutočná cena (hľadania, tokeny, $).

### Predbežný odhad nákladov (pred pilotom, prepočíta sa z nameraných čísel)
- Predpoklad pre Claude: ~3 hľadania × $0.01 + ~15–25k vstupných tokenov × $0.10/MTok ≈ **$0.03–0.035 na akciu**.
- 11 podnikov: ~9,4 nových akcií za deň ≈ 280 za mesiac → **~$9–10 mesačne** (Claude). 50 podnikov (lineárne ×4,5): ~1 300 za mesiac → **~$40–45 mesačne**.
- Gemini 2.5 Flash-Lite: 1 300 akcií za mesiac ≈ 43 za deň, čo je pod bezplatným limitom 500 grounded RPD → $0, ak projekt ostane na bezplatnej úrovni.

### Časť 5 – Testovacie JPEG (hotové)
- `web/public/test-thumb-*.jpg` sú presunuté do `tests/playwright/fixtures/thumbs/`. `web/screenshots051.mjs` a `tests/playwright/screenshots-051.spec.ts` ich servírujú cez `route`.
- `npm run build`: vo `web/dist` je 0 súborov `test-thumb*`.
- `node screenshots051.mjs` prebehol a obrázky v mriežke sa načítali. Výstup v `docs/tasks/051` som vrátil do pôvodného stavu, nové screenshoty úloha nežiadala.
- Zistenie: `npx playwright test` z `web/` nenačíta spec súbory v `tests/playwright/`. Chyba je už pri `screenshots.spec.ts`, nie je z tejto zmeny. Neopravené.

### Rozhodnutia urobené samostatne
- Cache som opravil odstránením triggera, nie značkou v `classification`: bez zmeny dátového modelu a trigger už splnil účel.
- Gemini cez REST a štandardnú knižnicu (bez novej závislosti), model 2.5 Flash-Lite (jediný lacný s bezplatným groundingom).
- Výber akcií je v kóde (reprodukovateľný), nie ručný.

### Čo treba od Mateja
1. Pridať GitHub Secret `GEMINI_API_KEY` (kľúč z AI Studio, projekt bez billingu = bezplatná úroveň).
2. Spustiť `Daily pipeline` 2× po sebe (workflow_dispatch) a potom `Enrich pilot (manual)`.
3. Dať mi výsledky: buď nainštalovať a prihlásiť `gh` (`gh auth login`), alebo poslať job summary oboch denných behov a artefakt `enrich_pilot.json`. Potom doplním časť 1, tabuľku pilotu, overenie proti webu a ceny.
