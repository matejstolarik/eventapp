# 058: Test Gemini 3.5 Flash (2 kroky), prechod na Gemini, žánre, štruktúrovaná cena, prepočítanie

## Zadanie

**Robí sa hneď (pred 057).** Pravidlá z úlohy 056 sú **presunuté sem** (056 sa nerobí samostatne; jej časti 1–3 sú časť 0 tejto úlohy, meranie je v teste). **Schválené Matejom 2026-11-17** vrátane zmien dátového modelu nižšie. Kredit Claude je takmer minutý (~0,19 $): denný beh nesmie spadnúť, keď Claude vráti chybu kreditu (len varovanie). Gemini: projekt `eventapp`, platená úroveň, predplatené ~100 Kč, **bez automatického dobíjania**, nič ďalšie nezapínať.

**Čítaj:** **`docs/ai-rules.md` celé (zdroj pravdy pre prompt)**; `docs/tasks/056-type-rules-from-labels.md` časti 1–3; report 054 (časť 1 – tabuľka Gemini vs. Claude, časť 4a – žánre, Otvorené); `docs/tasks/056/labels-matej.csv` (Matejove pravidlá typu v poznámkach); `docs/data-model.md` (žánre, `price_text`, `enrichment`); kód `pipeline/enrich_ai.py`, `pipeline/enrich_pilot.py`, `pipeline/classify_ai.py`, `web/src/core/eventText.ts`.

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`.

### 0. Pravidlá (z 056) – pred testom
- Prompt zaradenia aj doplnenia prepíš podľa `docs/ai-rules.md` (všetky body A–H) + 8–12 Matejových príkladov z `labels-matej.csv` (ako v 056 časť 2).
- 056 časť 1 (Facebook udalosti ako zdroj, Instagram nie – do `decisions.md`), časť 2 bod 10 (`apply_commercial_clubs()`: party vždy, `primary_format` dj pri známom menovanom DJ), časť 3 (podtyp `performance`, štítok `talk` → „čítanie a diskusia“ / „čtení a diskuse“ / „talk & reading“).

### 1. Test Gemini 3.5 Flash v dvoch krokoch
- Model `gemini-3.5-flash` (nie lite; over názov a cenu na oficiálnej stránke cenníka, odkaz do reportu).
- **Krok 1 – prieskum (s Google Search):** prompt ako otázka, ktorá sa bez hľadania nedá zodpovedať: „Urči všetkých účinkujúcich tejto akcie. **O každom hlavnom účinkujúcom vyhľadaj**, kto to je, odkiaľ je, ako sa prezentuje (kapela / DJ / producent / divadelný súbor…), aký žáner robí, čo vydal. Vyhľadaj aj stránku tejto akcie (web podniku, Facebook udalosť, predpredaj) kvôli cene a času. Vráť fakty so zdrojmi.“ Text stránky podniku daj až do kroku 2, nie sem (inak model nehľadá).
- **Spotify:** v kroku 1 pri každom hlavnom interpretovi samostatné hľadanie „<meno> spotify“. Gemini vracia presmerovacie odkazy (`vertexaisearch…/grounding-api-redirect/…`) – pipeline ich otvorí (HEAD/GET, User-Agent pipeline) a uloží len cieľ `open.spotify.com/artist/…`. Pri rovnakých menách len ak sedí žáner alebo krajina zo zistení o interpretovi; inak bez odkazu. V Exceli stĺpec Spotify; v reporte počet akcií so Spotify (054: 2 z 243).
- **Krok 2 – rozhodnutie (bez hľadania):** z faktov z kroku 1 + text stránky podniku určí typ (`primary_format`, `formats`), žánre **zoradené od hlavného**, cenu (štruktúra z časti 4), čas, interpretov a popis CZ/SK/EN – **z tých istých faktov** (popis, žánre aj typ z jedného prieskumu, nie samostatne). Pravidlá typu: definícia `party` (053), pravidlá z `labels-matej.csv` (hlavný interpret, ako sa prezentuje, harmonogram vs. DJ noc, live elektronika = concert…), štýl popisu (054 časť 4b).
- **Kontrola, že hľadal:** ak v kroku 1 chýba `groundingMetadata` / `webSearchQueries`, zopakuj raz s dôraznejším promptom; ak ani potom, akciu označ „nehľadal“ (v teste aj neskôr v dennom behu – vtedy sa výsledok neukladá ako `ai_web`).
- **Akcie:** 14 ručne overených z 052/054 + **Spitfire Company & PAST** (Akropolis; PAST = experimentálny / industrial hip-hop s elektronikou – Claude ho prehliadol) + 5 sporných z `labels-matej.csv` (Amphibian Quadrophonic Soundsystem, CREDIT 00 (live), DRUMSTATION, SLVL, Bashment Bass Foundation). **Navyše meranie typu na všetkých 50 akciách z `labels-matej.csv`** (len typ, krok 1+2; v Exceli tretí hárok: akcia · očakávané · Gemini · OK/chyba; presnosť spolu a bez akcií použitých ako príklady v prompte).
- **Výstup pre Mateja: `docs/tasks/058/gemini-test.xlsx`** (Arial, hlavička zamrazená, zalomený text, odkazy klikateľné), jeden riadok na akciu, stĺpce: podnik · názov akcie · odkaz · **čo hľadal** (všetky dotazy) · **zdroje** (URL) · **typ** (Gemini) · **žánre** (Gemini, v poradí) · **cena** (Gemini, ako sa zobrazí v appke + zdroj) · čas · interpreti · **popis CZ** · očakávané (overené / Matejovo označenie) · Claude 052/054 · výsledok (✔ / ✗ / ~ + krátko prečo). Druhý hárok: súhrn presnosti (typ, žánre, ceny) Gemini vs. Claude, počet hľadaní, tokeny, **cena testu**.
- **Po teste STOP.** Commit Excelu + report testu a čakaj. Matej Excel skontroluje; časti 2 a 5 sa robia až po jeho súhlase (Matej napíše „pokračuj 058“).
- **Podmienka prechodu:** typ správne **aspoň pri toľkých akciách ako Claude** (na tých istých overených akciách) a **žiadne nepodložené žánre** (každý žáner má oporu v nájdenom fakte). Ak splní → časť 2. Ak nie → zastav, report, nič neprepínaj.

### 2. Prechod na Gemini
- `ENRICH_PROVIDER=gemini` pre AI doplnenie (dvojkrokový postup z časti 1) **aj** pre AI zaradenie (`classify_ai.py`), aby denný beh nepotreboval Claude. Claude ostáva v kóde ako voľba.
- Limit: počítadlo hľadaní z 054 ostáva; pre Gemini nastav mesačný limit **4 500** hľadaní (pod bezplatnými 5 000). Pri chybe kreditu (HTTP 402) varovanie a beh pokračuje.

### 3. Žánre (Matejove rozhodnutia 2026-11-17)
- **Princíp:** mapovať len **synonymá a pravopisné varianty** (napr. `rap → hip-hop`, `d&b → drum-and-bass`). Podžánre zo zoznamu ostávajú samostatné; nadradený žáner sa **automaticky nepridáva** (metalcore ≠ metal).
- **Poradie:** `genres` zoradené od hlavného; zložené názvy → hlavný žáner prvý, napr. „ambient techno“ → `techno, ambient`; „mainstage“ → `edm, electronic`. (Ambient nie je vždy techno – rozhoduje AI podľa faktov.)
- **Nové hudobné žánre:** `blues`, `industrial`, `hardcore`, `bass-music`, `rave`, `dream-pop`, `darkwave`, `slowcore`, `oldies`, `edm`, `metalcore`, `death-metal`, `grindcore`, `goregrind`. **Nový žáner `stage_genres`:** `physical-theatre`. **Zamietnuté:** `mainstream`. `queer rave → rave`. `r-n-b` **premenovať na `rnb`** (dáta, kód, preklady).
- `bass music` sa **nemapuje** na `uk-bass` (UK bass len pre interpretov z UK) ani na `bassline` (konkrétny štýl zo Sheffieldu).
- i18n štítkov pre nové žánre (SK/CZ/EN, názvy žánrov väčšinou rovnaké; `physical-theatre` → „fyzické divadlo“ / „fyzické divadlo“ / „physical theatre“).
- **Export na kontrolu:** `docs/tasks/058/genres-review.md` – tabuľka všetkých mapovaní (surový názov → náš žáner, počet akcií, príklad) a všetkých kandidátov mimo zoznamu (aj < 3 akcie), po prepočítaní (časť 5).

### 4. Štruktúrovaná cena (zmena dátového modelu)
- Nové pole `price`: `{ min, max, currency, kind }`, `kind` ∈ `paid` | `free` | `voluntary` (dobrovoľné vstupné) | `free_reservation` (zdarma s rezerváciou). `price_text` ostáva ako pôvodný text zo zdroja (neukazuje sa). Do `data-model.md`.
- Pravidlá: viac cien (zľavnená, predpredaj/na mieste, BASIC/VIP) → **rozpätie** min–max; len „od X“ → `min` bez `max`; iná mena sa zachová.
- **Zobrazenie v appke podľa jazyka:** `350 Kč`, `250–350 Kč`, `od 950 Kč` / `od 950 Kč` / `from 950 CZK`, `20 €`, „Zdarma“ / „Zdarma“ / „Free“, „Dobrovoľné vstupné“ / „Dobrovolné vstupné“ / „Pay what you want“, „Zdarma, rezervácia“ / „Zdarma, rezervace“ / „Free, booking required“. Bez ďalšieho textu. Vypredané bez zmeny.
- Parser pre ceny z webov podnikov (časť 2 úlohy 054) aj výstup AI. Testy na reálnych vzorkách z `tests/fixtures/prices/`.

### 5. Prepočítanie existujúcich akcií
Po prechode (časť 2): všetky akcie v najbližších 60 dňoch znova cez Gemini (ignorovať cache, `reenrich`), aby dostali nové žánre, poradie, cenu a opravy ako PAST. Hľadania sa zmestia do bezplatných 5 000.

## Overenie a report
- `pytest -q`, `npm test` (`--reporter=dot`), build OK.
- Report: odkaz na `gemini-test.xlsx`, súhrn testu, rozhodnutie o prechode; po prepočítaní (z `site/events.json`, s príkazom): počty s cenou / časom / žánrami / popisom pred a po, počet hľadaní a cena behu, počet akcií „nehľadal“; ručne over 5 akcií (URL + čo tam je), z toho PAST.
- `genres-review.md` hotový.

## Poradie po tejto úlohe
056 (pravidlá typu, meranie – už s Gemini) → 057 (reporty).

## Report – časť 0, 1, 3, 4 (test Gemini; STOP pred časťami 2 a 5)

**Dátum:** 2026-11-17. **Stav: test hotový, podmienka prechodu splnená, čakám na „pokračuj 058“.** Časti 2 (prechod) a 5 (prepočítanie) nie sú urobené, denný beh má stále `ENRICH_PROVIDER: claude`.

**Commity:** časť 0 `4a6a41b` (performance, štítky, komerčný klub, Facebook) + `309160a` (prompty podľa `docs/ai-rules.md`); časť 3 `c1e64cc`; časť 4 `61aa01c`, `241a388`; časť 1 `309160a`, `1ae0646`, `f675dcb`, `02158e4`, `9774840`; report a Excel v tomto commite.

**Výstup pre Mateja:** [`docs/tasks/058/gemini-test.xlsx`](058/gemini-test.xlsx)
- hárok Akcie: 20 akcií = 14 overených + Spitfire & PAST + 5 sporných,
- hárok Súhrn,
- hárok Typ 50 akcií.

Surové výsledky sú v `docs/tasks/058/gemini_test.json`, moje hodnotenie v `docs/tasks/058/verdicts.json`.

### Časť 0 – pravidlá
- Prompty AI zaradenia (`classify_ai.py`) aj doplnenia (`enrich_ai.py`) sa skladajú z `pipeline/ai_rules.py`, kde sú body A–H z `docs/ai-rules.md`.
- V prompte je 12 Matejových príkladov: Amphibian, Tinlicker, Modeselektor, CREDIT 00, DRUMSTATION, Family Therapy, SLVL, Student Wednesday, Bashment, Set and Play, Kavárna křest, High Speed Fairytales. Ich zoznam je v `EXAMPLE_IDS` a v meraní sú vyznačené.
- Facebook udalosti môže AI pri hľadaní čítať, Instagram nie (`decisions.md`). Instagram je v kóde blokovaný ako zdroj rovnako ako `ra.co`.
- `apply_commercial_clubs()`: `party` sa pridá vždy. `primary_format` je `party`, okrem prípadu, keď AI určila `dj`.
- Podtyp `performance` (kultúra, ikona masiek). Štítky v appke sa prekladajú (`tagLabel`):
  - `talk` → „čítanie a diskusia“ / „čtení a diskuse“ / „talk & reading“,
  - `physical-theatre` → „fyzické divadlo“ / „physical theatre“.

### Časť 1 – test Gemini (beh [44106345171](https://github.com/matejstolarik/eventapp/actions/runs/44106345171))
- **Model:** `gemini-3.6-flash`, nie `gemini-3.5-flash`. Podľa https://aistudio.google.com/docs/models/gemini-3.5-flash je 3.5 Flash zastaraný a API ho automaticky presmeruje na 3.6 Flash. V zozname modelov API je ešte uvedený (beh [44105729633](https://github.com/matejstolarik/eventapp/actions/runs/44105729633)).
- **Cena modelu:** podľa https://aistudio.google.com/docs/pricing (2026-11-17) $0.75 vstup / $3.75 výstup za MTok do 31. 12. 2026, od 1. 1. 2027 $1.50 / $7.50. Hľadania: 5 000 za mesiac zdarma, potom $14 za 1 000.
- **Postup:**
  - Krok 1: prieskum s Google Search bez textu stránky podniku. Pri každom hlavnom interpretovi aj hľadanie „<meno> spotify“.
  - Krok 2: rozhodnutie bez hľadania z faktov, očíslovaných zdrojov a textu stránky.
  - Zdroje sa rozbalia z presmerovaní (HEAD bez nasledovania). `source_url` musí byť jeden z nich alebo stránka akcie, inak sa zahodí.
- **Čísla** (z `docs/tasks/058/gemini_test.json`):
  - 55 akcií, 0 chýb, 0× „nehľadal“, 1× opakovaný pokus (ten už hľadal);
  - 356 hľadaní (6,5 na akciu);
  - 329 798 vstupných + 318 591 výstupných tokenov, **$1.44** (~$0.026 na akciu). Skúšobný beh na 2 akciách stál $0.05.
- **Typ, 14 overených akcií: Gemini 14/14**, Claude 052 13 ✔ + 1 ~.
- **Typ, 50 akcií z `labels-matej.csv`: 47/50 (94 %), bez príkladov v prompte 35/38 (92 %).** Chyby:
  - REEAL TIME 3 → `other` (očakávané `performance`);
  - REVO: Z Gumy Do Gumy → nič nenašiel, typ prázdny (pravidlo H);
  - VIDEO OLDIES RUDA TUČEKA → `dj` + party (Matej: `party`). AI považuje Rudu Tučeka za menovaného DJ-a, rovnako ako SLVL.
- **Žánre:** žiadny nepodložený, každý žáner má fakt v `genre_facts` (stĺpec v Exceli). Zoradenie od hlavného funguje, napr. Allt `metalcore, metal, hardcore`, Athena `hip-hop` prvý.
  - Sporné: High Speed Fairytales `uk-bass` (nie je zistené, že DJ King Kobra je z UK).
  - PAST nájdený: Spitfire & PAST → `theatre`, žánre `hip-hop, physical-theatre`, 440 Kč overená na GoOut.
- **Ceny, 14 overených akcií:** Gemini uviedol 12 cien, 10 správnych. Athena mala 290–390 Kč, pričom overená cena je 290 Kč. Family Therapy mala vymyslenú cenu 400 Kč, overenie ju zahodilo. Claude 052 mal 7 správnych z 9.
- **Ceny v celom teste:** overenie jedným GET uložilo 9 cien, 15 zahodilo:
  - Akropolis ukazuje cenu až cez JavaScript (3 akcie, pri SOYUZ aj správnu 400 Kč);
  - Ticketmaster vracia 403 (2), rachot.cz má chybu SSL (1);
  - suma alebo slovo „zdarma“ na zdrojovej stránke chýba (8, z toho Family Therapy vymyslená);
  - názov akcie na stránke chýba (1).
  - Pri teste som opravil overovanie: „1490.00 Kč“ a ceny s dátumami (`9774840`). Výsledky som po oprave prepočítal lokálne bez nového volania AI (`python -m pipeline.gemini_test recheck docs/tasks/058/gemini_test.json pub.json`, `pub.json` = zverejnený `events.json` 2026-11-17 14:37).
- **Spotify: 0 z 55** (054: 2 z 243). Gemini urobil 124 hľadaní „<meno> spotify“, ale Google Search nevrátil ako zdroj ani jednu stránku `open.spotify.com/artist/…`. Pri 4 akciách vrátil `kworb.net/spotify/artist/<ID>`. Odkaz sa z nich dá odvodiť (ID je Spotify ID), ale je to nový spôsob, preto som ho nezaviedol.
- **Podmienka prechodu: splnená.** Typ 14/14 je aspoň toľko ako Claude (13). Žiadne nepodložené žánre.

Príkazy:
- presnosť typu na 50 akciách: `python -m pipeline.gemini_test xlsx docs/tasks/058/gemini_test.json docs/tasks/058/gemini-test.xlsx docs/tasks/058/verdicts.json` (vypíše `type 50 = 47/50 (94 %), without examples = 35/38 (92 %)`);
- tokeny, hľadania a cena: `totals` v `docs/tasks/058/gemini_test.json`.

### Časť 3 – žánre (kód hotový, `genres-review.md` až po časti 5)
- Nový zoznam: 47 hudobných žánrov, `rnb` namiesto `r-n-b` (premenuje sa aj v starších dátach pri každom behu), `stage_genres` = `physical-theatre`. Kód je v `pipeline/genres.py`.
- Mapuje sa len pravopisný variant (automaticky) a schválené synonymá v `data/genre_aliases.json`. Návrh `maps_to` od AI sa sám nepoužije.
- Pri kultúrnej akcii s hudobníkmi sa ukladajú aj hudobné žánre (PAST).

### Časť 4 – štruktúrovaná cena (kód hotový)
- Pole `price {min, max, currency, kind}` je v `data-model.md`. Počíta ho `pipeline/price.py` z `price_text` pri každom behu.
- Testy na reálnych textoch z `events.json` a `tests/fixtures/prices/` (`tests/test_price_struct.py`, 28 testov). Všetkých 82 rôznych `price_text` v zverejnených dátach sa rozpozná.
- Appka zobrazuje `price` podľa jazyka (`priceLabel`). Kým beh `price` nedoplní, zobrazuje sa ako doteraz `price_text`.

### Overenie
- `pytest -q` 318 passed.
- `npx vitest run --reporter=dot` 199 passed.
- `npm run build` OK.

### Rozhodnutia urobené samostatne (v `decisions.md`)
- Model `gemini-3.6-flash` namiesto zastaraného 3.5.
- Zdroje sa rozbaľujú HEAD-om bez nasledovania presmerovania. Spotify meno sa zisťuje jedným GET.
- Cena so zdrojom na Facebooku sa neuloží, lebo pipeline Facebook nesťahuje.
- Synonymá v `data/genre_aliases.json`. Obsahujú aj staršie schválené `psytrance → trance` a `reggaeton → latin`, ktoré treba skontrolovať v `genres-review.md`.
- Cena sa počíta jedným parserom v `main.py`.
- Overenie ceny podľa sparsovaných súm.

### Otvorené – na rozhodnutie Matejovi pred „pokračuj 058“
- **Kredit Gemini nestačí na časť 5.**
  - Test minul ~$1.49 (test + skúšobný beh) z predplatených ~100 Kč (~$4.3).
  - Prepočítanie ~245 akcií v 60 dňoch stojí pri $0.026 na akciu ~$6.4, od 1. 1. 2027 dvojnásobok.
  - Bežný denný beh (len nové akcie, jednotky za deň) je lacný.
  - Možnosti: dobiť kredit, alebo prepočítať len časť akcií.
- Spotify cez Gemini nefunguje (0/55). Možnosti: odkaz z `kworb.net/spotify/artist/<ID>` (nový spôsob), Spotify API (nový zdroj), alebo ostať pri vyhľadávaní podľa mena.
- Cena z Akropolis (načítava sa JavaScriptom) a z Ticketmastera (403) sa nedá overiť jedným GET, takže sa zahodí aj správna.
- VIDEO OLDIES RUDA TUČEKA: má byť Ruda Tuček „známy menovaný DJ“ (→ `dj`), alebo `party`? Pravidlo B5 to zatiaľ nerozlišuje.
