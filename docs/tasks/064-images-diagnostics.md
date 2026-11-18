# 064: Obrázky akcií – diagnostika (chýbajúce, rozlíšenie, orez) + psytrance/reggaeton

## Zadanie

**Schválené Matejom 2026-11-17.** Matej: obrázky sú základ appky, dnes (1) často chýbajú, (2) sú orezané tak, že nemajú výpovednú hodnotu (napr. Xzibit – vidno len rameno), (3) v detaile majú nízke rozlíšenie. **Táto úloha len meria a pripravuje podklad, appku ani dáta v `events.json` nemení** (okrem časti 4). Zmena zobrazenia príde po Matejovom posúdení a návrhu.

Príčiny z kódu (hlavný chat):
- `pipeline/thumbs.py`: náhľad akcie = štvorec zo stredu (`crop` + `resize` na 240 px). Políčko mriežky má ~120 CSS px, pri DPR ~3 treba ~360 px.
- `web/src/pages/EventPage.tsx`: detail ukazuje `image_url` v štvorci s `objectFit: cover` (tiež orez).
- Hypotéza (neistá): niektoré adaptéry berú malý obrázok zo zoznamu programu (`html_forum_karlin.py`, `html_archa.py`), hoci stránka akcie má väčší (`og:image`, `srcset`). `html_roxy.py`, `html_epic.py`, `rss.py`, `api.py` dávajú v zozname `image_url=None` – over, či sa doplní z detailu.

**Čítaj:** `pipeline/thumbs.py`, adaptéry s `image_url` (`grep -n image_url pipeline/adapters/*.py`), `docs/design.md` 1 a časti o mriežke Akcií a stránke akcie (len na pochopenie, nemeniť).

### 1. Chýbajúce a malé obrázky (po podnikoch)
- Z `events.json` posledného behu: na podnik počet akcií, bez obrázka, a rozlíšenie `image_url` (šírka × výška: medián, min; koľko pod 600 px na kratšej strane).
- Pre každý podnik otvor 2–3 stránky akcií (ohľaduplne, cache) a zisti, či je k dispozícii väčší obrázok (`og:image`, `srcset`, odkaz na plnú veľkosť) a pri akciách bez obrázka, či ho stránka akcie má. Tabuľka: podnik · odkiaľ berieme dnes · čo je k dispozícii · navrhovaná zmena. Nič neimplementuj.
- Bike Jesus: len konštatovať (program je na Facebooku).

### 2. Porovnanie orezov (kontaktný hárok)
- Pre všetky obrázky akcií v `events.json` vytvor 4 varianty štvorca 360 px:
  1. **dnes:** stred;
  2. **tváre:** detekcia tvárí (OpenCV, napr. YuNet alebo Haar – vyber a zdôvodni; závislosť len v skripte, nie v dennom behu). Štvorec okolo oblasti všetkých tvárí; ak sa nezmestí, okolo najväčších tvárí. Bez tváre: obrázok na výšku zhora, inak stred;
  3. **zhora:** na výšku zhora, inak stred (bez detekcie);
  4. **celý:** celý obrázok vycentrovaný na rozmazanom a stmavenom pozadí z neho samého.
- Výstup: **lokálna** HTML stránka `docs/tasks/064/sheet/index.html` (riadok = akcia: názov, podnik, pôvodný obrázok + rozmer + pomer strán, 4 varianty) s možnosťou pri každom riadku kliknúť, ktorý variant je najlepší, a export voľby do `docs/tasks/064/choices.json` (tlačidlo „Uložiť“ stiahne JSON; Matej ho vloží do repa).
- **Obrázky ani hárok s obrázkami necommituj** (cudzie autorské diela vo verejnom repe) – `docs/tasks/064/sheet/` daj do `.gitignore`. Commitni skript, ktorý hárok vytvorí (`scripts/review/crop-sheet.py`), a súhrn.
- Do reportu: počet obrázkov podľa pomeru strán (na výšku / štvorec / na šírku / banner ≥ 2 : 1), v koľkých detekcia našla tvár (1 / viac), koľko času detekcia trvá na obrázok.

### 3. Overenie zrušenia akcie (Forum Karlín)
- Pri prieskume AI (062) stránka Omah Lay (`forumkarlin.cz/udalost/omah-lay`, 18. 11.) ukazovala „ZRUŠENO“. `html_forum_karlin.py` má `status = "cancelled"` pri „ZRUŠENO“. Over v `events.json`, či má akcia `status: cancelled`, a v appke (Playwright, jedna snímka `docs/tasks/064/omah-lay.jpg`), ako sa zrušená akcia zobrazuje. Ak `status` nesedí, nájdi príčinu, neopravuj.

