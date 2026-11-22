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
