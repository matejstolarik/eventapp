# 089: Nové podniky – dávka 3 (Karlovy Lázně, Café V Lese, Klub 007 Strahov, OX Club, Kampus Hybernská) + mesačný limit pri behoch z úloh

## Zadanie

**Schválené Matejom 2026-11-20 až 2026-11-22.** Mení dáta → **jeden beh pipeline na konci** (druhý len pri oprave, ktorá mení dáta). Rovnaký postup a pravidlá ako **085 a 086** (prečítaj ich zadania a reporty: adaptéry, cache detailov, `venues.json`, `first_loaded`, upozornenie na obrázok miesta, AI okno 180 dní, jednorazový limit behu). **El Magico je v samostatnej úlohe 090** (nový typ zdroja – plagát cez obrázkový vstup). Čo nie je jasné, spýtaj sa.

**Čítaj:** reporty **083** (Karlovy Lázně) a **088** (Café V Lese, 007, OX Club, Kampus – vrátane „Doplnenie po spätnej väzbe Mateja“), Excel `docs/tasks/088/venue-survey-4.xlsx`, fixtures `tests/fixtures/survey2/` (`cafevlese_*`, `klub007_*`, `oxclub_*`, `kampushybernska_*`, Karlovy Lázně z 083), stratégia `mec_ajax` (Čitárna Unijazz), `docs/venue-capacity.md`. Ak sa web od fixtures líši tak, že plán nesedí, **zastav a napíš**.

### 1. Karlovy Lázně
- `karlovylazne.cz/events` (HTML, SolidPixels, SSR). Jeden podnik (5 poschodí len v popise akcie). Výpis = generické noci aktuálneho týždňa (aj minulé dni – tie odfiltruje pipeline) + NYE. **Opakované turistické noci pridať** (Matej 2026-11-20). Kapacita **1000** (Matej). IG `karlovylazne`. Obrázok miesta og 2048×1363.

### 2. Café V Lese
- Plugin MEC ako Čitárna Unijazz → stratégia `mec_ajax` / `jsonld`. **Rozdiel:** kalendár nemá číselné skin ID → poslať reťazec `atts` zo stránky namiesto `skin_id` (088: overené 6 POST dec.–máj). Malá úprava existujúcej stratégie, nie nový spôsob sťahovania; Čitárna sa nesmie pokaziť (test).
- JSON-LD čas má chybnú zónu `+00:00` → brať miestnu časť (ako O2). **Čas 19:30 brať ako začiatok** (Matej 2026-11-22, hoci je pri 44/45 akcií rovnaký). Cena „0 USD“ → `null`.
- Obrázok miesta: og:image chýba, fotky pozadia sú na výšku 636×1091 → použi najlepšiu fotku z webu; ak je len logo/grafika, napíš to (Matej pošle). Kapacita `null` (nezistená), IG `cafevlese`.

### 3. Klub 007 Strahov
- JSON-LD (EventON) všetkých akcií na titulke, 1 požiadavka. **Dátumy nie sú platné ISO** (`2026-12-3T19:00+1:00`) → tolerantný parser (len pre tento zdroj alebo bezpečne všeobecne; testy, iné zdroje sa nesmú zmeniť). Čas = začiatok; `endDate` 22:00 = koniec živej hudby (web) → `end_time`. Žáner z podtitulu `evcal_event_subtitle` do surových údajov (AI ho použije). Cena len ak je v popise.
- Kapacita **180** (web /informace/). IG nezistený (`null`). Obrázok miesta og 1200×630 (FB grafika – Matej môže vymeniť).

