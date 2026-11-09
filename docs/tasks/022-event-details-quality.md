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
