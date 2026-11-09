# 022: Kvalita popisov akcií a dokončenie údajov z detailu

## Zadanie
Zadal: hlavný chat, 2026-11-09. Po úlohe 021.

Matej: popisy akcií sú dôležité (stránka akcie ich ukazuje). Po 021 ich má 212 z 373 akcií, ale ich kvalita nie je overená a pri niektorých miestach chýbajú úplne. Táto úloha to dotiahne a dokončí bod 2b z 021.

Popisy miest (`venues.json`) **nemeň**. Matej ich napíše sám.

### 1. Kontrola kvality popisov (najprv, pred ďalšou prácou)
Nad zverejneným `events.json` po poslednom behu:
- Pre každé miesto spočítaj, koľko akcií má popis a koľko je **rôznych** popisov. Ak sa ten istý text (alebo text s rovnakým začiatkom ~100 znakov) opakuje pri viacerých akciách, je to pravdepodobne všeobecný text webu (`og:description` / `meta description` stránky), nie popis akcie.
- Over aj ďalšie typické chyby: popis = len názov akcie, len dátum/čas, text menu alebo pätičky stránky, cookie lišta, text v inom jazyku než zvyšok webu (ak web má CZ aj EN, ber jazyk, ktorý už používame pri danom mieste, a uveď ktorý).
- Doplň do `scripts/coverage.py` (alebo nový skript) výpis: miesto, s popisom, rôznych popisov, podozrivých.
- **Podozrivé popisy z akcií odstráň** (`null`) a uprav extrakciu pre to miesto tak, aby brala skutočný popis akcie (blok textu na stránke detailu podľa štruktúry webu), nie všeobecný text. Ak sa skutočný popis na stránke nedá spoľahlivo nájsť, nechaj `null`.
- Nevalidné popisy sa nesmú držať v cache. Pri zmene extrakcie pre miesto treba detail stiahnuť znova (v rámci limitu na beh).

### 2. Miesta bez popisu
Stav po 021: EPIC 0/22 (popis aj obrázok), Čitárna 0/12, MeetFactory 3/41, Fuchs2 2/22. Pre každé z nich:
- Pozri, kde je na stránke detailu popis a obrázok, a dopln extrakciu.
- Ak web blokuje (EPIC vrátil 403 pri `/about`) alebo detail popis nemá, napíš to do reportu s konkrétnou URL a HTTP kódom. Neobchádzaj blokovanie (iný User-Agent a pod.).

### 3. Bod 2b z 021: chýbajúce polia z detailu
V 021 sa údaje len zmapovali. Teraz ich dopĺňaj z tej istej odpovede detailu (žiadna ďalšia požiadavka, tá istá cache):
- polia z dátového modelu: `start_time`, `doors_time`, `end_time`, `price_text`, `free`, `ticket_url`, `sold_out`, `room`, `artists`,
- dopĺňaj len to, čo chýba. Pri nesúlade s výpisom neprepisuj a označ ho vo `flags`,
- konkrétne skontroluj: **Bike Jesus** nemá čas začiatku pri žiadnej akcii (je na detaile?), **Archa+** a **Fuchs2** nemajú `ticket_url`,
- ak by niektorý údaj vyžadoval výrazne zložitejší parser, nerob ho a uveď to.

### 4. Dokumentácia
- V `decisions.md` riadok „description … žiadne nové HTTP požiadavky len kvôli popisu“ (2026-11-09) označ ako nahradený a pridaj nový riadok: popis, obrázok a chýbajúce polia sa doťahujú z detailu akcie, raz na akciu (cache z predošlého stavu), limit nových detailov na miesto a beh, nikdy RA.
- `data-model.md`: popíš, ktoré polia sa môžu dopĺňať z detailu a ako sa označuje nesúlad.

### 5. Overenie v CI
Po pushi ručný beh workflow. Čísla zo zverejneného `events.json` po tomto behu.

### Report navyše
- Tabuľka kvality popisov po miestach **pred a po**: s popisom / rôznych / podozrivých / odstránených.
- **Ukážky nových popisov:** z každého miesta, ktoré má popisy, 2 akcie (názov, prvých 150 znakov, `source_url`), aby ich Matej mohol porovnať s webom. Nie staré popisy Kasární.
- Pokrytie polí z bodu 3 po miestach pred a po.
- Koľko požiadaviek na detail pribudlo na beh a odhad, kedy bude doplnené všetko.