### 4. ~~Drobnosť: psytrance a reggaeton~~ – **ZMENA 2026-11-17 (pred spustením): presunuté do 065, nerob.**
(pôvodný text ponechaný)
- Zrušiť mapovanie `psytrance → trance` a `reggaeton → latin` v `data/genre_aliases.json`, pridať `psytrance` a `reggaeton` do zoznamu žánrov (`docs/data-model.md`) a kde treba (preklady žánrov v appke). Pravopisné varianty (`psy trance`, `psychedelic trance` → `psytrance`). Platí od najbližšieho behu, bez prepočítania AI (ak sa mapovanie robí z uloženej surovej hodnoty, napíš to).

## Overenie a report
- `pytest -q`, `npm test`/`build` len ak sa menila appka (časť 4 preklady).
- Report: tabuľka z časti 1, súhrn z časti 2 (bez obrázkov), výsledok časti 3, príkaz na vytvorenie hárku, otvorené body. Matejovi napíš, ako hárok otvoriť.

## Report

**Dátum:** 2026-11-18. **Commity:** `2b32742` (skript hárku, Playwright spec, snímka, riadok v `decisions.md`), report v nasledujúcom commite. **Dáta:** `site/events.json` behu [44202801880](https://github.com/matejstolarik/eventapp/actions/runs/44202801880), generated_at `2026-11-18T00:57:25+01:00` (zhodný s `https://matejstolarik.github.io/eventapp/events.json`). Appka ani `events.json` sa nemenili. `pytest -q`: 494 passed. Časť 4 presunutá do 065, nerobená.

**Príkaz** (čísla z časti 1 a 2, hárok):
```
pip install opencv-python-headless pillow
python scripts/review/crop-sheet.py site/events.json
```
Hárok: otvor `docs/tasks/064/sheet/index.html` v prehliadači (lokálny súbor, dvojklik). Pri každom riadku klikni na najlepší variant (voľby sa pamätajú v prehliadači), „Uložiť“ stiahne `choices.json` → vlož ako `docs/tasks/064/choices.json`. Originály sa sťahujú len raz (cache `docs/tasks/064/sheet/orig/`), celý adresár je v `.gitignore`.

### 1. Chýbajúce a malé obrázky

Akcie s `image_url` 311 / 372; všetkých 311 sa stiahlo a dekódovalo.

| podnik | akcie | bez obrázka | medián š×v | min. kratšia strana | kratšia strana < 600 |
|---|---|---|---|---|---|
| palac-akropolis | 84 | 0 | 480×288 | 288 | 79/84 |
| archa-plus | 60 | 0 | 500×500 | 500 | 60/60 |
| roxy | 41 | 0 (3× zástupný `no-image-480-480.png`) | 480×480 | 480 | 41/41 |
| meetfactory | 35 | 0 | 250×327 | 139 | 35/35 |
| epic | 35 | **35** | – | – | – |
| bike-jesus | 26 | **26** | – | – | – |
| forum-karlin | 24 | 0 | 600×300 | 150 | 24/24 |
| fuchs2 | 21 | 0 | 1920×1080 | 468 | 1/21 |
| citarna-unijazz | 16 | 0 (ale **všetkých 16 má ten istý** obrázok) | 2560×1675 | 1675 | 0/16 |
| cross-club | 15 | 0 (1× logo klubu) | 150×150 | 150 | 15/15 |
| kasarna-karlin | 15 | 0 | 4500×4500 | 4500 | 0/15 |

Prieskum stránok akcií (2–3 na podnik, 1 požiadavka/s, cache v scratchpade). Rozmery overené stiahnutím:

| podnik | odkiaľ berieme dnes | čo je k dispozícii | navrhovaná zmena |
|---|---|---|---|
| Palác Akropolis | zoznam, `…_web_hp.jpg` (480×288) | detail: `…_web_event.JPG` 590×393 (Vivere); `og:image` = `_hp`; bez `_web` varianty (404) | brať `_web_event` z detailu (mierne väčší); väčší neexistuje |
| Archa+ | zoznam, `image-manipulation/resize?…&width=500&height=500` (server už oreže na štvorec) | `og:image` = originál `/images/…` (José González 1280×836; Andre miri cipa banner 3840×1280) | brať `og:image` (originál) |
| Roxy | `og:image` / JSON-LD `…-crop-480-480.png` = **štvorec, ktorý vyrezala už Roxy** z bannera 1400×480 (preto Xzibit = rameno; náš stredový orez na to nemá vplyv) | v skripte stránky (escapovaný JSON) `…-1400-500.png` = celý banner 1400×480 | brať banner `-1400-500` zo stránky akcie; pre štvorec potom len variant „celý“ (banner ≥ 2 : 1) |
| MeetFactory | JSON-LD `media/images/thumbs/…-250x.jpg` (250 px šírka) | `og:image` = originál (Arab Strap 640×640, Allt 800×800); v stránke aj `rescaled/…-320x426` | brať `og:image` namiesto JSON-LD `image` |
| Epic | nič (zoznam `None`; detail_enrich hľadá len JSON-LD/`og:image`, ktoré stránka nemá) | v detaile `<img src="/upload/temp/events/1000x1000-…-1920-1080.png">` (SLVL 1080×1080) | v `html_epic.py` (detail sa už sťahuje?) alebo detail_enrich: vziať tento `img` – **nová cesta k dátam, treba súhlas** |
| Forum Karlín | zoznam `…-600x300` (WP náhľad) | `og:image` = originál (Omah Lay 1920×640), zoznam má aj `srcset` 1280×640; galéria niekedy plagát na výšku (Stahlzeit `…_1080x1920_log-1.jpg` 675×1200) | brať `og:image` (alebo najväčší `srcset`); plagát na výšku len ak je, ako voliteľný |
| Cross Club | `og:image` z detailu `…/150x150c-…` (150×150 orez) | v detaile `…/420x0-…` (420 px šírka, pomer zachovaný, napr. 420×220); originál `/data/files/…` 404 | brať `420x0-` obrázok z detailu (väčší neexistuje) |
| Čítareň Unijazz | `og:image` | `og:image` je **spoločný obrázok webu** (`2022/11/DSC_0040-scaled.jpg`, rovnaký pre všetky akcie); JSON-LD `image` = logo; vlastný obrázok akcie stránka nemá (na Text-appeal sú obrázky VRBA, pravdepodobne iná akcia – neoverené) | ignorovať tento spoločný obrázok (→ `null`, zobraziť ako „bez obrázka“) |
| Fuchs2 | JSON-LD (Wix, `w_1920,h_1080`) | dostatočné | nič |
| Kasárna Karlín | JSON-LD, originál 4500×4500 PNG | dostatočné, ale veľké súbory (detail načíta originál priamo) | prípadne zmenšená kópia pre detail |
| Bike Jesus | API bez obrázkov | program je na Facebooku | len konštatujem |

**Nález navyše – chyba v `pipeline/thumbs.py` (neopravená):** 5 akcií má `image_url`, ale nemá `image_thumb` (4 Forum Karlín, 1 MeetFactory), lebo URL obsahuje ne-ASCII znaky (cyrilické `х` v `2400х800`, `‍` (ZWJ), `ö` v `Kötter`) a `urllib` ich odmietne (`'ascii' codec can't encode`). V skripte hárku stačilo `urllib.parse.quote(url, safe=…)`; v pipeline by to bola jednoriadková oprava.

### 2. Porovnanie orezov (súhrn, bez obrázkov)

311 obrázkov, varianty 360 px: 1 dnes (stred), 2 tváre, 3 zhora, 4 celý (na rozmazanom stmavenom pozadí). Detekcia: OpenCV YuNet (zdôvodnenie v `decisions.md` 2026-11-18).

- **Pomer strán** (uložený obrázok): na výšku (< 0,95) 23 · štvorec (0,95–1,05) 135 · na šírku 128 · banner ≥ 2 : 1 25. Pozor: veľa „štvorcov“ sú štvorce, ktoré už oreže web (Archa 60, Roxy 41) – tam žiadny náš variant orezu nepomôže, kým neberieme väčší obrázok (časť 1).
- **Tváre:** 1 tvár 82, viac tvárí 92 (z toho 34, kde sa všetky nezmestili a orez ide okolo najväčších), bez tváre 137.
- **Čas detekcie:** medián 8,4 ms / obrázok, max 95,7 ms, spolu 4,5 s pre 311 obrázkov (CPU, obrázok zmenšený na ≤ 1024 px).

### 3. Zrušená akcia Omah Lay (Forum Karlín, 18. 11.)

- `events.json`: `forum-karlin-2026-11-18-omah-lay` má **`status: "scheduled"`**, `flags: []` → nesedí.
- **Príčina:** `html_forum_karlin.py` (`_parse_card`, ~r. 150) hľadá zrušenie len v `.nalepka .msg`. Web (`https://www.forumkarlin.cz/program/`, 2026-11-18) ho označuje inak: v zozname `<div class="event cancel">` a `<p>ZRUŠENO</p>` pod dátumom; v detaile `<div id="event" class="cancel">` a `<p class="zmena">ZRUŠENO</p>`, kým `.nalepka .msg` ukazuje „JIŽ DNES“. Neopravené (podľa zadania).
- **Appka** (`docs/tasks/064/omah-lay.jpg`, skript `tests/playwright/screenshots-064.spec.ts`, skutočné `events.json`, čas 18. 11. 12:00): akcia sa zobrazuje ako bežná, bez akéhokoľvek označenia zrušenia. Appka zrušené akcie (`status: cancelled`) zo zoznamov vyraďuje (`web/src/core/events.ts`, `period.ts`, `night.ts`); detail ani `docs/design.md` označenie zrušenej akcie nemajú.

### Otvorené
- Návrhy zmien zdrojov obrázkov (tabuľka časti 1) – čaká na Matejovo posúdenie; Epic = nová cesta k dátam, treba súhlas.
- Oprava ne-ASCII URL v `thumbs.py` a stavu zrušenia vo Forum Karlín – samostatná úloha.
- Matejova voľba variantov v hárku (`choices.json`).