### 4. OX Club Prague (Francouzská 75/4)
- `oxclubprague.com/program`: statické karty sú šablóna; **skutočný program je base64 XML v inline skripte `dios_xml_akce`** (088 doplnenie, `oxclub_akce_decoded.xml`). Polia `nazev`, `popis` (HTML), `datumakce` (`D.M.YYYY`), `mpic` (plagát 531×531), `nazevurl`, `index`. Odkaz akcie `/shop/b<index>-<nazevurl>.htm`. 1 GET denne, detail netreba.
- Čas a cena len ak sú v texte popisu („Doors: 19:00 / Start: 20:00“); inak `null`. **„PRIVATE EVENT“ / `neprodavat`=1 vynechať** (logovať).
- Kapacita `null` (web ju neuvádza; tretie strany 1000/1200 – Matej rozhodne). IG `oxclubprague`. Obrázok miesta z galérie (2048×1365).

### 5. Kampus Hybernská
- `kampushybernska.cz/program` (Webflow, stránkovanie `?9857990c_page=N`, 4 strany po 20). **Všetky akcie, bez filtra kategórií** (Matej 2026-11-22) – typ a podtyp určí AI ako pri ostatných (workshop, talk, film…). „Druh akce“, čas od–do, cena z detailu (len nové akcie, cache). Jeden podnik (miestnosti len ako sála). Program ~1 mesiac dopredu. Ak sa kľúč stránkovania zmení → 0 akcií → existujúce varovanie.
- Kapacita `null`, IG `kampus.hybernska`, obrázok miesta og 2400×1260 (grafika – Matej môže vymeniť).

### 6. Mesačný limit DeepSeek pri behoch z úloh (Matej 2026-11-22)
- **Beh spustený z úlohy pri pridávaní podnikov ignoruje mesačný limit** (napr. vstup workflowu `ignore_monthly_cap: true` spolu s `ai_budget_usd`); **denné automatické behy (schedule) mesačný limit 5 $ dodržiavajú** ako doteraz. Zapíš do `docs/decisions.md`; test.
- Beh na konci tejto úlohy: `ai_budget_usd` napr. 1,00 $ a `ignore_monthly_cap: true`.

### 7. Záznamy vo `venues.json`
- Ako 085/086: `size` podľa kapacity (pri `null` podľa pravidla v `data-model.md`), zdroj kapacity do `notes`, adresa a súradnice z webu/OSM, `description: null`, `closing` z webu alebo `null`.
- `type`, `character`, `music`: **návrh** s 5–8 ukážkami akcií pri každom mieste (Matej schvaľuje; `character` sa dedí na akcie).

## Overenie a report
- `pytest -q` (Karlovy výpis, Café V Lese `atts` + zóna + Čitárna bez zmeny, 007 tolerantné dátumy, OX base64 XML + vynechanie private, Kampus stránkovanie, mesačný limit pri behu z úlohy vs. denný beh).
- **Jeden beh pipeline** (číslo). Tabuľka z publikovaného `events.json` ako v 086 (akcie, čas, otvorenie, cena, plagát, náhľad po mieste; vyradené), AI: doplnené, čaká, cena behu, mesačne.
- Overenie na webe: 2 akcie z každého miesta.
- Tabuľka návrhu štítkov s ukážkami; zoznam chýbajúcich údajov pre Mateja (kapacity, obrázky, zatváracie časy).
- Snímka `docs/tasks/089/events-new-venues.jpg` ako v 086.

## Report

**Dátum:** 2026-11-22. **Commity:** `f271e93` (adaptéry, `venues.json`, mesačný limit, testy, docs), report + snímka v nasledujúcom commite.
**Stav:** hotovo – všetkých 5 miest funguje, časť 6 (mesačný limit pri behu z úlohy) hotová. Pipeline bežal **raz** (45024287597, success). Pozn.: súčasne bežal oneskorený denný beh 45023309749 (spustený 12:38, starý kód) – môj prvý štart (45023577522) som zrušil, aby si behy neprepisovali stav; denný beh potom zlyhal pri deployi („No artifacts named github-pages“, chyba GitHubu) a nič nepublikoval.

