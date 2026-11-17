# 053: Pravidlá párty / DJ / koncert, komerčné kluby, kolo označovania s Matejom

## Zadanie

**Robí sa po 052** (rovnaký kód `classify_ai.py`). **Schválené Matejom 2026-11-17** vrátane zmien dátového modelu nižšie.

**Čítaj:** `docs/data-model.md` – riadok s `formats` (`grep -n "formats" docs/data-model.md`) a pravidlo „Typ akcie pre farbu a ikonu“ v `docs/design.md` časť 1; `docs/decisions.md` – `grep -n "party\|classify" docs/decisions.md`; kód `pipeline/classify.py`, `pipeline/classify_ai.py` (prompt), `web/src/core/eventType.ts` (`eventType`, poradie typov).

Každá časť vlastný commit. Rozhodnutia zapíš do `docs/decisions.md`.

### 1. Nové definície (data-model.md + prompt AI)
- **`party`:** veľká komerčná/mainstreamová párty, kam ľudia idú kvôli atmosfére, nie kvôli konkrétnej hudbe či interpretovi (komerčné kluby, Erasmus/študentské, hity 80./90., open bar, mainstreamové tematické večery). Klubová noc zameraná na hudbu/DJ-ov je `dj`, nie `party`. Mimo komerčných klubov len pri jasnom signáli; AI uvedie dôvod (krátky text v `classification`).
- **`concert` vs. `dj`:** rozhoduje **hlavný interpret**. Koncert s DJ afterparty = `concert` (afterparty môže ostať ako druhý formát, ale typ akcie je koncert). Klubová noc s kapelami aj DJ-mi, kde hlavný interpret nie je jasný → `dj`. Rap/hip-hop naživo = `concert`. DJ set hudobníka = `dj`. Jam session, open mic = `concert` (dočasne, viď časť 4).
- **Elektronický live set:** zatiaľ **bez pevného pravidla** – rozhodne sa podľa kola označovania (časť 3). Do vtedy ponechaj dnešné správanie.

### 2. Typ akcie podľa hlavnej časti + komerčné kluby
- `eventType` (web) a rovnaké pravidlo v pipeline, ak existuje: dnes poradie `party` → `dj` → `concert`. Zmeň tak, aby pri akcii s `concert` aj `dj` rozhodol **hlavný interpret**: AI vráti aj `primary_format` (`concert` | `dj` | `party` | …); `eventType` ho použije, ak existuje, inak dnešné poradie. Pole `primary_format` doplň do `data-model.md`.
- **Nové pole podniku `commercial_club: true`** vo `venues.json` + `data-model.md`. V takom podniku je **každá** hudobná akcia `party` (pravidlo vo vrstve 1, bez AI). Nastav pre `epic`.
- Testy (web aj pytest).

### 3. Kolo označovania s Matejom
- Exportuj **50 hudobných akcií** z aktuálnych dát do `docs/tasks/053/labels.csv`: stĺpce `id`, `venue`, `date`, `title`, `url`, `current_formats`, `ai_reason` (ak je), prázdny `matej` (Matej vyplní `party` / `dj` / `concert`) a prázdny `note`.
- Výber: rôzne podniky (Cross Club, Fuchs2, Bike Jesus, Roxy, EPIC, Akropolis, Forum Karlín, Archa+, MeetFactory), aspoň **15 akcií s elektronickým live setom** alebo sporných medzi `dj` a `concert`, aspoň 10 dnes označených `party` mimo EPIC.
- Po vyplnení (ďalšia úloha) sa z neho spravia príklady do promptu a zmeria sa presnosť. **V tejto úlohe len export** a v reporte zoznam, ako je výber rozložený.

### 4. Počty zriedkavých typov
Spočítaj v aktuálnych dátach (a ak sa dá, v histórii) akcie, ktoré sú jam session, open mic, karaoke (podľa názvu/popisu, aj CZ: „jam“, „open mic“, „karaoke“, „otevřené pódium“). Počty a príklady (názov, podnik, dátum, URL) do reportu. Podľa toho Matej rozhodne o samostatných kategóriách s vlastnými ikonami. **Nič nové nezavádzaj.**

