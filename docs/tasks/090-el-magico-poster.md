# 090: El Magico – celý mesiac z mesačného plagátu (DeepSeek s obrázkovým vstupom)

## Zadanie

**Schválené Matejom 2026-11-20 23:13 a 2026-11-22 12:48.** Nový typ zdroja (obrázok → text) – **Matej súhlasí**. Mení dáta → jeden beh pipeline na konci. **Spustiť po 089** (089 zavádza pravidlo mesačného limitu pri behoch z úloh). Postup pre `venues.json`, `first_loaded`, obrázok miesta, AI okno ako v 085/086/089. Čo nie je jasné, spýtaj sa.

**Čítaj:** report **083** (El Magico, sekcie „Dôležité zistenia“ a „El Magico – OCR“), `docs/tasks/083/elmagico/program-listopad-2026-el-magico.jpg` a **ručný referenčný prepis** `docs/tasks/083/elmagico/poster-reference-listopad-2026.md` (21 akcií), hárok El Magico v `docs/tasks/083/venue-survey.xlsx`, fixtures El Magico v `tests/fixtures/survey2/`, `docs/ai-rules.md` (typy), `pipeline/enrich_ai.py` (ako sa volá DeepSeek, limity, rozpočet).

### 1. Dva zdroje jedného miesta
- **HTML** `elmagico.cz/program/`: vždy 2 najbližšie akcie s detailom a plagátom (`hp-datum-akce`/`hp-mesic-akce`) – bežný adaptér.
- **Mesačný plagát:** `/wp-content/uploads/YYYY/MM/program-<mesiac>-YYYY-el-magico*.jpg` (názov nie vždy rovnaký: `-FINAL`, `-korekce-01`) – nájsť cez `/wp-json/wp/v2/media?…` (083) alebo odkaz zo stránky programu. Aktuálny aj nasledujúci mesiac, ak už je.

### 2. Čítanie plagátu cez DeepSeek
- **Model s podporou obrázkov over v oficiálnej dokumentácii** (api-docs.deepseek.com, sekcia Vision; podľa nej obrázky prijíma `deepseek-v4-flash-vision-exp`, iné zdroje uvádzajú podporu priamo v `deepseek-flash` od 9/2026). Použi ten, ktorý podľa docs funguje; zapíš do `docs/decisions.md` aj s URL. Žiadny nový kľúč ani platená služba navyše.
- Výstup: zoznam akcií (dátum, názov, prípadne čas – El Magico ho zvyčajne nemá) v pevnej JSON schéme. **Kontroly:** dátum v danom mesiaci; ak plagát uvádza deň v týždni, musí sedieť; pri neistote akciu nepridať (zalogovať). Nič nedomýšľať.
- **Plagát sa číta raz** (cache podľa URL/hash obrázka); nový/zmenený plagát = nové čítanie. Náklady zapíš (očakávané zlomky centu).
- **Test proti referenčnému prepisu novembra** (21 akcií): koľko akcií, dátumov a názvov model prečítal správne – tabuľka v reporte. Ak je presnosť zlá (napr. chybné dátumy), **zastav a napíš** pred zapojením do denného behu.

### 3. Akcie z plagátu vs. z webu
- Akcia z plagátu = jednoduchá akcia (názov, dátum, bez času, bez plagátu → obrázok miesta podľa pravidla 082). **Keď rovnaká akcia pribudne v HTML** (s plagátom a detailom), **nahradí tú z plagátu** – párovanie dátum + podobnosť názvu; v jeden deň môžu byť dve akcie (napr. kvíz a DJ), nespárovať nesprávnu. `id` a `first_seen` zostanú akcie z plagátu (nie je to nová akcia).
- Typy (Matej 2026-11-22): **turnaje a beer pong → párty, kvíz → kultúra / quiz**; ostatné určí AI ako pri iných miestach (doplniť do `docs/ai-rules.md` ako pravidlo pre tieto akcie, nie len pre El Magico).

### 4. Kontrola Matejom
- **Prvý mesiac skontroluje Matej:** v reporte tabuľka všetkých akcií z plagátu (dátum, názov, typ) vedľa plagátu; opravy pôjdu do `data/manual.json` (ako iné ručné opravy). Plagáty vyzerajú vždy rovnako – ďalej to má bežať samo.

### 5. Miesto vo `venues.json`
- El Magico, Chemická 953, Praha 4 – Chodov. Kapacita **300** (Matej). IG `elmagico_club`. Obrázok miesta: fotka 1000×667 z 083. Štítky: návrh s ukážkami akcií (Matej schvaľuje).