### Hotovo
- **Karlovy Lázně** – `html/karlovylazne`: výpis (názov, dátum + čas = začiatok, plagát 1920 px), detail cez cache (popis s poschodiami/DJ, og:image, odkaz na rezerváciu bez `?date=`). Opakované noci ostávajú; minulé dni týždňa odfiltruje okno.
- **Café V Lese** – existujúci `jsonld/mec_ajax` + `atts_from_page` (1 GET titulky, POST s reťazcom `atts` ako posiela JS kalendára, nov.–máj) + `ld_local_time` (19:30 z miestnej časti `startDate` napriek `+00:00`). Cena „0 USD“ sa nečíta. Čitárna posiela tie isté polia ako predtým (test).
- **Klub 007 Strahov** – nová stratégia `jsonld/eventon` (1 GET): tolerantný parser `2026-12-3T19:00+1:00` len pre tento zdroj, `endDate` 22:00 → `end_time` (23:59 → null), podtitul → `sources[].section`, cena z riadku „Vstupné …“, HTML entity v názvoch odstránené.
- **OX Club** – `html/oxclub`: base64 XML `dios_xml_akce` (1 GET), odkaz `/shop/b<index>-<nazevurl>.htm`, plagát `mpic`, `djs` → `artists`, čas/cena len z textu. PRIVATE EVENT (27. 11.) vynechaný a zalogovaný.
- **Kampus Hybernská** – `html/kampus`: 4 strany `?9857990c_page=N` + detail cez cache (úplný dátum s rokom, „Druh akce“ → `section`, vstupné, og:image, popis). Všetky kategórie.
- **Mesačný limit (časť 6):** vstup workflowu `ignore_monthly_cap` → `DEEPSEEK_IGNORE_MONTHLY_CAP`; platí len keď `GITHUB_EVENT_NAME` ≠ `schedule`; ignoruje 5 $ aj mesačný počet hľadaní, limit behu platí, útrata sa pripočíta do mesiaca. Zapísané v `docs/decisions.md`, test.
- 5 záznamov vo `venues.json` (adresy z webov, súradnice OSM, zatváracie časy z webov, `description: null`).
- Testy: `pytest -q` **721 passed**, 3 skipped (nové `tests/test_venues_089.py`, 17 testov; pribudli fixtures stránok 2 a 4 Kampusu).

### Rozhodnuté samostatne (v `docs/decisions.md`)
- Podtitul 007 a „Druh akce“ Kampusu do existujúceho `sources[].section` – bez nového poľa (dátový model sa nemení).
- Kampus: karta nemá rok → odhad, ktorý nahradí úplný dátum z detailu; viacdňová karta = jedna akcia v prvý deň (pravidlo 085); z každej stránky sa berie len zoznam s vlastným odkazom stránkovania (na stránkach 2+ sú kombinované odkazy iného zoznamu – opravené pred commitom).
- OX Club: čas aj z hlavičky „28. 11. 2026 | 23:00–04:30“ a z riadku len s časom („🕘 21:00–02:00“), keď text nemá „Start:“.
- `size` pri `capacity: null` je návrh (Café V Lese small, OX Club large podľa tretích strán, Kampus small); Karlovy Lázně 1000 → medium ako Lucerna (hranica medium/large).
- Café V Lese obrázok miesta = prvá fotka galérie na titulke (`/2022/05/1.jpg`, 1920×1440) – og:image chýba, fotky pozadia sú na výšku. Neprezeral som ju.
- Jednorazovo `ai_budget_usd = 1.00`, `ignore_monthly_cap = true`, `enrich_timeout_s = 2400`.

### Čísla (beh **45024287597**, success, `events.json` vygenerovaný 2026-11-22 14:16)
Príkaz: stiahnuť `events.json` a `pipeline_state.json` z Pages (adresa `PREVIOUS_EVENTS_URL` v `daily.yml`) do `<dir>` (state ako `state.json`), potom `python docs/tasks/089/nums089.py <dir> 2026-11-22`.

