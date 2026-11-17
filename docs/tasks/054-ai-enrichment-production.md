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

## Report

**Dátum:** 2026-11-17. **Stav: hotové** (otvorené body na konci).

**Commity:** časť 1 `f11873c`, `a576a65`, `39ccf70`, `fb532f2`, `dd12173`; časť 2 `dd12173` (zmeny adaptérov Archa+/Akropolis a `detail_enrich` sa omylom dostali do commitu s opravou pilotu) + `e00d56c`; časť 3 `f5d9ece`; časť 4 `5b63740`; časť 5 `ea22456`; oprava po overení `5649733`; report a screenshot v tomto commite.

**Behy:** pilot Gemini [44077395754](https://github.com/matejstolarik/eventapp/actions/runs/44077395754), [44078065827](https://github.com/matejstolarik/eventapp/actions/runs/44078065827), [44078482813](https://github.com/matejstolarik/eventapp/actions/runs/44078482813), [44078488131](https://github.com/matejstolarik/eventapp/actions/runs/44078488131), [44079278045](https://github.com/matejstolarik/eventapp/actions/runs/44079278045). Denné behy: [44080923669](https://github.com/matejstolarik/eventapp/actions/runs/44080923669) (1), [44082337257](https://github.com/matejstolarik/eventapp/actions/runs/44082337257) (2, backfill), [44085753105](https://github.com/matejstolarik/eventapp/actions/runs/44085753105) (3), [44087053350](https://github.com/matejstolarik/eventapp/actions/runs/44087053350) (4, posledný, s opravou `5649733`).

### Časť 1 – Pilot Gemini na platenej úrovni
- Všetkých 20 akcií z 052 je v dátach (rovnaké `id` aj názov), nič sa nenahrádzalo. Prompt, pravidlá a strop 60 hľadaní sú rovnaké ako v 052.
- **Model `gemini-3.1-flash-lite`** (odpoveď API `modelVersion: gemini-3.1-flash-lite`, HTTP 200). Podľa https://aistudio.google.com/docs/pricing (2026-11-17) je to najlacnejší textový model s Grounding with Google Search: $0.25 vstup / $1.50 výstup za MTok, 5 000 hľadaní mesačne zdarma (spoločne pre Gemini 3+), potom $14 za 1 000. Modely 2.5 sú pre nových používateľov nedostupné (052).
- **Gemini skoro nehľadá.** S rovnakým promptom ako Claude urobil 0 hľadaní (2 behy, `groundingMetadata` v odpovedi úplne chýba). `gemini-3.5-flash-lite` urobil 3 hľadania pri 2 akciách. S jednou vetou navyše („Use Google Search to verify every value…“) urobil 1 hľadanie. Hodnoty berie z vlastných znalostí a pri niektorých uvádza zdroj `vertexaisearch…/grounding-api-redirect/…`, hoci API žiadne hľadanie nevykázalo.
- Tokeny a cena (z `usageMetadata` a cenníka; skutočné vyúčtovanie v AI Studio overiť nemôžem, nemám prístup):
  - Gemini, beh 44078482813 (rovnaký prompt): 21 415 vstupných + 9 458 výstupných tokenov, 0 hľadaní = **$0.0195 za 20 akcií (~$0.001 na akciu)**.
  - Claude (052): 478 445 + 26 779 tokenov, 26 hľadaní = **$0.3212 (~$0.016 na akciu)**.
- Text výsledkov hľadania: Gemini ho **neúčtuje ako vstupné tokeny**. Pri 2 akciách s hľadaním bol `promptTokenCount` 973 a 943, teda len prompt, a `toolUsePromptTokenCount` chýbal. Claude ho účtuje (~24 000 vstupných tokenov na akciu).

| # | Akcia | Overené (052) | Claude (052) | Gemini 3.1-flash-lite (rovnaký prompt) |
|---|---|---|---|---|
| 1 | Cross KŘIŽOVATKA | dj, DnB + rap, zdarma, 20:00 | dj / dnb, hip-hop ✔, zdarma ✔ | dj / hip-hop, dnb ✔, zdarma ✔ (zdroj redirect), 20:00 ✔ |
| 2 | Fuchs2 HIGH SPEED FAIRYTALES | dj, DnB / broken beats, bez ceny | dj / dnb, uk-garage, electronic ✔ | dj / dnb, electronic ✔ |
| 3 | Bike Jesus Athena Chlebová | concert (krst), 290 Kč, 20:00 | concert,dj / hip-hop ✔, 290 ✔, 20:00 ✔ | concert,dj / hip-hop + techno, house ✗, cena –, čas – |
| 4 | Akropolis СОЮЗ | folk / pop, 400 Kč | folk, pop ✔, 400 ✔ | jazz, folk, pop ~, cena – |
| 6 | EPIC STUDENT WEDNESDAY | dj,party, BASIC 290 / VIP 500 | dj,party ✔, cena – | dj ✗ (bez party), 290 Kč ~ (bez VIP) |
| 7 | Archa+ ROAST | talk / comedy, zdarma | talk,other ~, cena – | party,other ✗, cena – |
| 9 | Forum Omah Lay | concert pop / hip-hop | ✔, Spotify ✔ | ✔, Spotify – |
| 11 | Roxy COLORFACTORY | concert, 990 Kč | concert ✔, 990 ✔ | concert / electronic, pop, 990 ✔ |
| 12 | Cross KAVÁRNA KŘEST knihy | talk (+dj) | talk,dj ✔ | other ✗ |
| 13 | Fuchs2 FAMILY THERAPY | dj, cena na webe nie je | dj ✔, 400 Kč ✗ vymyslená | dj ✔, 400 Kč ✗ vymyslená |
| 16 | MeetFactory Allt | concert metal(core), od 950 Kč, 20:00 | metal ✔, cena –, 20:00 ✔ | metal + electronic ~, 950 Kč ✔, 20:00 ✔ |
| 17 | EPIC ALMOST WEEKEND | dj,party, 250 / 400 | dj,party ✔, 250/400 ✔ (zlý zdroj) | dj ✗ (bez party), 250–400 ✔ (správny zdroj) |
| 19 | Kasárna ANIMAGLAJZ | film, 100 CZK, 19:00 | film ✔, 100 ✔ | film ✔, 100 ✔ |
| 20 | Cross UP TONE | concert,dj post-punk / shoegaze, zdarma, 20:00 | všetko ✔ | ✔ + techno, zdarma ✔, 20:00 ✔ |

Spolu na 14 overených akciách:
- **Typ:** Claude 13 ✔ + 1 ~, Gemini 10 ✔ (✗ pri #6, #7, #12, #17).
- **Žánre:** Claude bez chyby, Gemini pridáva nepodložené žánre (#3, #4, #16).
- **Ceny:** Claude 7 správnych z 9 (1 vymyslená), Gemini 7 správnych z 8 (1 vymyslená, našiel ich viac).

**Výber pre časť 4: Claude.** Gemini nemá presnosť typu a žánrov aspoň takú ako Claude, čo zadanie vyžaduje, a nižšia cena to nemení. Prepínač `ENRICH_PROVIDER` (`claude` | `gemini`) je v kóde, denný beh má `claude`.

### Časť 2 – Ceny a časy zo stránok podnikov (bez AI)
Overené 2026-11-17 na stránkach akcií (vzorky sú v `tests/fixtures/prices/`):

| Podnik | Cena na webe | Kde | Vyťahuje sa teraz | S cenou pred → po (60 dní) |
|---|---|---|---|---|
| EPIC | áno | `.event-detail__price` „Vstupné BASIC: 250,-kč \| VIP: 400,-kč“ | áno (`detail_enrich`) | 0 → 31/31 |
| MeetFactory | áno | „Vstupenky:“ a riadky s cenami pod ním | áno | 0 → 18/20 |
| Roxy | áno | „Vstupenky: 599 Kč“, „Základní vstupné 990 Kč“ | áno | 0 → 16/21 |
| Cross Club | čiastočne | „Vstupné: zdarma / free entry“ („via FOURCE“ a „Tba“ sa neukladajú), „Začátek: 20:00“ | áno, aj čas | 0 → 9 (+1 AI)/15; čas 15/15 |
| Čitárna | áno | veta „Vstupné v předprodeji 250 Kč / 350 Kč na místě“ | áno | 0 → 9 (+1 AI)/16 |
| Kasárna | čiastočne | „Admission: 100 CZK“ | áno | 0 → 2/14 |
| Archa+ | len „vstup zdarma“ | štítok v programe | áno (adaptér) | 0 → 6 (+4 AI)/35 |
| Akropolis | len „VSTUP VOLNÝ“ | kód 3 vo `vstupne_6` | áno (adaptér) | 0 → 0 (+5 AI)/44 |
| Fuchs2 | nie | len odkaz na ra.co | – | 0 → 0/16 |
| Forum Karlín | nie (výnimočne v texte) | tlačidlá Ticketmaster / Ticketportal | – | 0 → 0 (+2 AI)/13 |
| Bike Jesus | nie | Strapi API bez ceny | – | 0 → 0 (+3 AI)/18 |

V celom `events.json` (180 dní) má cenu po zmene **146 z 374 akcií** (predtým 0). Cena sa ukladá bez slova návestia (`design.md` časť 7), napr. „zdarma / free entry“, „od 950 Kč na webu pořadatele“.

### Časť 3 – Dátový model
- `docs/data-model.md` má nové polia a pravidlá:
  - `enrichment`: `run`, mapa pole → `{by, model, checked_at, source_url | source_urls, confidence, reason}` a `genre_candidates`;
  - `artist_links`, `descriptions {cs, sk, en}`, `description_source: "ai"`, `classification.method: "llm+web"`;
  - pravidlá doplňovania a cache;
  - nový stavový súbor `pipeline_state.json`.
- Pravidlá sú aj v kóde (`pipeline/enrich_ai.py`): zdroj má prednosť a prepíše AI hodnotu, `ai_web` hodnota bez `source_url` sa neuloží, `ra.co` je zablokované v nástroji hľadania a navyše sa zahodí v kóde.

### Časť 4 – AI doplnenie v dennom behu (+ 4a, 4b)
| Beh | Hľadania | Mesiac / limit | Cena | Doplnené | Z cache |
|---|---|---|---|---|---|
| 1 (44080923669) | 0 | – | $0 | 0 (stav ešte nebol zverejnený, Pages vrátil 503, AI sa preto bezpečne nespustilo) | – |
| 2 (44082337257, backfill) | **325** | 325 / 400 | **$4.29** | 243 | 0 |
| 3 (44085753105) | **0** | 325 / 400 | $0 | 0 | 243 |
| 4 (44087053350, posledný) | **0** | 325 / 400 | $0 | 0 | 243 |

Backfill stál $0.0177 na akciu (1,34 hľadania na akciu), bez chýb, trval ~14 min. Ceny, ktoré neprešli overením jedným GET na zdroj, sa zahodili: 8.

**Pred a po:** pred = zverejnený `events.json` 2026-11-17 11:23, po = beh 4 (13:58); akcie od 2026-11-17 do 2027-01-16.

| | Pred | Po |
|---|---|---|
| Akcie v 60 dňoch | 243 | 243 |
| S cenou | 0 | 107 (91 z webu podniku, 16 od AI) |
| S časom | 177 | 224 (15 z webu Cross, 32 od AI) |
| S popisom (`description` alebo `descriptions`) | 180 | 230; `descriptions` od AI 217 |
| Hudobné so žánrami | 86 / 176 | 154 / 171 |
| S interpretmi | 0 | 198 |
| S `artist_links` (Spotify) | 0 | **2** |
| Zmena typu (`formats`) | – | 50 akcií (z toho 14 EPIC: `party` → `party, dj`) |
| `classification.method` | llm 147, source 67, keyword 29 | llm+web 119, source 63, llm 55, manual 6 |

Príkaz (`before.json` = zverejnený `events.json` 11:23, `run4.json` = zverejnený po behu 4):
`python -c "import json,collections,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); ev=[e for e in d['events'] if '2026-11-17'<=e['date']<='2027-01-16' and e.get('status')!='cancelled']; m=[e for e in ev if set(e.get('formats') or [])&{'concert','dj','party','music'}]; E=lambda e,k: k in (e.get('enrichment') or {}); print(len(ev), sum(1 for e in ev if e.get('price_text')), sum(1 for e in ev if E(e,'price_text')), sum(1 for e in ev if e.get('start_time')), sum(1 for e in ev if e.get('description') or e.get('descriptions')), sum(1 for e in ev if e.get('descriptions')), len(m), sum(1 for e in m if e.get('genres')), sum(1 for e in ev if e.get('artists')), sum(1 for e in ev if e.get('artist_links')), collections.Counter((e.get('classification') or {}).get('method') for e in ev))" run4.json`

**Ručné overenie doplnených akcií proti webu (2026-11-17, 11 akcií, 7 s cenou od AI):**
1. Gurriers (Bike Jesus), AI 490 Kč – https://goout.net/en/gurriers+support-enola-gay/szuuoiy/: „Entry CZK 490“ ✔
2. Rikas (Bike Jesus), AI 590 Kč – https://goout.net/cs/rikas/szatoiy/: „Vstupné 590 Kč“ ✔
3. Hrdza (Akropolis), AI 450 Kč – https://goout.net/cs/hrdza-vanocni-turne/szwckky/: „Vstupné 450 Kč“ ✔
4. Cocotte Minute (Akropolis), AI 590 Kč – https://www.smsticket.cz/vstupenky/71890-cocotte-minute-palac-akropolis-praha-post-it-anteater: „11. prosince … Palác Akropolis … Cena 590 Kč“ ✔
5. José González (Archa+), AI 990 Kč – https://vikendo.cz/events/jose-gonzalez-archa: „Vstupenky za 990 Kč“ ✔
6. Adéla (Forum Karlín), AI 1120 Kč – https://www.forumkarlin.cz/udalost/adela: „Vstupenky (1120 korun)“ ✔
7. Slava Vakarchuk (Forum Karlín), AI 990 CZK a typ talk → concert – https://ticketsvakarchuk.com/cz/event/vakarchuk_prague_forumkarlin_291126: „29.11.2026 20:00 Forum Karlín … 990.00 CZK“, je to koncert ✔
8. Mat213 (Archa+), concert / hip-hop, indie, pop + popis – https://archa-plus.cz/cz/program/detail/791/2026-11-27-mat213-krest-desky-a-medley-nejvetsich-hitu: „Rap, indie pop, hyperpop, folk“, ceny Apollo a Vinyl za Objav roka, nástupca albumu Nesu oheň v 2026 ✔ (fakty v popise sedia, text je vlastnými slovami)
9. The Stranger (Kasárna), film + popis – https://kasarnakarlin.cz/en/program/2026/11/24/the-stranger-2025: Ozon, adaptácia Camusa, Benátky ✔; ďalšie fakty (César pre P. Lottina) sú z en.wikipedia a neoveril som ich
10. Allt (MeetFactory): concert / metal ✔, cena „od 950 Kč na webu pořadatele“ (z webu podniku) ✔, popis ~ – uvádza „debut From The New World vyšiel v roku 2025“, Matejov vzor uvádza 2024, pravdepodobne chyba
11. Křižovatka (Cross Club): **typ ✗**. AI dala `dj, party` s dôvodom „Cross Club listing marks the night as Party“. Na https://www.crossclub.cz/cs/program/8718-krizovatka/ je „Party – Hlavní stage“ len názov sály, podľa definície je to `dj`. Rovnako dopadli „Prodigy afterparty rave“ a „Los Tekkenos“ (Cross Club). Prompt je opravený v `5649733`, už spracované akcie sa nezmenia (cache podľa názvu).

**4a – Návrhy žánrov po backfille** (`site/genre_proposals.json`, aspoň 3 akcie; v appke sa nezobrazujú):

| Návrh | Typ | Počet | Príklady |
|---|---|---|---|
| mainstream | hudba | 11 | [EPIC Student Wednesday](https://www.epicprague.com/program/2297/student-wednesday), [Almost Weekend](https://www.epicprague.com/program/2075/almost-weekend), [Erasmus Semester Closing](https://www.epicprague.com/program/2243/erasmus-semester-closing) |
| blues | hudba | 3 | [František Skála (Akropolis)](https://palacakropolis.cz/work/33298?event_id=41254&genre=1&no=62&page_id=33824), [Mirek Kemel (Akropolis)](https://palacakropolis.cz/work/33298?event_id=40213&genre=1&no=62&page_id=33824), [Michal Prokop (Forum Karlín)](https://www.forumkarlin.cz/udalost/vanocni-koncert-michala-prokopa-framus-five) |
| industrial | hudba | 3 | [Revo Spirála (Bike Jesus)](https://bikejesus.com), [Chelsea Wolfe (Archa+)](https://archa-plus.cz/cz/program/detail/833/2026-12-05-chelsea-wolfe-the-dark-world-tour), [Neurobeat (Roxy)](https://www.roxy.cz/events/detail/5177/www-neurobeat-dvacet-let-od-prvniho-uderu-porad-pod-kuzi) |
| physical theatre | divadlo | 3 | [Tantehorse (Akropolis)](https://palacakropolis.cz/work/33298?event_id=40492&genre=2&no=62&page_id=33824), [Laterna magika (Akropolis)](https://palacakropolis.cz/work/33298?event_id=40703&genre=2&no=62&page_id=33824), [Divadlo NIE (Archa+)](https://archa-plus.cz/cz/program/detail/928/2026-12-01-jeden-a-jeden-a-jeden-1) |

„mainstream“ nie je žáner, ale charakter večera (EPIC), navrhujem ho zamietnuť. Pri filme nemá žiadny žáner aspoň 3 akcie.

**Navrhnuté mapovania** (AI `maps_to`, v `genres` sú už použité; celý zoznam 107 mapovaní je v `site/genre_aliases.json`), čakajú na schválenie:
- Sporné: `hardcore → punk` (môže to byť aj hardcore techno), `bass music → bassline`, `ambient techno → ambient`, `darkwave → post-punk`, `dream pop → indie`, `slowcore → indie`, `chanson → folk`, `oldies → pop`, `mainstage → electronic`, `queer rave → electronic`, `gore / death / grind → metal`, `beatdown hardcore → punk`.
- Bez problému napríklad `metalcore → metal`, `neurofunk / jungle / liquid funk → drum-and-bass`, `psytrance → trance`, `rap / trap → hip-hop`, `deep house / afro house → house`, `afrobeats / klezmer / balkan → world`, `dub / dancehall → reggae`.

### Časť 5 – Appka
- `web/src/core/eventText.ts`:
  - popis: `descriptions[jazyk]` → `descriptions.cs` → `description`, bez označenia, že je od AI;
  - Spotify: `artist_links[0].spotify_url`, inak doterajšie vyhľadávanie.
  - Testy sú v `eventText.test.ts`.
- Cena: `price_text` sa zobrazuje bez zmeny kódu (overené na screenshote).
- Overenie: `npx vitest run --reporter=dot` 195 passed, `npm run build` OK, `pytest -q` 282 passed.
- Screenshot `docs/tasks/054/stranka-akcie-ai-popis.jpg`: Hrdza (Akropolis, 3. 12.), cena 450 Kč a slovenský popis, oboje od AI. Skript `web/screenshots054.mjs` berie dáta z behu 4 a v DOM overil, že cena aj popis sú na stránke.

### Rozhodnutia urobené samostatne (všetky v `decisions.md`)
- Stav medzi behmi je v `site/pipeline_state.json` na Pages, nie v cache Actions. Ak sa nedá načítať (iná chyba ako 404), AI sa nespustí, lebo počítadlo hľadaní by bolo neznáme. Stalo sa to v behu 1 (503).
- Oproti návrhu z 052 pribudlo `enrichment.run`, aby fungovala cache aj pri akcii, kde AI nič nedoplnila.
- Návrhy a mapovania žánrov sú v `site/`, nie v `data/`, lebo denný beh nemôže zapisovať do repozitára. Schválené mapovania sa dávajú ručne do `data/genre_aliases.json` (zatiaľ `{}`).
- Po dosiahnutí limitu 400 sa nespracované akcie odložia na ďalší mesiac a AI sa bez hľadania nevolá. Inak by ostali v cache navždy neoverené.
- Popis s výkričníkom, emoji alebo reklamnou frázou sa zahodí.
- Formát a žánre AI nemení pri `manual` a `source`. Pravidlo komerčného klubu beží až po AI.
- Chýbajúca cena z webu podniku sa kontroluje znova najskôr po 7 dňoch.
- Na API idú 4 súbežné požiadavky a celý krok má limit 25 min.

### Čo ostáva otvorené
- **Spotify je len pri 2 akciách z 243.** Claude vo výsledkoch hľadania takmer nevidí stránky `open.spotify.com/artist/…`. Ak to má byť častejšie, treba iný spôsob (napr. Spotify API, čo je nový zdroj a rozhodnutie pre Mateja).
- Cross Club má `dj, party` pri 3 DJ nociach (pozri overenie, bod 11). Prompt je opravený, ale existujúce akcie sa prepočítajú len pri zmene názvu. Treba rozhodnúť, či ich prepočítať (~$0.05).
- Akcie bez popisu `detail_enrich` sťahuje pri každom behu (91 stránok na beh). Takto to fungovalo už pred touto úlohou, neopravené.
- Archa+ a Akropolis majú `price_text` „vstup zdarma“ / „vstup volný“ (slovo „vstup“ je z webu). Ak má byť len „zdarma“, je to malá úprava.
- Novembrový limit: ostáva 75 hľadaní (≈ 55 nových akcií), zvyšok novembra sa dobehne v decembri.
- Skutočnú cenu Gemini v AI Studio som nevidel (nemám prístup), uvedená cena je vypočítaná z tokenov a cenníka.
- Úloha 057 čaká súbor `data/genre_proposals.json`, ten je ale v `site/genre_proposals.json` (pozri rozhodnutia).
