# 054: Pilot Gemini (platená úroveň), ceny zo stránok podnikov, AI doplnenie v dennom behu

## Zadanie

**Robí sa po 053.** **Schválené Matejom 2026-11-17:**
- zmena dátového modelu podľa návrhu z 052 časť 3 (`enrichment`, `artist_links`, `description_source: "ai"`),
- AI s hľadaním v dennom behu (nový spôsob získavania dát), mesačný limit **400 hľadaní**,
- overenie ceny od AI jedným GET na jej `source_url` (nový spôsob sťahovania, len na tento účel).
- Gemini: projekt `eventapp` má platenú úroveň s predplatením ~100 Kč, **bez automatického dobíjania**; nič ďalšie neplatiť ani nezapínať. Ak kredit dôjde (HTTP 402), zastav Gemini a napíš to.

**Čítaj:** report úlohy 052 (`docs/tasks/052-ai-cache-enrich-pilot.md`, sekcie Časť 3, Časť 4 – výsledky, Závery); `docs/data-model.md` časť o akcii; `docs/design.md` časť 7, bod „Spotify (doplnenie 2026-11-17)“; kód `pipeline/enrich_pilot.py`, `pipeline/classify_ai.py`, `pipeline/detail_enrich.py`, adaptéry podnikov z časti 2.

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`.

### 1. Pilot Gemini na platenej úrovni
- Rovnakých 20 akcií ako v 052 (rovnaké `id`; ak už niektorá v dátach nie je, napíš ktorá a nahraď ju podobnou), rovnaký prompt, pravidlá a strop 60 hľadaní.
- Model: najlacnejší aktuálny Gemini model s Grounding with Google Search pre nových používateľov (over v oficiálnej dokumentácii a z odpovede API; v reporte model a odkaz na stránku s cenou).
- Report: tabuľka Gemini vs. Claude (z 052) pri tých istých akciách; pri 14 akciách ručne overených v 052 kto mal pravdu; tokeny, hľadania, skutočná cena (z odpovede API / AI Studio) a či sa text výsledkov hľadania účtoval ako vstupné tokeny.
- **Výber poskytovateľa pre časť 4:** Gemini, ak má na overených akciách presnosť typu, žánrov a cien **aspoň takú ako Claude** a nižšiu cenu na akciu; inak Claude. Výsledok a čísla v reporte. Poskytovateľ sa prepína premennou `ENRICH_PROVIDER` (`claude` | `gemini`).

### 2. Ceny a časy zo stránok podnikov (bez AI)
- Pre každý podnik zisti, či stránka akcie (alebo program) uvádza cenu a čas. Známe: EPIC (BASIC/VIP), MeetFactory („od … Kč“), Kasárna („Admission: … CZK“), Roxy, Archa+ („vstup zdarma“), Cross Club („zdarma“ / „via …“). Ostatné over.
- Kde áno, vyťahuj `price_text` (presne podľa zdroja, aj rozsah a „zdarma“) a chýbajúci čas v adaptéri alebo `detail_enrich`. Fixtúry a testy.
- V reporte tabuľka: podnik → cena na webe áno/nie, kde, či sa teraz vyťahuje; počet akcií s cenou pred/po.

### 3. Dátový model
Implementuj návrh z 052 (časť 3) do `data-model.md` a pipeline: `enrichment` (pôvod, `source_url`/`source_urls`, `model`, `checked_at`, `confidence`, `reason`), `artist_links`, `description_source: "ai"`, `classification.method: "llm+web"`. Pravidlá: údaj zo zdroja podniku má prednosť a prepíše AI hodnotu; `ai_web` hodnota bez `source_url` sa neuloží; `ra.co` nikdy nie je zdroj.

### 4. AI doplnenie v dennom behu
- Rozsah: akcie v **najbližších 60 dňoch**, ktoré sú nové alebo majú zmenený názov (cache cez `previous_events` + `enrichment.checked_at`, rovnako ako AI cache). Vzdialenejšie akcie sa spracujú, keď sa dostanú do 60 dní.
- Pri každej takej akcii: overenie typu a žánrov hľadaním (definície z 053, `primary_format`), doplnenie chýbajúcej ceny, času, popisu (2–3 vety česky, vlastnými slovami), interpretov a `artist_links` (Spotify len ak bol vo výsledkoch hľadania). Najprv text stránky akcie (už stiahnutý), hľadať len chýbajúce.
- **Overenie ceny:** pred uložením jeden GET na `source_url` (User-Agent pipeline, timeout, nie `ra.co`); cena sa uloží, len ak text stránky obsahuje danú sumu **a** názov akcie alebo hlavného interpreta. Inak zahodiť a zapísať do logu.
- **Limit:** najviac 400 hľadaní za kalendárny mesiac (stav v cache medzi behmi). Po dosiahnutí sa hľadanie preskočí, beh pokračuje a v job summary je varovanie. Prvé doplnenie (backfill) sa počíta do limitu; čo sa nestihne, dobehne v ďalších dňoch/mesiaci.
- Chyba AI alebo poskytovateľa nesmie zastaviť denný beh (varovanie, pokračovať bez doplnenia).
- Job summary: hľadania tento mesiac / limit, cena behu, počty doplnených polí (typ zmenený, žánre, cena, čas, popis, Spotify), zahodené ceny.

### 4a. Žánre a návrhy nových žánrov (Matej 2026-11-17)
- Žánre aj pre kultúru: nové zoznamy `film_genres` a `stage_genres` (divadlo, tanec, performance) v `data-model.md`, **na začiatku prázdne** – plnia sa len schválenými návrhmi. Hudobný zoznam (33) ostáva.
- AI vráti aj žánre mimo zoznamov (`genre_candidates`, surový text). Ak zapadá pod existujúci žáner, namapuj ho (`data/genre_aliases.json`: surový → náš, aby sa dalo kontrolovať). Ak nie, ulož ako **návrh** (`data/genre_proposals.json`: názov, typ hudba/film/divadlo, počet akcií, príklady `event_id`); v appke sa **nezobrazuje**.
- Návrh sa hlási až pri **≥ 3 akciách**. Schválené žánre pridáva do zoznamov hlavný chat podľa Matejovho rozhodnutia.
- **Po prvom behu na existujúcich akciách (backfill)** daj do reportu tejto úlohy tabuľku návrhov (názov, typ, počet, 2–3 príklady s odkazom) a navrhnuté mapovania – Matej ich schváli hneď, nečaká na týždenný report.

### 4b. Popis akcie od AI pri každej akcii (Matej 2026-11-17, schválené vrátane zmeny dátového modelu)
- **Každá** akcia v rozsahu časti 4 dostane popis od AI v troch jazykoch v jednom volaní: `descriptions: { "cs": …, "sk": …, "en": … }` (nové pole v `data-model.md`). Čeština je hlavná, `sk` a `en` sú preklady toho istého textu.
- Podklad: pôvodný popis zo zdroja (ostáva v dátach ako `description`, v appke sa nezobrazuje) + fakty z hľadania. Z pôvodného textu sa **preberajú fakty, nie vety** – nekopírovať ani neprehadzovať slová (autorské práva).
- **Štýl:** 3–5 viet, vecný, informatívny, ide do hĺbky (kto to je, odkiaľ, čím je známy, čo vydal, čo je na večeri zvláštne: krst, návrat, hostia). **Bez reklamných fráz** („nezmeškejte“, „legendární“, „nezapomenutelný“, „unikátní zážitek“), bez pátosu, bez výkričníkov a emoji, bez ceny, času a miesta (sú inde v appke). Len fakty zo zdrojov; čo sa nenašlo, sa nepíše (ani „pražská“, ak to zdroj neuvádza).
- **Názvy žánrov sa neskloňujú ani nepočešťujú:** „techno“, „drum and bass“, „metalcore“, „afrobeats“ – nie „technové“, „drum and bassový“, „metalcorová“. (Napr. „album v žánri techno“ / „techno album“.)
- **Vzor (schválený Matejom):** „Švédská kapela Allt z Karlskogy hraje progresivní metalcore a od svého vzniku v roce 2020 si vybudovala pověst skupiny, která staví koncerty jako audiovizuální příběh. Debut From The New World z roku 2024 je koncepční deska o kolapsu a přežití, ovlivněná zbrojním průmyslem v jejich rodném městě. Letos vydali u Century Media druhé album Ataraxia a v MeetFactory, kde v roce 2024 předskakovali Imminence, se teď představí jako hlavní hvězda. Večer otevřou německá kapela Avralize a švédští Bite Down.“ Vlož ho do promptu ako príklad.
- `enrichment.description` so `source_urls`. Ak AI nemá dosť faktov (napr. len názov), napíše kratší popis z toho, čo má, alebo nič – nevymýšľa.

### 5. Appka
- Popis akcie: zobraz `descriptions[jazyk appky]`, ak chýba `descriptions.cs`, ak chýba aj ten, doterajší `description`. Popis od AI sa v appke **neoznačuje**.
- Tlačidlo Spotify: `artist_links[0].spotify_url`, ak existuje; inak doterajšie vyhľadávanie.
- Cena sa už zobrazuje (`price_text`) – len over, že funguje s novými dátami.

## Overenie
- `pytest -q`, `npm test` (`--reporter=dot`), build OK.
- Denný beh ručne 2× po sebe. Z `site/events.json` posledného behu (s príkazom): počet akcií v 60 dňoch; s cenou, s časom, s popisom, so žánrami (pri hudobných), so `artist_links` – pred (dnešné dáta) a po; počet zmien typu; hľadania a cena oboch behov (druhý beh ≈ 0 hľadaní).
- **Ručne over 10 náhodných doplnených akcií** proti webu (URL + čo tam je), aspoň 5 s cenou od AI.
- Screenshot (Playwright, JPEG 390 × 844 do `docs/tasks/054/`): `stranka-akcie-ai-popis.jpg` (akcia s cenou a popisom od AI, bez poznámky).
