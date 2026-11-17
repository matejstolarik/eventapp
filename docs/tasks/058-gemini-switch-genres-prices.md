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