| Miesto | Akcií | Čas začiatku | Otvorenie | Cena (`price`) | z toho zo zdroja | `image_url` | náhľad | Vypredané |
|---|---|---|---|---|---|---|---|---|
| Karlovy Lázně | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0 |
| Café V Lese | 45 | 45 | 0 | 23 (AI) | 0 | 45 | 45 | 0 |
| Klub 007 Strahov | 33 | 33 | 0 | 18 | 12 | 33 | 33 | 0 |
| OX Club Prague | 8 | 7 | 3 | 2 | 1 | 8 | 8 | 0 |
| Kampus Hybernská | 63 | 63 | 0 | 63 | 63 | 62 | 60 | 0 |

- Spolu **848** akcií (pred úlohou 696). Všetky nové miesta majú `image_card` (upozornenie `venue-image` nevzniklo), `first_loaded` = 2026-11-22 (ich akcie nie sú „Nové“).
- Karlovy Lázně = 3, lebo výpis má len aktuálny týždeň (dnes nedeľa: 21.–22. 11.) + NYE; od pondelka pribudne nový týždeň.
- Kampus: adaptér 64, v `events.json` 63; 1 akcia bez obrázka (Current Issues in Archeology – detail nemá og:image), 2 náhľady sa nevytvorili.
- Vyradené (log): OX Club 1× PRIVATE EVENT (27. 11.).
- AI: v tomto behu doplnených **150** akcií (`enrich_ai: window=838 cached=688 enriched=150 errors=0 searches=365`); s `checked_at` 2026-11-22 spolu 321 (vrátane ranného behu 086), opakované hľadanie 2, **čaká 1**. Cena behu **0,76 $** (limit 1,00 $; mesiac pred behom 4,07 $, log „month limit ignored for this run“), za november **4,84 $ z 5 $**, hľadaní 2642; zostatok DeepSeek **1,95 $**.

### Overenie na webe (2026-11-22, stránky stiahnuté počas úlohy)
| Miesto | URL | Web | `events.json` |
|---|---|---|---|
| Karlovy Lázně | karlovylazne.cz/events (Sunday Shakedown) | 22. November 2026, 22:00 | 2026-11-22 22:00 ✔ |
| Karlovy Lázně | karlovylazne.cz/udalosti/nye-2026 | 31. December 2026, 20:00 | 2026-12-31 20:00 ✔ |
| Café V Lese | cafevlese.cz/events/the-veils-nz/ | JSON-LD 2026-11-22, 19:30 | 2026-11-22 19:30 ✔ (cena 490 Kč doplnila AI) |
| Café V Lese | cafevlese.cz/events/chloe-slater-uk/ | 2026-12-02T19:30:00+00:00 | 2026-12-02 19:30 ✔ |
| Klub 007 | klub007strahov.cz/events/astro-zombies-fr-kungpao-cowboys-cz/ | 2026-12-3T19:00+1:00 – 22:00, „psychobilly“ | 2026-12-03 19:00–22:00 ✔ |
| Klub 007 | klub007strahov.cz/events/lakome-barky-cz-cantina-cz/ | 26. 11. 19:00, „Vstupné 300 Kč“ | ✔ |
| OX Club | oxclubprague.com/shop/b1058-Diana-Arbenina.htm | 22. 11. 2026, Doors 19:00, Start 20:00 | doors 19:00, start 20:00 ✔ |
| OX Club | oxclubprague.com/shop/b1089-ALENA-OMARGALIEVA.htm | 10/04/2027, Otevření dveří 18:30, Začátek 19:30, od 1 100 Kč | ✔ |
| Kampus | kampushybernska.cz/program/hyb4-hudba-pio-plays-coltranes-ascension | 4. 12. 2026, 20:00–22:00, 250 Kč předprodej / 300 Kč na místě, Hudba | ✔ |
| Kampus | kampushybernska.cz/program/uterni-otevrena-sici-dilna-3 | 24. 11., 16:00–18:00, 300 Kč, D.1 Ateliér | ✔ |

