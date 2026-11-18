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
