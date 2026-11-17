# 063: Typ od AI pred kategóriou podniku, popis bez „nedostatku informácií“

## Zadanie

**Schválené Matejom 2026-11-17** po reporte 062. Rozhodnutia: `docs/ai-rules.md` B7 (typ od AI má prednosť pred kategóriou podniku) a F (popis prezentuje informácie, nikdy ich nedostatok; miesto a sála v popise povolené).

**Čítaj:** `docs/ai-rules.md` B7, F, H; report 062 (Časť 1, Otvorené); `pipeline/classify.py` (riadky s `"method": "source"`), `pipeline/classify_ai.py` (podmienka `method in ("manual", "source", "keyword")`), `pipeline/enrich_ai.py` (aplikácia `formats` a `genres` podľa `method`), `pipeline/ai_guards.py`, `pipeline/deepseek.py`; `docs/decisions.md` (`grep -n "062"`).

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`.

### 1. Typ od AI má prednosť pred zdrojom
- Dnes typ zo zdroja (`classification.method: source`, kategória podniku, napr. Roxy) a `keyword` blokuje AI typ (062: 63 akcií, Tinlicker ostal `dj`). Nové poradie: `manual` > AI (`formats` + `primary_format`) > `source` > `keyword`. Typ zo zdroja ostáva ako záloha, keď AI nič nevráti (napr. pravidlo H, rozpočet, výpadok).
- Žánre: bez zmeny (žánre zo stránky podniku majú prednosť ako doteraz).
- Akcie z 60 dní, ktoré už AI spracovala: použi uložené AI výsledky alebo rozhodnutie z uloženého prieskumu (`reenrich_from_research`), **bez nového hľadania**. Vyplniť aj chýbajúci `primary_format` (062: 70 akcií).
- `classify_ai` (nové akcie): rovnaké poradie.
- Testy: Tinlicker (zdroj `dj`, AI `concert`) → `concert`, `dj` doplnkový; `manual` prebije AI; AI bez výsledku → typ zo zdroja.
- Do reportu tabuľka všetkých akcií, kde sa typ zmenil: názov, miesto, dátum, typ zo zdroja → typ od AI (na Matejovu kontrolu).

### 2. Popis bez viet o nedostatku informácií
- Prompt podľa nového F: žiadne vety o tom, čo sa nenašlo, nie je známe, nebolo zverejnené/ohlásené, ani o tom, ako AI hľadala.
- Poistka v kóde (CZ, pred prekladom): **vymazať jednotlivé vety** o chýbajúcich informáciách, nie celý popis. Ak po vymazaní neostane nič použiteľné, akcia AI popis nemá (pravidlo H, `needs_review`). Zapísať do `dropped` (druh `description_no_info`).
- Testy na skutočných vetách: DIVA INVITES („O jednotlivých účinkujících se kromě jejich jmen … nedochovaly další podrobnosti, stejně jako informace o vydaných nahrávkách“), Text-appeal („Konkrétní účinkující pro tento večer nejsou zveřejněni.“), „Sedmé jméno zatím ohlášeno nebylo.“, REVO (celý popis o tom, že meno majú iní nesúvisiaci interpreti → žiadny popis). **Falošné zachytenie nesmie nastať:** Bonobo „…takže jeho vystoupení nejsou postavená na laptopu…“ ostáva.
- Existujúce dáta: nájdi všetky AI popisy v `events.json` s takými vetami (zoznam do reportu: akcia + vymazaná veta), oprav ich z uloženého prieskumu bez hľadania a SK/EN prelož znova z opraveného CZ.

### 3. Miesto v popise nie je na kontrolu
- Odstrániť `needs_review` za podnik/sálu v popise (062: 48 akcií). Poistka môže ostať len ako počítadlo v logu.

### Rozpočet
- Bez nového hľadania; celkom najviac 0,10 $ (kredit ~0,46 $). Pri HTTP 402 stop, beh pokračuje.

## Overenie a report
- `pytest -q` OK; číslo behu (denný workflow s `reenrich_from_research` alebo nový vstup).
- Čísla z `events.json` posledného behu (príkaz): akcie so zmeneným typom (z čoho na čo, súhrn), s `primary_format`, `needs_review` (pred 85 → po, podľa dôvodu), opravené popisy, akcie bez AI popisu, cena behu, zostatok kreditu.
- Ručne over 3 akcie so zmeneným typom na webe podniku a 3 opravené popisy (pôvodná veta → nový text).
- Otvorené body.

## Report

**Dátum:** 2026-11-17. **Stav: hotové (časti 1–3).**

**Commity:**
- `6a02be6` – časť 1 (typ od AI pred kategóriou podniku);
- `f7b3fc2` – časť 2 (popis bez viet o nedostatku informácií);
- `df62af9` – časť 3 (miesto v popise sa len počíta);
- `5a7a8fb` – oprava k časti 1: `classify_ai` necháva akcie v okne na `enrich_ai`; `primary_format` z prieskumu aj pri `manual`;
- report je v commite s týmto textom.

**Behy workflow (`daily.yml`, `reenrich_from_research` s id, bez hľadania):**
- beh 1: [44170861864](https://github.com/matejstolarik/eventapp/actions/runs/44170861864). Zoznam id: [`063/redo-run1.txt`](063/redo-run1.txt) – 34 akcií (13 s typom od AI iným ako zdroj + 23 s vetami o nedostatku informácií). `ai_budget_usd=0.10`, cena **$0.0304** (zaradenie $0.0025, rozhodnutie a preklad $0.0279).
- beh 2: [44172530495](https://github.com/matejstolarik/eventapp/actions/runs/44172530495). Zoznam id: [`063/redo-run2.txt`](063/redo-run2.txt) – 36 akcií, ktoré mali v cache ešte `needs_review` z 062 za miesto v popise. `ai_budget_usd=0.065`, cena **$0.0348**.
- zostatok (`deepseek-test.yml` mode `balance`): [44174167942](https://github.com/matejstolarik/eventapp/actions/runs/44174167942).
- Zoznamy id vytvoril `python docs/tasks/063/redo_ids.py events.json research/2026-11.json`. Zoznam pre beh 2 som vybral z výsledku behu 1 (akcie s `needs_review` a miestom v popise, ktoré beh 1 nespracoval).

`pytest -q`: **406 passed**. Nové testy: `tests/test_type_063.py`, `tests/test_no_info_063.py`. Upravené sú 3 staré testy, ktoré kódovali nahradené pravidlá (zdroj > AI pri type, `classify_ai` bez `source`/`keyword`, kontrola za miesto v popise).

### Časť 1 – typ od AI pred zdrojom
- **Poradie:** `manual` > AI > `source` > `keyword`.
  - `enrich_ai.apply_enrichment` aplikuje typ od AI pri všetkom okrem `manual`.
  - `classify_ai` posiela aj akcie so `source`/`keyword`. Kategóriu podniku dostane ako nápovedu (`Venue category`).
  - Keď AI typ nevráti, ostane typ zo zdroja (testy: prázdny výsledok, chyba providera).
- **Žánre bez zmeny:** žánre zo stránky podniku vyhrávajú ako doteraz. `main.py` určí tieto akcie (`venue_genre_ids`) ešte pred AI vrstvami, lebo `classify_ai` môže zmeniť `classification.method`.
- **Akcie v 60-dňovom okne so `source`/`keyword`** `classify_ai` neposiela. Typ im určí `enrich_ai` z prieskumu s webom. Inak by odhad bez webu prepísal typ akcií spracovaných pred 063 (tie nemajú typ od AI v cache).
- **Akcie spracované v 062 – bez nového hľadania:**
  - AI typ sa v 062 pri `source` neuložil. V uloženom prieskume je len `primary_format`.
  - Ak je uložený `primary_format` jedným z formátov zo zdroja (50 akcií, napr. divadlo v MeetFactory), doplní sa bez volania API (`fill_primary_from_research`).
  - Ak je iný (13 akcií), akcia išla na rozhodnutie z uloženého prieskumu (beh 1).
  - Formáty zo zdroja ostávajú pri tých 50 akciách nezmenené (doplnkové formáty od AI neboli uložené).
- **Testy:**
  - Tinlicker (zdroj `dj`, AI `concert`) → `concert`, `dj` doplnkový, aj z cache v ďalšom behu;
  - `manual` prebije AI;
  - AI bez výsledku / chyba → typ zo zdroja;
  - `keyword` → AI;
  - žánre podniku ostávajú;
  - `primary_format` z prieskumu.

**Akcie so zmeneným typom** (`events.json` pred 063 = beh 44156896473 → po behu 2; typ = `formats` (`primary_format`)) – na kontrolu Matejom:

| názov | miesto | dátum | zo zdroja | od AI | method |
|---|---|---|---|---|---|
| LẨU–VYPRÁVĚNÍ U JÍDLA | palac-akropolis | 2026-11-29 | theatre (None) | talk/performance (talk) | source → llm+web |
| LẨU–VYPRÁVĚNÍ U JÍDLA | palac-akropolis | 2026-11-30 | theatre (None) | performance/talk (performance) | source → llm+web |
| TANTEHORSE ►IRIS | palac-akropolis | 2026-12-01 | theatre (None) | comedy/theatre/music (comedy) | source → llm+web |
| AHMEDOVÁ, GEISLEROVÁ, DITTRICHOVÁ ►A BEZ POVÍ | palac-akropolis | 2026-12-08 | theatre (None) | performance (performance) | source → llm+web |
| MIŘENKA ČECHOVÁ & SPITFIRE COMPANY ►BALETKY | palac-akropolis | 2027-01-30 | theatre (None) | theatre/dance (theatre) | source → llm |
| LẨU–VYPRÁVĚNÍ U JÍDLA | palac-akropolis | 2027-02-20 | theatre (None) | talk (talk) | source → llm |
| THE MUSIC DIGEST (38) ►THE DEVIL'S TRADE+SKOT | palac-akropolis | 2026-11-23 | other (None) | talk (talk) | source → llm+web |
| THE MUSIC DIGEST (39) | palac-akropolis | 2026-12-15 | other (None) | talk (talk) | source → llm+web |
| Burkicom: Slunce | archa-plus | 2026-11-18 | dance (None) | dance/performance (dance) | source → llm+web |
| Orin Rodriguez, Kirikou Gueye: Titty Killer | archa-plus | 2026-12-17 | theatre (None) | performance/theatre (performance) | source → llm+web |
| God Save the Drama Queen: Král*ovna | archa-plus | 2027-01-22 | theatre (None) | performance (performance) | source → llm |
| A+U: Set and Play w/ Ursula Sereghy | archa-plus | 2027-01-27 | dj (None) | workshop (workshop) | keyword → llm |
| Night Lovell | archa-plus | 2027-02-08 | dj (None) | concert (concert) | keyword → llm |
| DRUM & BASS PILATES | roxy | 2026-11-20 | dj (None) | workshop/dj (workshop) | source → llm+web |
| TINLICKER | roxy | 2026-11-21 | dj (None) | concert/dj (concert) | source → llm+web |
| MC GEY | roxy | 2026-11-26 | concert (None) | concert/dj (concert) | source → llm+web |
| TECHNO PILATES S DJ HOUND | roxy | 2026-11-27 | dj (None) | workshop/dj (workshop) | source → llm+web |
| Drum & Bass Pilates s DJ BARBAROU | roxy | 2026-12-18 | dj (None) | workshop/dj (workshop) | source → llm+web |
| New Year’s Eve 2026: Gold Rush | roxy | 2026-12-31 | dj (None) | party/dj (party) | source → llm+web |
| The Opening Party 2027 | roxy | 2027-01-01 | dj (None) | party/dj (party) | source → llm+web |
| Modeselektor LIVE | roxy | 2027-03-03 | dj (None) | concert/dj (concert) | source → llm |

Súhrn (21 akcií):
- **zmena hlavného typu – 18:**
  - divadlo → performance 4;
  - divadlo → čítanie a diskusia (`talk`) 2;
  - `other` → `talk` 2 (Music Digest);
  - divadlo → comedy 1 (TANTEHORSE ►IRIS – podozrivé, pozri Otvorené);
  - `dj` → `workshop` 4 (3× Pilates, A+U Set and Play);
  - `dj` → `concert` 3 (Tinlicker, Modeselektor LIVE, Night Lovell);
  - `dj` → `party` 2 (Roxy NYE Gold Rush, Opening Party 2027);
- **hlavný typ rovnaký, len pribudol doplnkový formát – 3:** Baletky +`dance`, Burkicom +`performance`, MC GEY +`dj`.
- Akcie s `llm` (bez webu, mimo 60-dňového okna) rozhodol `classify_ai`.

### Časť 2 – popis bez viet o nedostatku informácií
- **Prompt** (`RULES_DESCRIPTION`) podľa nového F:
  - žiadne vety o tom, čo sa nenašlo, nie je známe, nebolo zverejnené alebo ohlásené;
  - nič o samotnom hľadaní;
  - miesto a sála sú povolené.
- **Poistka** `strip_no_info` (`pipeline/ai_guards.py`): vymaže jednotlivé vety v CZ ešte pred prekladom. SK/EN sa prekladajú z opraveného CZ.
  - Ak ostane menej ako 60 znakov, akcia AI popis nemá a dostane `needs_review` (pravidlo H).
  - Každá vymazaná veta je v `dropped` ako `description_no_info`.
  - Veta o presune alebo zrušení akcie ostáva (fakt).
- **Testy na skutočných vetách:**
  - DIVA INVITES, Text-appeal, „Sedmé jméno zatím ohlášeno nebylo.“, REVO (celý popis → žiadny popis) – zachytené;
  - Bonobo „…nejsou postavená na laptopu…“ ostáva.
- **V nových odpovediach behu 1** poistka zachytila 3 vety, v behu 2 žiadnu (log `enrich_ai dropped by kind`).
- **Existujúce dáta:** 23 akcií, 32 viet. Všetky sú rozhodnuté znova z uloženého prieskumu s novým promptom a SK/EN sú preložené z nového CZ (beh 1). Po behu 2 je v AI popisoch **0** takých viet.
  - Zoznam (akcia | vymazaná veta z popisu pred 063):

| akcia | veta |
|---|---|
| DIVA INVITES (2026-11-17) | O jednotlivých účinkujících se kromě jejich jmen a označení Portera jako britského interpreta nedochovaly žádné další podrobnosti, stejně jako informace o vydaných nahrávkách. |
| SUNDEJ SE SUNDAY (2026-11-22) | Večer SUNDEJ SE SUNDAY je postavený na jeho setu, ke kterému se podle názvu akce přidávají hosté; konkrétní jména hostů ale nejsou u tohoto termínu uvedena. |
| SUNDEJ SE SUNDAY (2026-11-22) | Program tak zůstává otevřený a může se proměnit podle toho, kdo se k Jamesi Wingovi přidá. |
| PSYTRANCE (2026-11-25) | Náplní noci je psytrance set od Cassie a jejích hostů, bližší podrobnosti o dramaturgii ani o hostech ale zveřejněny nebyly. |
| PSYTRANCE (2026-11-25) | O Cassie samotné nejsou k dispozici žádné informace o vydaných nahrávkách ani o jejím původu. |
| UNITY RAGE DNB STAGE (2026-11-26) | Večer nese název Unity Rage DNB Stage a kromě Mikea Helpera se na něm představí i hosté, jejichž jména pořadatelé zatím nezveřejnili. |
| SUNDEJ SE SUNDAY (2026-11-29) | Konkrétní jména hostů pro tento termín nejsou zveřejněná, program tak zůstává otevřený. |
| Unijazz Open (2026-12-02) | Podrobnosti k průběhu a pravidlům turnaje nejsou v dostupných materiálech uvedeny. |
| Text-appeal vol. 29 (2026-12-10) | Konkrétní jména účinkujících pro tento večer nejsou uvedena. |
| SUDOP – dětské domovy - uzavřený pronáje (2026-12-12) | Pro veřejnost se prostor otevírá až od 19:00, samotný program pronájmu není blíže specifikován. |
| SUDOP – dětské domovy - uzavřený pronáje (2026-12-12) | Veřejnosti přístupná část večera není v dostupných informacích popsána. |
| vánoční večírek GiBONi (2026-12-15) | O složení kapely, jejím původu ani o tom, odkud pochází, nejsou k dispozici žádné další informace. |
| .THEMAYREVOLUTION - PRAHA KŘEST 1 /live (2026-11-19) | Zbytek hostů bude postupně oznámen. |
| REVO: Z Gumy Do Gumy (2026-11-20) | O akci REVO: Z Gumy Do Gumy není k dispozici dost informací, které by umožnily popsat její obsah. |
| REVO: Z Gumy Do Gumy (2026-11-20) | Název se nepodařilo spolehlivě spojit s konkrétním interpretem ani s konkrétním formátem večera. |
| REVO: Z Gumy Do Gumy (2026-11-20) | Z dostupných zdrojů vyplývá pouze to, že se akce koná v termínu 20. listopadu 2026. |
| REVO: Z Gumy Do Gumy (2026-11-20) | Podrobnosti o účinkujících, dramaturgii ani programu nejsou známé. |
| FEVERDREAM (2026-11-26) | Podrobnější informace o jednotlivých vystupujících ani o jejich tvorbě nejsou k dispozici. |
| REVO: SOUR ROOM (2026-11-27) | Konkrétní jména účinkujících ani dramaturgie večera SOUR ROOM ale nejsou veřejně dostupné, stejně jako informace o vydaných nahrávkách či hostech. |
| REVO: SOUR ROOM (2026-11-27) | Akce je proto zaznamenána jen rámcově a podrobnosti o obsazení zůstávají otevřené. |
| WELLWET Residents + Secret Guest (DE) (2026-11-27) | Tentokrát rezidenti dostanou prostor jako hlavní aktéři večera a doplní je blíže neurčený tajný host z Německa, jehož jméno ani zaměření nejsou zveřejněny. |
| DRUM & BASS PILATES (2026-11-20) | Pro tuto listopadovou lekci nejsou konkrétní instruktoři ani DJ jmenováni. |
| NYE Warm Up (2026-12-30) | Program je podle pořadatelů teprve v přípravě, konkrétní DJs mají být oznámeni později. |
| NYE Warm Up (2026-12-30) | Podrobnosti k účinkujícím ani k programu zatím nejsou zveřejněné. |
| The Opening Party 2027 (2027-01-01) | Roxy otevírá rok 2027 první taneční nocí, na kterou zatím nejsou ohlášeni konkrétní interpreti. |
| The Opening Party 2027 (2027-01-01) | Program se podle pořadatelů soustředí na elektronickou taneční hudbu a jména DJů mají být oznámena později. |
| VIDEO OLDIES RUDA TUČEKA (2026-11-21) | Jiní účinkující nejsou uvedeni. |
| SUNDAY RITUALS - MAINSTREAM MUSIC (2026-12-06) | Za pulty se představí DJs SPIRIT a ANDEE, o nichž se kromě zařazení do této klubové řady nepodařilo dohledat bližší údaje o původu, tvorbě ani vydaných nahrávkách. |
| EPIC IS YOUR CHURCH (2026-12-10) | Žádné vlastní releasy k oběma DJs nejsou doloženy, večer tak stojí především na klubovém zvuku a prostředí. |
| SUNDAY RITUALS - ALL KIND OF MUSIC (2026-12-27) | Oba interpreti vystupují především jako DJs a žádné vlastní nahrávky ani bližší biografické údaje o nich nejsou dostupné. |
| NEW YEARS EVE 2026 (2026-12-31) | Pauli Gabrieli a Richard Reynolds doplňují sestavu, o jejichž tvorbě není k dispozici více informací. |
| TITI (2027-01-15) | Podpůrné vystoupení je zatím oznámeno jako TBA. |

- Vynechal som 1 vetu, ktorú prvá verzia vzorov zachytila: Debasement (Fuchs2) „…termín byl … přesunut a nové datum má být oznámeno…“. Presun je fakt, preto ostáva.

### Časť 3 – miesto v popise nie je na kontrolu
- `venue_mentions` sa len počíta v logu a v súhrne behu (`venue / hall in description (no review)`: beh 1 30, beh 2 33). `needs_review` už nenastavuje.
- **Staré značky z cache:** 49 akcií malo `needs_review` a miesto v popise. Pri 13 z nich išlo v behu 1 o nové rozhodnutie (značka je teraz vlastná značka modelu). Zvyšných 36 išlo v behu 2 na rozhodnutie z uloženého prieskumu.
  - Značku som nemazal podľa odhadu. V meraní 062 mala 1 z 8 akcií so značkou modelu zároveň miesto v popise (REVO), takže z cache sa nedalo rozlíšiť, či značku dal model alebo miesto.

### Čísla z `events.json` posledného behu
- Beh 44172530495, `generated_at 2026-11-17T21:52:57+01:00`.
- Príkazy (súbory stiahnuté z GitHub Pages):
  - `python -m pipeline.ai_numbers events.json pipeline_state.json`;
  - `python docs/tasks/063/compare.py events_pred.json events.json` (pred = beh 44156896473).

| | pred (062) | po |
|---|---|---|
| akcie | 374 | 374 |
| s AI doplnením (60 dní) | 243 | 243 |
| typ od AI (`llm` + `llm+web`) / s webom | 227 / 173 | **324 / 197** |
| `method: source` / `keyword` | 114 / 23 | **40 / 0** |
| s `primary_format`, len akcie s AI doplnením | 173 | **243** (70 chýbajúcich doplnených); všetky akcie po: 370 / 374 |
| so žánrami | 227 | 266 |
| s popisom od AI | 239 | 239 |
| s AI doplnením bez AI popisu | 4 | 4 |
| `needs_review` | 85 (48 miesto, 37 model) | **41** (všetky vlastná značka modelu, pravidlo H; 0 za miesto, 0 „popis po vymazaní prázdny“) |
| vety o nedostatku informácií v AI popisoch | 32 v 23 akciách | **0** |

- **Cena 063:** $0.0304 + $0.0348 = **$0.0652** (limit 0,10 $). Žiadne hľadanie: `month=953/3000` sa nezmenil.
- **Mesiac** (`ai_cost`): $1.288, 3 behy.
- **Zostatok kreditu DeepSeek: 0,41 $** (pred 063 0,46 $).
- Nárast žánrov (227 → 266) a typov od AI (`llm`) spôsobil `classify_ai`: 74 akcií mimo okna so `source`/`keyword` išlo prvý raz na AI (4 volania, $0.0025).

### Ručné overenie na webe (2026-11-17, GET stránky, hľadanie textu)
**Typ:**
1. **TINLICKER** – https://www.roxy.cz/events/detail/5077/tinlicker
   - na stránke: „TINLICKER OVLÁDNOU ROXY SVÝM DJ SETEM“ a „místo klasických DJ setů začali vystupovat jako živá kapela“;
   - v dátach: `concert` (hlavný), `dj` doplnkový – **správne podľa B7**.
2. **DRUM & BASS PILATES** – https://www.roxy.cz/events/detail/5191/drum-bass-pilates
   - na stránke: „přináší energickou lekci … spojení pilates, rychlých DnB beatů a klubové atmosféry“;
   - v dátach: `workshop` (hlavný), `dj` – **správne** (zdroj mal `dj`).
3. **THE MUSIC DIGEST (38)** – https://palacakropolis.cz/work/33298?event_id=40909&genre=17&no=62&page_id=33824
   - na stránke: „38. setkání u poslechového pořadu hudebního žurnalisty Dana Sywaly“, „hosté na 15 min rozhovory“;
   - v dátach: `talk` – **správne** (zdroj mal `other`).
4. Navyše **Titty Killer** – https://archa-plus.cz/cz/program/detail/929/2026-12-17-orin-rodriguez-kirikou-gueye-titty-killer-1
   - na stránke: „premiéra divadlo EN friendly performance“, „zvukové a divadelní performance“;
   - v dátach: `performance` (hlavný), `theatre` – **správne**.

**Popisy (pôvodná veta → nový text):**
1. **Text-appeal vol. 29**
   - pôvodne: „Konkrétní jména účinkujících pro tento večer nejsou uvedena.“;
   - teraz bez tej vety, posledná veta „Dvacátý devátý díl se koná v Čítárně Unijazz na Žižkově…“ (miesto povolené). Bez `needs_review`.
2. **Video Oldies Rudy Tučeka (EPIC)**
   - pôvodne: „Jiní účinkující nejsou uvedeni.“;
   - teraz 5 viet o Rudovi Tučekovi a formáte (80. a 90. roky, videoklipy na LED), bez vety o chýbajúcich účinkujúcich.
3. **DIVA INVITES (Cross Club)**
   - pôvodne: „O jednotlivých účinkujících se … nedochovaly žádné další podrobnosti…“;
   - teraz: „…techno night DIVA INVITES, který staví na stejnojmenné rezidentce Diva. Ta na techno stage přivítá britského hosta Portera (UK)…“ – veta o nedostatku zmizla.
   - Model však napísal „Vstup je zdarma.“ (cena v popise, porušenie F) a dal `needs_review` – pozri Otvorené.

### Rozhodnutia urobené samostatne (v `decisions.md`)
- **Typ:**
  - `classify_ai` neposiela akcie so `source`/`keyword` v 60-dňovom okne, rozhoduje `enrich_ai` z webového prieskumu;
  - chýbajúci `primary_format` sa doplní z uloženého prieskumu, ak je medzi formátmi (aj pri `manual`, ručné formáty sa nemenia);
  - inak nové rozhodnutie z prieskumu.
- **Poistka viet:**
  - zoznam vzorov;
  - prah 60 znakov pre „nič použiteľné“;
  - veta o presune/zrušení ostáva;
  - pri jednokrokovom provideri (Claude, záloha) sa CZ opraví a SK/EN sa zahodia.
- **Staré značky za miesto** neodstraňovať odhadom, ale novým rozhodnutím z prieskumu (beh 2, $0.0348).
- Súhrn behu: `review` teraz znamená len „bez popisu po vymazaní“. Pribudli počítadlá `venue / hall in description (no review)` a `primary_format from stored research`.

### Otvorené
- **REVO: Z Gumy Do Gumy:**
  - Starý popis (len vety o nedostatku) poistka správne celý zahodí (test).
  - Nové rozhodnutie z prieskumu však napísalo iný text: dátum, popis klubu a domnienku „Název odkazuje na motiv gumy … u plášťů a duší“. Taký text poistka nezachytí, lebo nejde o vetu o nedostatku informácií, ale o výplň a dohad.
  - Akcia má `needs_review` od modelu. Návrh: pri `needs_review` od modelu popis neukladať (pravidlo H „nič = žiadny popis“) – rozhoduje Matej.
- **Cena a dátum v popise:**
  - DIVA INVITES má „Vstup je zdarma.“, viaceré popisy majú dátum („17. listopadu“).
  - Cena a čas sú vo F zakázané, ale poistka v kóde na ne nie je (len prompt). Prípadná ďalšia poistka = nová úloha.
- **TANTEHORSE ►IRIS → `comedy`/`theatre`/`music`** (hlavný `comedy`) vyzerá podozrivo pri divadelnom súbore. Na kontrolu Matejom, prípadne ručná oprava v `manual.json`.
- **50 akcií spracovaných v 062** má od AI len `primary_format`, formáty ostali zo zdroja. Doplnkové formáty od AI sa doplnia až pri ďalšom spracovaní (zmena názvu alebo nové prepočítanie).
- **`classify_ai` cez DeepSeek** bežal v tomto behu naživo (4 volania, 0 chýb). Typ akcií mimo okna je odhad bez webu.
- **Kredit 0,41 $** vydrží pri bežnej prevádzke približne 8–9 dní. Treba ho dobiť (Matej).