## Overenie a report
- `pytest -q` (hľadanie plagátu, schéma výstupu, kontroly dátumu, párovanie plagát ↔ HTML vrátane dvoch akcií v jeden deň, cache plagátu).
- Presnosť čítania novembrového plagátu proti referenčnému prepisu (tabuľka).
- **Jeden beh pipeline** (`ignore_monthly_cap` podľa 089). Počet akcií El Magico (z plagátu / z HTML / nahradených), cena čítania plagátu, AI doplnenie.
- Tabuľka akcií z plagátu na kontrolu Matejom; návrh štítkov.

## Report

**Dátum:** 2026-11-22. **Commity:** `c22460e` (čítanie plagátu + testovací režim), `209530c` (oprava YAML), `414101f` (adaptéry, párovanie, `venues.json`, pravidlo typov, testy, docs), `74f7aa8` (čas len zo „Začátek/Start“), report v nasledujúcom commite.
**Stav:** hotovo. Pipeline bežal dvakrát: 45040172355 (success). Pri kontrole som v ňom našiel chybný čas 17:00 z vety o happy hour, preto po oprave ešte 45041636988 (success). Čísla sú z druhého behu.

### Hotovo
- **Nový typ zdroja `poster`** (`pipeline/adapters/poster.py`, stratégia `elmagico`). Plagát sa hľadá cez `/wp-json/wp/v2/media?search=program` (1 GET denne) pre aktuálny aj nasledujúci mesiac podľa názvu `program-<mesiac>-RRRR-el-magico*.jpg` (funguje aj `-FINAL` a `-korekce-01`, mesiac sa berie z názvu, nie z priečinka). Decembrový plagát ešte nie je zverejnený.
- **Čítanie plagátu** (`pipeline/poster_read.py`): model `deepseek-flash` s obrázkom (base64 `image_url`, `detail: high`, JSON mode). Model je podľa oficiálnej stránky https://api-docs.deepseek.com/guides/vision/ (stiahnutá v behu 45039236491, z počítača nedostupná) a je zapísaný v `docs/decisions.md`. Kód kontroluje mesiac/rok v hlavičke, deň v mesiaci, deň v týždni, `uncertain`, prázdne a duplicitné riadky; čas berie len ako platné HH:MM. Zahodené riadky sa logujú.
- **Plagát sa číta raz:** cache v `pipeline_state.json` → `adapter_detail.el-magico.posters[URL]` (`modified`, SHA-256, riadky). V druhom behu sa už nečítal.
- **HTML** `html/elmagico`: 1 GET. Z karty berie dátum, názov, odkaz, flyer, celý text a cenu z riadku „vstup…“ so sumou; čas len zo „Začátek/Start HH:MM“.
- **Párovanie plagát ↔ HTML** (`pipeline/poster_merge.py`): ten istý deň, podobnosť slov ≥ 0,6 a aspoň 2 spoločné slová. HTML akcia preberá `id` a `first_seen` akcie z plagátu a `sources` = html + poster. Počítajú sa aj akcie z plagátu z predchádzajúceho behu. Obrázok plagátu sa nepoužíva ako stránka akcie (detail enrichment ani AI ho neotvárajú).
- **Typy:** pravidlo B8 v `docs/ai-rules.md` a v prompte – turnaj / beer pong → `party`, kvíz → `quiz`, pre všetky miesta.
- **El Magico vo `venues.json`:** Chemická 953, Praha 4 – Chodov, súradnice OSM, kapacita 300 (small), IG `elmagico_club`, obrázok 1000×667 z 083, zatváracie časy z pätičky webu.
- `data-model.md`: typ zdroja `poster`. `pytest -q`: **736 passed**, 3 skipped (nové `tests/test_elmagico_090.py`, 16 testov: hľadanie plagátu, schéma a fallback odpovede, kontroly dátumu a dňa, cache plagátu, párovanie vrátane dvoch akcií v jeden deň a reálnej stránky z 22. 11.). Zastaraný test v `tests/test_venues_089.py` som upravil podľa Matejových údajov z `82f3108` (IG 007, kapacita Café V Lese 200).

### Presnosť čítania novembrového plagátu (beh 45039236491, `docs/tasks/090/poster_test_run45039236491.txt`)
| Referencia | Prečítané | Dátumy správne | Dni v týždni | Názvy (bez ohľadu na veľkosť/diakritiku) | Názvy doslova | Interpreti | Navyše | Zahodené |
|---|---|---|---|---|---|---|---|---|
| 21 | 21 | 21 | 21 | 21 | 20 | 21 | 0 | 0 |