### Návrh štítkov (na schválenie Matejom, už vo `venues.json`)
| Miesto | `type` | `character` | `music` | `size` (kapacita) | `closing` | Ukážky akcií |
|---|---|---|---|---|---|---|
| Karlovy Lázně | dance-club | tourist, commercial, late-night | pop, oldies, latin, edm | medium (1000) | Ne–Št 04:00, Pi–So 05:00 (web) | Monday Mania, Twisted Tuesday, Student Tuesdays, Wild Wednesday, Thursday Thunder, 5 Story Friday, 5 Story Saturday, NYE 2026 |
| Café V Lese | concert-club, bar | alternative | indie, punk, post-punk, rock | small (null) | Po–So 02:00, Ne 00:00 (web) | The Veils (NZ), Black holes + THE QUEUES, Widowspeak (US), Chloe Slater (UK), The Wants (USA), Orion (křest alba), PEXESO (křest EP) |
| Klub 007 Strahov | concert-club | underground, diy, student, alternative | punk, hardcore, metal, ska, rock | small (180) | Ne–Št 00:00, Pi–So 01:00 (web) | ULIANA DEL REI, PUNISHABLE ACT, ASTRO ZOMBIES, GREEN SMÅTROLL, VÁNOČNÍ SKAPARÁDA!, PALE DEATH + INGROWING, THE MEFFS, COLOUR HAZE |
| OX Club Prague | dance-club, concert-club | commercial, late-night | pop, house, edm, rock | large (null; 3. strany 1000/1200) | Pi, So 05:00 (web) | Diana Arbenina, SEPAR oficiální afterparty, EARTH – narozeniny, NYE 2026 – Cabaret Edition, Maniak live, Shrek Rave, Alena Omargalieva, Sound of Ibiza |
| Kampus Hybernská | culture-center | community, student, art-space | jazz, experimental, world | small (null) | null | HYB4 Hudba: PIO plays Coltrane’s Ascension, HYB4 Film: Obsession, HYB4 Čítárna, Úterní otevřená šicí dílna, Vědec z NASA a meziplanetární cestování, International Středa, Konference Dějiny ve veřejném prostoru |

Pozn.: `character` sa dedí na akcie. Kampus podľa AI: 25 talk, 20 workshop, 12 concert, 4 performance, 3 film, 3 theatre.

### Chýbajúce údaje pre Mateja
- **Kapacity:** Café V Lese, OX Club (web nemá; tretie strany 1000 / 1200), Kampus Hybernská.
- **Obrázky miesta na výmenu:** Klub 007 (FB grafika 1200×630), Kampus (grafika hyb4 2400×1260), Café V Lese (fotka galérie – neprezeraná).
- **IG Klubu 007** nezistený. **Closing Kampusu** null.

### Snímka
`docs/tasks/089/events-new-venues.jpg` (Akcie, Kedykoľvek, `events.json` z Pages obmedzený na 5 nových miest, 390 × 844; `tests/playwright/screenshots-089.spec.ts`, spustené z `web/` s `NODE_PATH=web/node_modules`). Neprezeral som ju.

### Otvorené
- Mesačný rozpočet: po behu 4,84 $ z 5 $ → denné behy doplnia do konca novembra AI len za ~0,16 $.
- Log `enrich_ai` pri ignorovanom limite píše `month=2642/1000000000` (kozmetické).
- Kampus má zrušenie len v názve („Ped Jams - ZRUŠENO“) – rieši to všeobecné pravidlo pipeline, adaptér nič neupravuje; neoverené.
- Café V Lese: čas 19:30 je pri všetkých 45 akciách (zrejme predvolený na webe – berie sa podľa rozhodnutia Mateja).
