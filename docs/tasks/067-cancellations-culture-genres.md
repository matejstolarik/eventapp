# 067: Zrušené a presunuté akcie vo všetkých zdrojoch, žánre filmov a divadla

## Zadanie

**Schválené Matejom 2026-11-18.** Dôvod: zrušená akcia ukázaná ako bežná je najhoršia chyba pre dôveru v appku (Omah Lay 18. 11.). 066 zistila, že zrušenie vôbec nerozpoznávajú Archa+, Roxy, EPIC, Bike Jesus (API) a Cross Club (RSS); JSON-LD (MeetFactory, Kasárna, Unijazz, Fuchs2) len `eventStatus` s „cancel“; presun takmer nikto. Druhá časť: filmy (a divadlo, tanec) nemajú žánre, lebo pri prieskume (062) bol zoznam filmových žánrov prázdny a prieskum žánrové fakty nezbieral (`genre_facts: {}`, napr. Ratatouille) – 065 nemala čo premapovať.

**Čítaj:** report 066 časť 1 (zoznam slepých miest); `docs/data-model.md` (`status`, `sold_out`, Quality checks); `pipeline/detail_enrich.py` (limit 40, detail sa znova nesťahuje, kým sa nezmení URL), adaptéry `html_archa.py`, `html_roxy.py`, `html_epic.py`, `api.py` (Bike Jesus), `rss.py` (Cross Club), `jsonld.py`, `html_akropolis.py` (kód 6 = presun), `html_forum_karlin.py` (vzor z 066); `pipeline/enrich_ai.py` + `research_store.py` (opätovný prieskum podľa id); `docs/decisions.md` (`grep -n "cancel\|postpon\|status"`).

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`.

### 1. Rozpoznanie zrušenia a presunu
- **Spoločná kontrola textu** (jedna funkcia pre všetky zdroje, nie kopírovanie do adaptérov): názov akcie a text karty/stránky akcie, ktorý už máme (zoznam, detail, RSS, API, JSON-LD), na výrazy zrušenia a presunu v CZ/SK/EN (`zrušeno`, `zrušen`, `ruší se`, `odpadá`, `cancelled`, `canceled`; `přesunuto`, `přeloženo`, `odloženo`, `postponed`, `rescheduled`, `nový termín`). Zrušené → `status: cancelled`; presunuté bez nového dátumu → `postponed` (prefix z názvu preč podľa `data-model.md`); presun s novým dátumom: zdroj väčšinou zmení dátum → ponechať, len zalogovať. Pozor na falošné zachytenie (napr. „zrušeno“ v popise inej akcie alebo vo vete „nic se neruší“, názov kapely) – kontrolovať len krátke označenia (prefix názvu, štítok, samostatný riadok/prvok), nie celý dlhý popis; testy na falošných prípadoch.
- **Metadáta:** JSON-LD `eventStatus` `EventCancelled` → cancelled, `EventPostponed` → postponed, `EventRescheduled` → zalogovať. Akropolis kód 6 → postponed (ak ide o presun bez dátumu; inak zalogovať).
- **Adaptéry so špecifickým označením** (ako Forum Karlín): pri Arche, Roxy, EPIC over na webe, či majú vlastnú triedu/štítok zrušenia (nájdi aspoň jednu zrušenú alebo presunutú akciu v archíve/programe, inak napíš, že si žiadnu nenašiel, a spoľahni sa na spoločnú kontrolu). Bike Jesus API a Cross Club RSS: aké polia/text majú.
- **Opätovná kontrola blízkych akcií:** zrušenie sa objaví neskôr na tej istej URL. Akcie v **najbližších 7 dňoch** (len tie, ktorých detail vôbec sťahujeme) skontrolovať znova raz za deň, aj keď sa URL nezmenila – v rámci limitu na podnik (napíš, o koľko požiadaviek viac to je). Pri Forum Karlín a podnikoch so zrušením v zozname stačí zoznam.
- `sold_out` (VYPRODÁNO v názve/štítku): over, že sa rozpoznáva rovnako všade, kde to zdroj uvádza (napr. Roxy „VYPRODÁNO COLORFACTORY“); prefix z názvu preč, ak to `data-model.md` tak určuje.
- Report: tabuľka podnik · čo rozpozná zrušenie · presun · vypredané · ako overené (URL zrušenej/presunutej akcie, ak sa našla).

### 2. Žánre filmov, divadla a tanca
- Opätovný **prieskum s hľadaním** (nie len rozhodnutie z uloženého prieskumu) pre akcie s formátom `film` v najbližších 60 dňoch (~12), s aktuálnym promptom (filmové žánre C9). Rozpočet **0,08 $**.
- Divadlo a tanec (`theatre`, `dance`, `performance` – ~60 akcií): **len ak zostatok DeepSeek pred spustením (over ako v 063) ≥ 1,00 $**, rozpočet 0,40 $. Inak preskoč a napíš to (Matej dobije kredit, spustí sa neskôr cez workflow – napíš príkaz/vstup).
- Over, že prompt pri kultúre naozaj žiada žánrové fakty (napr. „animovaný“, „dokumentární“, „činohra“), a že poistka ich pustí.
- Report: filmy pred → po (žánre), 3 overené na webe; počet divadelných/tanečných, ak sa robili.

### 3. Drobnosti
- Náhľad podniku Cross Club: `thumbs: cross-club — HTTP Error 404` (obrázok podniku vo `venues.json`) – nájsť platný obrázok z webu podniku alebo `null`.
- 2 neúplné PNG EPIC (`epic-2026-11-19-almost-weekend`, `epic-2026-12-13-sunday-rituals-urban-music`): skúsiť ešte raz pri ďalšom behu, pri opakovanej chybe záloha = obrázok zo zoznamu (620×360).

## Overenie a report
- `pytest -q`; číslo behu (príkaz).
- Čísla z `events.json` posledného behu: `cancelled` / `postponed` / `sold_out` po podnikoch (pred/po), filmy so žánrom, cena behu, zostatok kreditu.
- Ručne over na webe všetky akcie, ktoré dostali `cancelled` alebo `postponed` (URL + text).
- Otvorené body.

## Report

**Dátum:** 2026-11-18. **Commity:** `f5b51a0` (1. zrušenie / presun / vypredané), `b437541` (2. prompt pre žánre filmov a divadla), `3148b98` (3. obrázok Cross Club, záloha pri neúplnom obrázku), report v nasledujúcom commite. `pytest -q`: **621 passed**.

**Beh:** [44350551801](https://github.com/matejstolarik/eventapp/actions/runs/44350551801) (commit `3148b98`, `reenrich_ids` = 10 filmov v najbližších 60 dňoch, `ai_budget_usd=0.08`), úspešný a nasadený; `events.json` generated_at `2026-11-18T17:54:27+01:00`. „Pred“ = Pages pred behom, generated_at `2026-11-18T14:17:03+01:00` (beh 44310543609).

**Príkaz** (skript v scratchpade, nie v repe; `before.json` / `after.json` = `https://matejstolarik.github.io/eventapp/events.json` pred a po behu):
```
python stats067.py before.json after.json
```