Jediná chyba: č. 7 „NA **JIŽÁKU**“ prečítané ako „NA **JÍZÁKU**“ (diakritika). Cena testu 0,00097 $, v pipeline 0,00082 $ (1269 vstupných tokenov, z toho 1024 z cache; 1296 výstupných; mimo špičky). Za mesiac ide o 1–2 čítania, teda menej ako 0,01 $.

### Čísla (beh **45041636988**, `events.json` vygenerovaný 2026-11-22 17:13)
Príkaz: stiahnuť `https://matejstolarik.github.io/eventapp/events.json` a `pipeline_state.json` (uložiť ako `state.json`) do `<dir>`, potom `python docs/tasks/090/nums090.py <dir>`.
- Všetkých akcií **828**. El Magico **7**: len z plagátu **4**, z HTML nahradzujúca plagát (`html+poster`) **1**, len z HTML **2**.
- Plagát: 21 riadkov, 0 zahodených; 15 akcií je minulých (pred 21. 11.).
- Log: `poster events: 20, replaced by HTML: 1`. Riadok 24. 11. má rovnaký normalizovaný názov aj `id` ako HTML akcia, takže ho odstránil už `dedup` (HTML vyhrala, `id` sedí). Riadok 25. 11. „DARTS BATTLE & RUMOVÝ PROJECT X“ sú na webe **dve akcie**: Rumový PROJECT X prevzal `id` plagátu, Darts Battle ostal ako samostatná akcia.
- AI: zo 7 akcií El Magico je doplnených 6. Glow in the Dark (21. 11.) je už mimo okna AI. 3 akcie z plagátu majú `needs_review`. Prvý beh: `enriched=10`, 0,0502 $; druhý beh: `enriched=2`, 0,0055 $. Za november **4,8973 $** (mesačný limit ignorovaný, `ignore_monthly_cap`), zostatok DeepSeek **1,77 $**.
- `first_loaded` El Magico = 2026-11-22 (akcie nie sú „Nové“), `image_card` vygenerovaný.

### Overenie na webe (2026-11-22)
| URL | Web | `events.json` |
|---|---|---|
| elmagico.cz/program/darts-battle-2/ | „Středa 25.11.2026 … Start turnaje v 19:00“ | 2026-11-25 19:00 ✔ (čas doplnila AI zo stránky) |
| elmagico.cz/program/ (karta 24. 11.) | „Happy Hour … od 17:00 do 22:00“, bez času začiatku | čas `null` ✔ (po oprave; prvý beh mal chybne 17:00) |
| plagát `program-listopad-2026-el-magico.jpg` | 27. 11. PÁ „BLACK FRIDAY – PRICE MASSACRE“, DJ ABE; 28. 11. SO „BUMBU LATIN FIESTA“, DJ MARIO | ✔ názov, dátum, interpret |