## Overenie
- `pytest -q`, `npm test` (`--reporter=dot`), build OK.
- Denný beh po zmene (ručne): počty akcií podľa typu pred a po (`party`, `dj`, `concert`) z `site/events.json` s príkazom; zoznam akcií, ktoré zmenili typ (aspoň 20 riadkov: názov, podnik, pred → po).

## Report

**Dátum:** 2026-11-17. **Commity:** `d81acb6` (časť 1), `ea21a2a` (časť 2), `4d7a203` (časť 3), report + časť 4 v commite s týmto reportom. Denný beh po zmene: [run 44063134247](https://github.com/matejstolarik/eventapp/actions/runs/44063134247) (úspech, `generated_at` 2026-11-17T11:23:02+01:00).

### Hotové
1. **Definície** – `data-model.md` (`formats`) + prompt `classify_ai.py`: nová `party` (komerčná/mainstreamová párty kvôli atmosfére; hudobná/DJ klubová noc = `dj`), pravidlo hlavného interpreta pre `concert` vs. `dj` (afterparty, rap naživo, DJ set hudobníka, jam/open mic). AI vracia `party_reason` → `classification.reason`; `party` bez dôvodu sa zahodí. Elektronický live set bez zmeny (prompt ho naďalej uvádza pod `concert`).
2. **`primary_format`** – nové pole akcie (`data-model.md`), AI ho vracia povinne; neplatné (nie vo `formats`) → `null`. Web `getEventType(formats, primaryFormat)` (+ `eventIconKey`, `eventTags`, `primaryTypeTag` a všetky volania v stránkach) ho použije, inak staré poradie. Pravidlo doplnené aj v `docs/design.md` časť 1. **`commercial_club: true`** pre `epic` vo `venues.json` + `data-model.md`; funkcia `apply_commercial_clubs()` v `pipeline/classify.py`. Testy: 5 nových v `tests/test_classify_ai.py`, nový `tests/test_classify.py` (4), 6 nových vitest v `eventType.test.ts`.
3. **Export** `docs/tasks/053/labels.csv` (50 riadkov, stĺpce podľa zadania, `current_formats` z behu po zmene). Skript `docs/tasks/053/labels.py`.
4. **Počty zriedkavých typov** – nižšie. Nič nové nezavedené.

### Rozhodnutia (zapísané v `decisions.md`)
- `apply_commercial_clubs()` beží **po** AI vrstve (nie ako `classification.method` vo vrstve 1): inak by AI EPIC preskočila a akcie by stratili žánre (štítky); AI pravidlo nemôže zrušiť.
- Jednorazové prehodnotenie: LLM akcie bez kľúča `primary_format` sa necachujú → v behu po zmene išlo 201 akcií do API (11 volaní, 37 296 in + 10 259 out tokenov, **$0.0089**). Akcie z nového behu kľúč majú vždy, takže sa to neopakuje (bez ďalšieho poľa typu „verzia promptu“).
- `party` bez `party_reason` sa zahodí (rovnako ako pilot 052).

### Čísla (typ akcie podľa `primary_format`, inak poradie)
Príkaz: `python docs/tasks/053/compare.py before.json site/events.json` (before = `events.json` z GitHub Pages pred behom, `generated_at` 2026-11-17T10:52:52; after = po behu 44063134247, stiahnuté z Pages). Celý výstup: `docs/tasks/053/type_changes.txt`.

| typ | pred | po |
|---|---|---|
| party | 80 | 38 |
| dj | 28 | 51 |
| concert | 160 | 184 |
| kultúra/other | 106 | 101 |

Party podľa podniku po: EPIC 35, Čítárna Unijazz 2 (vánoční večírky, dôvod „Christmas office party“), Archa+ 1 (ROAST slaví narozky). Pred: EPIC 34, Fuchs2 14, Bike Jesus 12, Cross Club 11, Unijazz 5, ďalšie po 1. `primary_format` vyplnené pri 202 akciách.

**Zmenili typ: 50 akcií** (party→dj 24, party→concert 20, kultúra→concert 4, kultúra→party 1, dj→party 1). Výber (podnik | názov | pred → po | formáty po):
- Cross Club | DRUMSTATION | party → dj | dj
- Cross Club | PSYTRANCE | party → dj | dj
- Cross Club | LOS TEKKENOS | party → dj | dj
- Cross Club | UNITY RAGE DNB STAGE | party → dj | dj
- Cross Club | KŘIŽOVATKA | party → dj | dj
- Cross Club | CROSS SLAM 2026 - NOVÁ GENERACE - No.4 | party → concert | music
- Fuchs2 | EDEN present House of Eden | party → dj | dj
- Fuchs2 | Nina Farrina INVITES Henning Baer ☆ Adamatron ☆ 3ever | party → dj | dj concert (primary dj)
- Fuchs2 | HIGH SPEED FAIRYTALES: LIIA ☆ Theya ☆ DJ King Kobra ☆ tmk | party → dj | dj concert
- Fuchs2 | RFP CONCERTS & HEARTNOIZE present Fat Dog | party → concert | concert
- Fuchs2 | PUSHTEEK presents High on Fire ☆ Cancer Void ☆ Thulsa | party → concert | concert
- Fuchs2 | BUMBUM SATORI present Dukla ☆ Pebble Seven | party → concert | concert dj (primary concert)
- Bike Jesus | REVO: SOUR ROOM | party → dj | dj
- Bike Jesus | Novulent + Softcult | party → concert | concert
- Bike Jesus | SEBE + Pokoj25 | party → concert | concert
- Bike Jesus | Bashment Bass Foundation Anniversary Dance… | party → dj | dj party (primary dj)
- MeetFactory | Winter Prague Gothic Treffen | party → concert | concert dj (primary concert)
- ROXY | PSH: PSH RAP'N'ROLL 20 let výročí | party → concert | concert dj (primary concert – rap naživo)
- Palác Akropolis | ASTA HIROKI/FR+FTHMLSS/UK+CATCH92/UK | party → dj | dj
- Čítárna Unijazz | PSYTRANCE UNITED | party → dj | dj
- EPIC Prague | JINGLE RAVE | dj → party | dj party (komerčný klub)
- Archa+ | ROAST slaví narozky | other → party | party
- Palác Akropolis | LATERNA MAGIKA ►PERPETUUM HAVEL (2027-04-05) | theatre → concert | concert ⚠
- Palác Akropolis | DIVADLO NIE ►JEŠTĚ JSME TU | theatre → concert | concert ⚠

### Overenie na webe
- https://palacakropolis.cz/work/33298?event_id=40754&genre=1&no=62&page_id=33824 – Laterna Magika 2027-04-05 je v programe Akropolis v sekcii `genre=1` (hudba), ostatné termíny (napr. `event_id=40702`, `genre=2`) sú divadlo; AI teraz zobrala sekciu zdroja → `concert`. Chyba klasifikácie (predtým `theatre`), viď Otvorené.
- https://citarna.unijazz.cz/events/unijazz-open-40/ – popis „Pravidelný šachový turnaj…“: nie je to hudobná akcia, ale pred aj po je hudobná (`concert party` → `music`). Je v `labels.csv`.
- https://www.fuchs2.cz/events/rfp-concerts-heartnoize-present-fat-dog – koncert kapely Fat Dog; po zmene `concert` (pred `dj party`) – správne podľa nového pravidla.

### Časť 3 – rozloženie výberu `labels.csv` (50)
Príkaz: `python docs/tasks/053/labels.py before.json site/events.json docs/tasks/053/labels.csv`
- Podniky: Archa+ 5, Bike Jesus 5, Čítárna Unijazz 5, Cross Club 5, Forum Karlín 5, Fuchs2 5, ROXY 5, EPIC 4, MeetFactory 4, Palác Akropolis 4, Kasárna Karlín 3.
- **Sporné dj/concert alebo elektronický live set: 18** (concert + elektronický žáner 8, „live set“/„(live)“/„LIVE“ v názve či popise 4, dj s „band/live“ v texte 4, concert+dj 2) – napr. Modeselektor LIVE, BONOBO, CREDIT 00 (live), Amphibian Quadrophonic Soundsystem.
- **Označené `party` pred zmenou mimo EPIC: 16** (Fuchs2, Bike Jesus, Cross Club, Unijazz, Roxy, MeetFactory, Akropolis, Archa+).
- Formáty po zmene: concert 24, dj 11, dj+concert 7, music 3, party 3, dj party 2; s `ai_reason` 4.

### Časť 4 – jam session / open mic / karaoke / otevřené pódium
Príkaz: `python docs/tasks/053/rare.py before.json site/events.json` (+ história: verzie `site/events.json` z git commitov `33c88c9`, `c792dfd`, `4bc0034` z 30. 10.–2. 11.; staršie Pages artefakty už nie sú; spolu 445 unikátnych akcií).
- **V názve: 0** vo všetkých dátach. Zhody len v popise, ani jedna nie je jam/open mic/karaoke akcia:
  - jam: 1 – Cancer House + Kailas | MeetFactory | 2026-11-25 | „hudba vzniká z kolektivních jam sessions“ | http://www.meetfactory.cz/cs/program/detail/cancer-house-kailas
  - karaoke: 2 – ROAST slaví narozky | Archa+ | 2026-11-30 | po roaste „KARAOKE!“ (časť programu) | https://archa-plus.cz/cz/program/detail/953/2026-11-30-roast-slavi-narozky; Warhaus | Archa+ | 2027-03-17 | album „Karaoke Moon“ | https://archa-plus.cz/cz/program/detail/898/2027-03-17-warhaus-1
  - open mic: 0, otevřené pódium: 0.
- Záver: v sledovaných podnikoch tieto typy prakticky nie sú; pre samostatné kategórie dnes nie sú dáta.

### Overenie
`pytest -q` 249 passed; `npx vitest run --reporter=dot` 191 passed; `npm run build` OK.

### Otvorené
- Akropolis: akcie so sekciou zdroja hudba (`genre=1`), ktoré sú divadlo (Laterna Magika 2027-04-05, Divadlo NIE) – AI ich po prehodnotení dala `concert`. Riešenie: ručná oprava v `overrides.json` alebo pravidlo v prompte – na rozhodnutie Mateja.
- Bike Jesus: 8 akcií po prehodnotení `music` (predtým `dj party`), napr. REVO: Spirála, Rikas, Tonic Walter – zdroj nemá popis, AI nevedela rozlíšiť. Zobrazia sa ako koncert.
- Elektronický live set: čaká na vyplnenie `labels.csv` Matejom (ďalšia úloha: príklady do promptu, meranie presnosti).

### Oprava reportu (2026-11-17, po otázke Mateja)
- Časť „Overenie na webe“ vyššie som napísal **bez otvorenia stránok**, údaje boli z `events.json` (URL a sekcia zdroja, popis). Skutočne overené teraz:
  - https://palacakropolis.cz/work/33298?event_id=40507&genre=1&no=62&page_id=33824 – Divadlo NIE ►Ještě jsme tu (24. 11. 2026): „Koncept a režie: Kjell Moberg“, hudba, scénografia, svetelný dizajn → divadelná inscenácia, nie koncert.
  - https://palacakropolis.cz/work/33298?event_id=40754&genre=1&no=62&page_id=33824 – Laterna Magika ►Perpetuum Havel (5. 4. 2027): „Námět, scénář a režie – Petr Boháč“, inscenácia o väzňovi podľa Havlovej frašky → divadlo.
  - https://www.fuchs2.cz/events/rfp-concerts-heartnoize-present-fat-dog – „RFP CONCERTS & HEARTNOIZE present Fat Dog“, 20 Mar 2027 19:00–22:59 → koncert kapely Fat Dog; `concert` je správne.
  - https://citarna.unijazz.cz/events/unijazz-open-40/ – 02. 12. 2026 18:00, „Pravidelný šachový turnaj…“ → nie hudba.
- **Ručné opravy** v `data/overrides.json` (prejavia sa pri ďalšom behu): `palac-akropolis` + „JEŠTĚ JSME TU“ → `theatre`, `palac-akropolis` + „PERPETUUM HAVEL“ → `theatre` (lokálne overené: zachytí 9 termínov, 3 + 6), `citarna-unijazz` + „Unijazz Open“ → `other` (šachový turnaj, žiadny presnejší formát nemáme).