### 1. Zrušenie a presun

Spoločná funkcia `pipeline/status_marks.py` (názov v `normalize.py`, štítky v adaptéroch, stránka akcie v `detail_enrich.py`). Kontrolujú sa len krátke označenia: prefix/prípona názvu, štítok alebo samostatný riadok ≤ 40 znakov, ktorý je celý označením, a schema.org (`eventStatus`, `offers.availability: SoldOut`). Testy falošných prípadov (`tests/test_status_067.py`): „SPITFIRE COMPANY & PAST ►CANCEL“ (názov hry v Akropolise), „Postponed Dreams“, „Nic se neruší“, „Koncert je zrušen kvůli nemoci…“ (veta), „Zrušeno“ inej akcie ďaleko pod názvom („další akce“), „Odpadlíci“, „Sold Outsiders“. Názov so `ZRUŠENO`/`VYPRODÁNO` ostáva (data-model určuje odstránenie len pri presune); presun s dátumom, `nový termín` a `EventRescheduled` sa len logujú.

| podnik | zrušenie | presun | vypredané | ako overené |
|---|---|---|---|---|
| Forum Karlín | trieda `cancel`, riadok `ZRUŠENO` (066) + spoločná kontrola názvu | spoločná kontrola názvu | `.nalepka .msg` (066) | 066: Omah Lay, Enigma (stále `cancelled`) |
| Archa+ | **trieda `canceled` na `h2` v zozname** (nové) + štítky | štítky | `span.btn-soldout` + štítky | **Mat213 27. 11.** – `https://archa-plus.cz/cz/program/` (`<h2 class="goout-event-header canceled">`), detail `https://archa-plus.cz/cz/program/detail/791/2026-11-27-mat213-krest-desky-a-medley-nejvetsich-hitu` (`<span class="canceled">Zrušeno</span>`); fixtúry `tests/fixtures/archa_*canceled*` |
| Akropolis | kód 5 | **kód 6 → `postponed`** (nové; predtým len log) | kód 2 | v tomto behu žiadna akcia s kódom 6 |
| Roxy | spoločná kontrola názvu + stránky | **prvok `.postponed`** (nové) | **`VYPRODÁNO:` v názve** (nové) | `.postponed` len zo štýlov webu (`/css/cssloader-…css`: `.event-list .item .wrap .front .postponed`), presunutú akciu som nenašiel; vypredané: 3 akcie na `https://www.roxy.cz/club/` („VYPRODÁNO: COLORFACTORY / VOILÀ / ADDICT CLUB EDITION #2“) |
| EPIC | spoločná kontrola názvu + stránky | rovnako | rovnako | web nemá vlastné označenie (žiadna trieda v HTML ani v CSS); zrušenú akciu som nenašiel |
| Bike Jesus (API) | **`Subtitle`, `Tag` ako štítky** + názov | rovnako | rovnako | API má len `Title, Subtitle, Tag, Description, Tickets`, žiadne pole stavu; zrušenú akciu som nenašiel |
| Cross Club (RSS) | názov + stránka akcie | rovnako | rovnako | RSS má len `title` a prázdny `description`; zrušenú akciu som nenašiel |
| MeetFactory, Kasárna, Unijazz, Fuchs2 (JSON-LD) | `EventCancelled` + názov + stránka | **`EventPostponed`** (nové) + názov | **`SoldOut`** + stránka | Fuchs2 presun z názvu, MeetFactory/Fuchs2 vypredané zo stránky (nižšie) |

**Opätovná kontrola blízkych akcií:** akcie `scheduled` v najbližších 7 dňoch sa raz denne stiahnu znova (`pipeline_state.json` → `status_checked`), v rámci limitu 40 na podnik; okrem Forum Karlín, Archa+, Akropolis (stav zo zoznamu každý beh) a Bike Jesus (nemá stránky akcií). V behu `status_checks=39` → **39 požiadaviek denne navyše** (stav 18. 11.: Cross Club 9, Kasárna 7, EPIC 6, Roxy 5, MeetFactory 5, Unijazz 4, Fuchs2 2), `status_found=0`. Pred nasadením som rovnakú kontrolu pustil ručne na tých 39 stránkach: názov akcie sa našiel na všetkých, žiadne falošné zrušenie.

**Čísla (pred → po):**

| podnik | akcie | cancelled | postponed | sold_out |
|---|---|---|---|---|
| archa-plus | 60 → 60 | 0 → **1** | 0 → 0 | 2 → 2 |
| bike-jesus | 25 → 25 | 0 → 0 | 0 → 0 | 0 → 0 |
| citarna-unijazz | 16 → 16 | 0 → 0 | 0 → 0 | 0 → 0 |
| cross-club | 15 → 15 | 0 → 0 | 0 → 0 | 0 → 0 |
| epic | 35 → 35 | 0 → 0 | 0 → 0 | 0 → 0 |
| forum-karlin | 24 → 24 | 2 → 2 | 0 → 0 | 0 → 0 |
| fuchs2 | 20 → 21 | 0 → 0 | 1 → **2** | 0 → **1** |
| kasarna-karlin | 15 → 15 | 0 → 0 | 0 → 0 | 0 → 0 |
| meetfactory | 35 → 35 | 0 → 0 | 0 → 0 | 0 → **1** |
| palac-akropolis | 85 → 85 | 0 → 0 | 0 → 0 | 10 → 10 |
| roxy | 44 → 45 | 0 → 0 | 0 → 0 | 0 → **3** |
| **spolu** | 374 → 376 | 2 → 3 | 1 → 2 | 12 → 17 |

**Overenie na webe (2026-11-18 ~18:00), všetky `cancelled` / `postponed` a nové `sold_out`:**
- `archa-plus-2026-11-27-mat213-…` **cancelled** – URL vyššie, „Zrušeno“.
- `forum-karlin-2026-11-18-omah-lay`, `forum-karlin-2027-01-30-original-enigma-voices-symphonic` **cancelled** – z 066, nezmenené.
- `fuchs2-2026-12-31-floa-bert-and-friends-madhouse-express-anna-vaverkova` **postponed** – `https://www.fuchs2.cz/events/presunuto-floa-bert-and-friends-madhouse-express-anna-vaverkova`: nadpis „PŘESUNUTO / FLOA: Bert and Friends…“, text „TERMÍN JE PROVIZORNÍ, BUDE TEPRVE OZNÁMEN.“. Názov bez prefixu = „FLOA: Bert and Friends…“, preto **nové id** (staré `…-presunuto-floa-…` zmizlo; rovnako ako pri prefixe `POSTPONED:` od 017).
- `fuchs2-2026-12-31-debasement` **postponed** – `https://www.fuchs2.cz/events/postponed-debasement`: „POSTPONED: deBasement“ (už pred 067).
- `meetfactory-2026-11-27-live-nation-tiffany-day` **sold_out** – `http://www.meetfactory.cz/cs/program/detail/live-nation-tiffany-day`: riadok „Vyprodáno!“ (JSON-LD tam má `InStock`). Veta „Koncert byl přesunut ze SubZero“ sa správne nezobrala ako presun.
- `fuchs2-2026-12-03-f2-live-dusan-vlk-asthmaboy-again` **sold_out** – `https://www.fuchs2.cz/events/f2-live-dusan-vlk-asthmaboy-again`: riadok „SOLD OUT / VYPRODÁNO“.
- Roxy 3× **sold_out** – názvy „VYPRODÁNO: …“ na `https://www.roxy.cz/club/`.

### 2. Žánre filmov, divadla a tanca
- **Prompt:** výskumný prompt (DeepSeek aj Gemini) sa pri filme pýtal len na „interpretov“, nie na film. Doplnené: pri filme samotný film (réžia, rok, krajina) a žánre podľa zdrojov, pri divadle/tanci/performance žáner diela; nový riadok faktov `F: …`; pravidlo C3 v prompte uznáva fakt o filme/diele (`docs/ai-rules.md` A5 = vykonanie C5). Poistka `genre_supported` sa nemenila; `tests/test_culture_genres_067.py` overuje, že pustí „animated“, „animovaný“, „dokumentární“, „činohra“, „současný tanec“, „taneční divadlo“.
- **Filmy (10 v najbližších 60 dňoch): so žánrom 1 → 9.** Lola `drama`; The Danish Girl `drama, biography, romance`; Animaglajz `animation, documentary`; Shark Tale `animation, family, comedy, adventure`; The Stranger (2025) `drama, crime`; Ratatouille `animation, comedy`; We'll Kick Up a Fuss… `comedy`; The Simpsons Movie `animation, comedy, family`; Reeal Time 3 ostáva `experimental, animation`; Podzemnícka vianočná besídka (zmiešaný program) bez žánru.
- **Overené na webe:** Ratatouille – `https://kasarnakarlin.cz/en/program/2026/11/25/ratatouille` „As part of our Animated Classics series…“; The Danish Girl – zdroje výskumu AllMovie `https://www.allmovie.com/movie/the-danish-girl-am126747` a Wikipedia (film Toma Hoopera 2015, životopisná romantická dráma); Animaglajz – `https://kasarnakarlin.cz/en/program/2026/11/20/animaglajz-animations-from-sutnarka`: „animated work“ ✓, **`documentary` má slabú oporu** (stránka píše, že škola vedie študentov aj k „animated documentary“, nie že ho premietanie obsahuje).
- **Divadlo a tanec (39 akcií v 60 dňoch, 8 so žánrom): preskočené.** Zostatok DeepSeek pred spustením **0,35 $** (< 1,00 $), beh `deepseek-test.yml` mode `balance` [44349421369](https://github.com/matejstolarik/eventapp/actions/runs/44349421369). Po dobití: workflow `daily.yml`, `ai_budget_usd=0.40`, `reenrich_ids` = id akcií `theatre`/`dance`/`performance` v najbližších 60 dňoch, zoznam vypíše:
  ```
  python -c "import json,datetime as d;e=json.load(open('site/events.json',encoding='utf-8'))['events'];t=d.date.today();print(','.join(x['id'] for x in e if t<=d.date.fromisoformat(x['date'])<=t+d.timedelta(60) and set(x.get('formats') or [])&{'theatre','dance','performance'}))"
  ```
- **Cena behu:** AI doplnenie **$0.0599** (13 akcií = 10 filmov + 3 nové, 29 hľadaní), rozpočet behu $0.08; mesiac pred behom $1.3052. Zostatok kreditu odhadom **~0,29 $** (0,35 $ − 0,06 $; po behu neoverený cez API).

### 3. Drobnosti
- **Cross Club:** `og:image` webu (`/media/images/logo-fb.png`) vracia 404. Nový obrázok `https://www.crossclub.cz/files/2019/cervenec/cross.jpg` (535×277, fotka sály s logom, z novinky 1356 na webe klubu). V behu `thumbs: cross-club → site/img/venues/cross-club.jpg`, bez 404.
- **EPIC neúplné PNG:** obrázok sa skúsi stiahnuť dvakrát, pri druhej chybe sa použije obrázok zo zoznamu (`pipeline_state.json` → `detail_image[id].listing`). V behu obe zlyhali znova („image file is truncated“) → `epic-2026-11-19-almost-weekend` a `epic-2026-12-13-sunday-rituals-urban-music` majú teraz `image_url` 620×360 zo zoznamu a `image_thumb` aj `image_detail`. Veľký obrázok sa skúša každý beh znova (2 stiahnutia navyše na akciu).

### Rozhodnutia urobené samostatne
- Z názvu sa odstraňuje len prefix presunu (podľa `data-model.md`); `VYPRODÁNO:` / `ZRUŠENO:` v názve ostáva. Ak ich má appka skrývať, je to zmena dátového modelu (zmení id) – na rozhodnutie Mateja.
- Prefix bez oddeľovača („ODLOŽENO Blackout“) len veľkými písmenami, aby sa nebrali názvy kapiel.
- `offers.availability: InStock` sa neberie ako „lístky v predaji“ (CMS ho dáva predvolene, aj pri prázdnej cene); `SoldOut` áno.
- Akropolis kód 6 → `postponed` (nový riadok v `decisions.md` nahrádza „len zalogovať“ z 2026-11-02).
- Kontrola stránky hľadá označenie len v okolí riadkov s názvom akcie (8 pred, 15 za, max. 3 výskyty), nie na celej stránke.
- Obrázok podniku Cross Club vybraný z novinky na ich webe (iný obrázok sály som na webe nenašiel).

### Otvorené
- Divadlo, tanec, performance (39 akcií) – po dobití kreditu (príkaz vyššie).
- Roxy `.postponed`: overené len zo štýlov; ak presunutá akcia nemá `time.date`, adaptér ju nezaradí – overiť pri prvej presunutej akcii.
- EPIC, Bike Jesus, Cross Club: žiadna zrušená akcia na overenie, spoliehame sa na spoločnú kontrolu.
- `documentary` pri Animaglajz slabo podložený (možná ručná oprava v `manual.json`).
- Názvy „VYPRODÁNO: …“ (Roxy) a „ZRUŠENO …“ ostávajú v názve (viď rozhodnutia).