### Akcie z plagátu – na kontrolu Matejom (november; plagát: `docs/tasks/083/elmagico/program-listopad-2026-el-magico.jpg`)
| # | Dátum | Deň | Názov (plagát) | Cena (plagát) | Interpret | V `events.json` | Typ |
|---|---|---|---|---|---|---|---|
| 1 | 03. 11. | ÚT | BEER PONG CHAMPIONSHIP & AFTERPARTY | VSTUP ZDARMA |  | nie (minulá) |  |
| 2 | 04. 11. | ST | VŠCHT HALLOWEEN 4 STUDENTS |  |  | nie (minulá) |  |
| 3 | 05. 11. | ČT | TURNAJ VE STOLNÍM FOTBÁLKU + CHUPITO 1 + 1 ZDARMA | VSTUP ZDARMA |  | nie (minulá) |  |
| 4 | 06. 11. | PÁ | FRIDAY KÝBLMANIA |  | DJ PARTYBOY | nie (minulá) |  |
| 5 | 07. 11. | SO | RAP NIGHT CZ/SK BY LET'S RAVE IT UP |  |  | nie (minulá) |  |
| 6 | 10. 11. | ÚT | BEER, CHILL & GAMES & CUBA LIBRE ZA 59 KČ | VSTUP ZDARMA |  | nie (minulá) |  |
| 7 | 11. 11. | ST | ALKOBITVA KOLEJÍ NA JÍZÁKU (správne JIŽÁKU) - O 5 XXL KÝBLŮ AMU SKINNY | VSTUP DO 22:00 ZDARMA | DJ ABSOLUTH | nie (minulá) |  |
| 8 | 12. 11. | ČT | Z-QUIZ & AFTERPARTY | VSTUP ZDARMA |  | nie (minulá) |  |
| 9 | 13. 11. | PÁ | AMUNDSEN TWIST NIGHT |  | DJ DAJI SCREW | nie (minulá) |  |
| 10 | 14. 11. | SO | STAR WARS NIGHT S JAMESONEM |  | DJ LUCKY D | nie (minulá) |  |
| 11 | 16. 11. | PO | NEJVĚTŠÍ STUDENTSKÁ AKCE: SEMAFOR BY LET'S RAVE IT UP |  |  | nie (minulá) |  |
| 12 | 17. 11. | ÚT | BEER PONG CHAMPIONSHIP & AFTERPARTY | VSTUP ZDARMA |  | nie (minulá) |  |
| 13 | 18. 11. | ST | SEZNAMOVÁK NF VŠE VOL. 2 |  | DJ ABE | nie (minulá) |  |
| 14 | 19. 11. | ČT | TURNAJ VE STOLNÍM FOTBÁLKU & WILD PRICE CRASH | VSTUP ZDARMA |  | nie (minulá) |  |
| 15 | 20. 11. | PÁ | MISS TANGA 2026 VOL. 2 O 10.000 KČ |  | DJ ABSOLUTH | nie (minulá) |  |
| 16 | 21. 11. | SO | GLOW IN THE DARK BY LET'S RAVE IT UP |  |  | áno, poster | party |
| 17 | 24. 11. | ÚT | BEER, CHILL & GAMES & CHUPITO 1 + 1 ZDARMA | VSTUP ZDARMA |  | áno, html → „Beer, Chill & Games & Chupito 1+1 ZDARMA“ | party |
| 18 | 25. 11. | ST | DARTS BATTLE & RUMOVÝ PROJECT X - STUDENT TAKEOVER | VSTUP DO 22:00 ZDARMA | DJ FANDA MAREK | áno, html+poster → „Rumový PROJECT X – STUDENT TAKEOVER“ (+ samostatne „Darts Battle“ z HTML, party) | party |
| 19 | 26. 11. | ČT | BEER, CHILL & GAMES & GIN & TONIC WHISKOVKA ZA 59KČ | VSTUP ZDARMA |  | áno, poster | party |
| 20 | 27. 11. | PÁ | BLACK FRIDAY – PRICE MASSACRE |  | DJ ABE | áno, poster | party |
| 21 | 28. 11. | SO | BUMBU LATIN FIESTA |  | DJ MARIO | áno, poster | party |

### Návrh štítkov (na schválenie, už vo `venues.json`)
| `type` | `character` | `music` | `size` (kapacita) | `closing` | Ukážky akcií |
|---|---|---|---|---|---|
| dance-club, bar | student, commercial, late-night | pop, hip-hop, latin, edm | small (300) | Út 02:30, St 03:30, Čt 02:30, Pá–So 05:00 (web) | Beer Pong Championship, Z-Quiz, Rap Night CZ/SK, Miss Tanga, Glow in the Dark, Black Friday, Bumbu Latin Fiesta |

Návrh: **`commercial_club: true`** (študentský komerčný klub, ako Karlovy Lázně). Nenastavené – podľa `data-model.md` ho nastavuje Matej.

### Rozhodnuté samostatne (v `docs/decisions.md`)
- Hľadanie plagátu cez WP media search, cache podľa URL + `modified` + SHA-256; neúspešné čítanie sa necacheuje. Cena čítania sa pripočíta k rozpočtu DeepSeek a číta sa aj pri vyčerpanom mesačnom limite (zlomok centu raz mesačne).
- Poznámka „/VSTUP ZDARMA/“ ide z názvu do `price_text` (`free` len pri presnom „VSTUP ZDARMA“). Kolektívy „… DJ'S“ nie sú interpreti.
- Pravidlá párovania (prah, prednosť pri zhode); nespárovaná HTML akcia ostáva samostatná.
- Čas v HTML len zo „Začátek/Start“, nie z „od HH:MM“ (nový riadok, mení bod 6).

### Čo ostáva otvorené
- **Opravy cez `data/manual.json`:** dnes vie opraviť len typ, žáner, cenu, čas a popis, **nie názov ani dátum**. Oprava diakritiky (č. 7) alebo chybného dátumu z plagátu by potrebovala nové polia `title`/`date` v `manual.json`, čo je zmena dátového modelu → rozhoduje Matej.
- `commercial_club` a štítky El Magico čakajú na schválenie.
- Decembrový plagát ešte nie je; načíta sa automaticky, keď ho El Magico nahrá (v logu „[poster]: read …“).
- 3 akcie z plagátu majú od AI `needs_review` (na webe je o nich málo informácií).