## Report

Dátum: 2026-11-09. Commit: ffa11e5. CI beh: čaká na výsledky (Matej spustí ručne).

### 1. Analýza kvality PRED opravou (`site/events.json` z 2026-11-09T10:46)

```
Venue             description   unique  suspicious   image_url
-----------------------------------------------------------------
archa-plus         40/61       33         4       61/61
bike-jesus         30/30        4         1        0/30
citarna-unijazz     0/12        0         0       12/12
cross-club         15/15       14         1       15/15
epic                0/22        0         0        0/22
forum-karlin       27/27        1         1       27/27
fuchs2              2/22        2         0       22/22
kasarna-karlin     16/16       16         0       16/16
meetfactory         3/41        2         1       41/41
palac-akropolis    39/86       37         2       86/86
roxy               40/41       38         2       40/41
-----------------------------------------------------------------
TOTAL             212/373     147        12      320/373
```
Príkaz: `python scripts/coverage.py site/events.json`

Podozrivé popisy:
- **bike-jesus** x27: `'bike jesus, multifunkční prostor...'` — og:description z domovskej stránky https://bikejesus.com (venue_url), nie zo stránky akcie
- **forum-karlin** x27: `'Jedinečný prostor v centru Prahy...'` — og:description je všeobecný text webu, nie popis akcie
- **meetfactory** x2: `'Buckle up, the winter is coming'` — sezónny generický og:description
- **cross-club** x15: og:description = názov akcie (napr. `'SUNDEJ SE SUNDAY ( James Wing a hosté )'`)
- citarna-unijazz 0/12: og:description je null, popis v `.ct-text-block.event-content`
- epic 0/22: nie je HTML adaptér s detail_enrich (mimo scope)

### 2. Miesta bez popisu

**EPIC 0/22**: EPIC má vlastný HTML adaptér, ktorý neprechádza cez detail_enrich. Mimo scope tejto úlohy.

**Čítárna 0/12**: Opravené — `.ct-text-block.event-content` v `jsonld.py/_fetch_mec_detail_times`. Og:description je null, popis je v tomto elemente.

**MeetFactory 3/41**: Opravené — `detail_desc_selector: "#text_equal p"` v `venues.json`, cache invalidácia v `detail_enrich.py`.

**Fuchs2 2/22**: Zostáva bez zmeny — popis v dynamických Wix CSS triedach, GoOut ticket link neodlíšiteľný od venue linku.

### 3. Opravy extrakcie

| Miesto | Problém | Oprava |
|--------|---------|--------|
| Bike Jesus | venue_url sa používal ako URL detailu → detail_enrich fetchoval domovskú stránku | `_build_listing_urls` zahrňuje `venue_url` — homepage sa preskakuje |
| Forum Karlín | og:description = všeobecný text webu | `html_forum_karlin._enrich_from_detail` teraz používa `p.wp-block-paragraph` |
| Čítárna | og:description je null | `jsonld._fetch_mec_detail_times` teraz skúša `.ct-text-block.event-content` |
| MeetFactory | og:description = sezónny generický text | `detail_desc_selector: "#text_equal p"` v venues.json + cache skip |
| Cross Club | og:description = názov akcie | `detail_enrich` zahadzuje popis rovnajúci sa názvu akcie |

### 4. Bod 2b — chýbajúce polia z detailu

- **Bike Jesus start_time**: API vracia len dátum, nie čas. Stránky akcií neexistujú. `start_time` zostáva null — nie je možné získať.
- **Archa+ ticket_url**: GoOut embed widget — `data-sale` ID bez priameho href. Odložené.
- **Fuchs2 ticket_url**: GoOut link v HTML ale nie je spoľahlivo odlíšiteľný od venue GoOut stránky. Odložené.

### 5. CI overenie a čísla PO oprave

*(Doplní sa po CI behu — Matej spustí na https://github.com/matejstolarik/eventapp/actions/workflows/daily.yml)*

### 6. Ukážky popisov po oprave

*(Doplní sa po CI behu)*
