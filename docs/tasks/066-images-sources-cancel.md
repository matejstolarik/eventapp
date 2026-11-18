# 066: Zrušené akcie Forum Karlín, väčšie obrázky zo zdrojov, náhľady, pravidlo orezu (meranie)

## Zadanie

**Schválené Matejom 2026-11-18** po reporte 064. Matej súhlasí s obrázkom EPIC zo stránky akcie alebo zo zoznamu programu (ten istý web – nová cesta k dátam schválená). Zobrazenie v appke (orez v mriežke, celý obrázok v detaile) **nie je súčasťou** – príde po návrhu.

**Čítaj:** report 064 (tabuľky časti 1, časť 3); `pipeline/adapters/html_forum_karlin.py` (`_parse_card`, `_enrich_from_detail`), `html_archa.py`, `html_roxy.py`, `html_akropolis.py`, `html_epic.py`, `jsonld.py`/`detail_enrich.py` (MeetFactory, Cross Club, Unijazz – over, kde sa berie `image_url`), `pipeline/thumbs.py`; `data/genre_hierarchy.json`; `docs/decisions.md` (`grep -n "064\|thumb\|image"`).

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`.

### 1. Zrušené akcie vo Forum Karlín (prvé, hneď beh)
- Príčina (064): adaptér hľadá zrušenie len v `.nalepka .msg`; web označuje zrušenie `<div class="event cancel">` a `<p>ZRUŠENO</p>` v zozname a `<div id="event" class="cancel">`, `<p class="zmena">ZRUŠENO</p>` v detaile. Rozpoznať všetky tri; `.nalepka .msg` ponechať.
- Test na uloženom HTML (Omah Lay 2026-11-18). Po commite **ručný denný beh** a over v `events.json`, že `forum-karlin-2026-11-18-omah-lay` má `status: cancelled` (ak už akcia z okna vypadla, over na teste a napíš to).
- Over, či iné adaptéry nemajú podobné slepé miesto pri zrušení/presune (len `grep` a krátky súhrn, neopravovať).

### 2. Väčšie obrázky zo zdrojov (podľa tabuľky 064)
- **Archa+:** `og:image` (originál) namiesto štvorca 500×500 zo zoznamu.
- **Roxy:** celý banner `…-1400-500` zo stránky akcie namiesto štvorca `-crop-480-480` (príčina Xzibit). Zástupný `no-image-480-480.png` → `null`.
- **MeetFactory:** `og:image` namiesto JSON-LD `image` 250 px.
- **Forum Karlín:** `og:image` (originál) alebo najväčší `srcset`.
- **Cross Club:** **originál z odkazu lightboxu v detaile** (Matej 2026-11-18: `<a href="/files/2026/prosinec/sub.jpg" rel="lightbox">` na https://www.crossclub.cz/cs/program/8728-drum-and-bus-station-w-fourward-smooth-chris-su-7-mc-fedora/ – vysoké rozlíšenie; 064 skúšala len `/data/files/…`). Ak lightbox nie je, `420x0-`; logo klubu → `null`.
- **Palác Akropolis:** `_web_event` z detailu, ak existuje.
- **EPIC:** obrázok zo stránky akcie (`/upload/temp/events/…`) alebo zo zoznamu programu (Matej: každá akcia má obrázok, viď `https://www.epicprague.com/program`); vyber spoľahlivejšie, bez nových požiadaviek navyše, ak sa dá.
- **Čítareň Unijazz:** 064 zistila, že `og:image` je spoločný obrázok webu. **Matej tvrdí, že takmer každá akcia má po rozkliknutí vlastný obrázok.** Over na 3–4 akciách v tele stránky (obsah článku, galéria, `wp-post-image`, `img` v `.entry-content`), nie len v metadátach; napíš URL a čo si našiel. Vlastný obrázok akcie brať; spoločný obrázok webu a logo → `null`.
- Pri každom podniku over na 2 akciách rozmer stiahnutého obrázka (tabuľka pred/po). Ohľaduplnosť ako doteraz (žiadne požiadavky navyše, ak detail už sťahujeme; inak v limitoch zdroja).

### 3. Náhľady a obrázok pre detail
- `thumbs.py`: oprava URL s ne-ASCII znakmi (`urllib.parse.quote`), test na 3 prípadoch z 064 (cyrilické `х`, ZWJ, `ö`).
- Náhľad akcie **480 px** (namiesto 240) – stále stredový štvorec, orez sa mení až po návrhu. Prepočítať existujúce (limit náhľadov za beh podľa potreby zvýš jednorazovo, napíš o koľko).
- Nové pole **`image_detail`**: zmenšená kópia bez orezu, dlhšia strana najviac 1200 px, JPEG, na Pages vedľa náhľadov (rovnaké pravidlá a cache ako náhľady). Appka ho zatiaľ nepoužíva. Zapíš do `data-model.md`.

### 4. Meranie pravidla orezu (bez zmeny appky)
Na obrázkoch a variantoch z 064 (lokálna cache hárku) a Matejových voľbách `docs/tasks/064/choices.json` spočítaj zhodu pravidiel s voľbou Mateja. **Vynechaj riadky, kde sú varianty prakticky rovnaké** (napr. štvorcový zdroj; kritérium napíš).
- R1: vždy stred (dnes);
- R2: na výšku zhora, inak stred;
- R3: na výšku zhora; na šírku s tvárou → okolo tvárí; na šírku bez tváre → celý; štvorec → stred;
- R4: ako R3, ale banner ≥ 2 : 1 s tvárou → stred.
Výstup: tabuľka zhody (počet, %) a 10 prípadov, kde najlepšie pravidlo nesedí (id, pomer strán, tváre, voľba Mateja). Nič neimplementuj.

### 5. Drobnosť: rodičia existujúcich podžánrov (Matej 2026-11-18)
- V `data/genre_hierarchy.json` doplniť rodičov aj pre podžánre, ktoré existovali pred 065 (napr. `tech-house`, `deep-house`, `afro-house` ak existuje → `house`; `death-metal`, `metalcore`, `black-metal` → `metal`; `drum-and-bass` podžánre, `minimal-techno` → `techno` …). Úplný zoznam pridaných vzťahov do reportu na Matejovu kontrolu. Test konzistencie ostáva.

## Overenie a report
- `pytest -q`, `npm test`; čísla behu (príkaz).
- Čísla z `events.json` posledného behu: akcie s obrázkom po podnikoch (pred/po), medián kratšej strany `image_url` po podnikoch (pred/po), akcie s `image_thumb` a `image_detail`, `status: cancelled` po podnikoch.
- Ručne over na webe 1 akciu na podnik (URL obrázka a rozmer) a zrušenie Omah Lay.
- Otvorené body.

## Report

**Dátum:** 2026-11-18. **Commity:** `0a6c0a3` (1. zrušenia Forum Karlín), `6f48afa` (2. obrázky zo stránok akcií), `5fa7f87` (3. náhľady 480 px, `image_detail`, ne-ASCII URL), `c0bb724` (5. rodičia podžánrov), `cffa0ec` (4. skript merania orezu), `ca9ecd9` (oprava: pri limite detailov ostáva obrázok z minulého behu), report + návrat limitu náhľadov na 150 v nasledujúcom commite. `pytest -q`: 538 passed; `npm test`: 199 passed.

**Behy:** ručný [44299322419](https://github.com/matejstolarik/eventapp/actions/runs/44299322419) (len časť 1; pipeline prebehla, deploy zlyhal na chybe GitHubu „No artifacts named github-pages“, nič sa nepublikovalo), [44301346294](https://github.com/matejstolarik/eventapp/actions/runs/44301346294) (časti 1–5, generated_at `13:26:34`), [44304250499](https://github.com/matejstolarik/eventapp/actions/runs/44304250499) (commit `cffa0ec`, doplnenie detailov nad limit 40, generated_at `2026-11-18T13:40:33+01:00`). **Čísla nižšie sú z behu 44304250499**, zhodné s `https://matejstolarik.github.io/eventapp/events.json`.

**Príkaz** (rozmery `image_url` sa čítajú stiahnutím prvých 256 kB obrázka, 1 požiadavka/s na web; skript je v scratchpade, nie v repe):
```
python stats066.py site/events.json dims.json        # "po" = beh 44304250499
python stats066.py events_before.json dims.json      # "pred" = beh 44202801880 (Pages pred 066)
python scripts/review/crop-rules.py                  # časť 4
```

### 1. Zrušené akcie Forum Karlín
- Adaptér rozpoznáva zrušenie aj podľa triedy `cancel` na karte zoznamu, riadku `ZRUŠENO` v `<p>` karty, `<div id="event" class="cancel">` a `<p class="zmena">ZRUŠENO</p>` v detaile; `.nalepka .msg` ostáva. Testy na uloženom HTML (`tests/fixtures/forumkarlin_program_20261118.html`, `forumkarlin_detail_omah_lay.html`).
- `events.json`: `forum-karlin-2026-11-18-omah-lay` má **`status: cancelled`**. Navyše sa našla druhá zrušená akcia **`forum-karlin-2027-01-30-original-enigma-voices-symphonic`** (`<div class="event cancel">`, `<p>The Next Chapter<br>ZRUŠENO</p>`). Overené na `https://www.forumkarlin.cz/program/` a `https://www.forumkarlin.cz/udalost/omah-lay/` (2026-11-18 12:53).
- Slepé miesta iných adaptérov (len grep, neopravené): **Archa+, Roxy, EPIC, Bike Jesus (API), Cross Club (RSS)** zrušenie vôbec nerozpoznávajú (`status` je vždy `scheduled`). **JSON-LD** (MeetFactory, Kasárna, Unijazz, Fuchs2) rozpozná len `eventStatus` obsahujúce „cancel“; `EventPostponed`/`EventRescheduled` sa neberú, text „ZRUŠENO“ na stránke tiež nie. **Akropolis** rozpozná zrušenie (kód 5), presun (kód 6) len zaloguje a nechá `scheduled`. (`fuchs2-2026-12-31-debasement` má `postponed` z inej cesty.)

### 2. Väčšie obrázky
Pravidlá po podnikoch v `pipeline/images.py` (rozhodnutie v `decisions.md`). Forum Karlín a Unijazz berú obrázok v adaptéri (detail sa už sťahuje, 0 požiadaviek navyše); EPIC má zo zoznamu farebný obrázok 620×360 ako zálohu (0 navyše). Ostatné: `detail_enrich` stiahne stránku akcie raz (limit 40 nových na podnik a beh), výber sa drží v `pipeline_state.json` → `detail_image` (268 záznamov). Beh 44301346294 stiahol 231 stránok, beh 44304250499 167 (časť z nich sa sťahuje kvôli cene a popisu aj tak).

**Čítareň Unijazz** (Matej mal pravdu): vlastný obrázok je v tele stránky ako `background-image` prvého prvku slidera (`.oxy-dynamic-list .ct-div-block`), nie v metadátach ani v `<img>`:
- `https://citarna.unijazz.cz/events/david-pillow-krest-jakub-eden/`: `2026/10/album-photoshoot-3.jpg` (1000×1000) + druhá fotka v slideri
- `https://citarna.unijazz.cz/events/freshwater-dogs-table-mountain-string-band/`: `2026/10/tmsb-Blavoj-Zvonimir.jpg` (1000×665)
- `https://citarna.unijazz.cz/events/jazzmanie-vladimira-kourila-274/`: `2026/11/DSC7763-scaled.jpg`
- `https://citarna.unijazz.cz/events/psytrance-united/`: slider prázdny, len spoločný `og:image` a logo, teda `null`

V behu má 8/16 akcií Unijazz vlastný obrázok, 8 slider nemá (`null`, predtým spoločný obrázok webu).

Pred/po na 2 akciách na podnik (rozmer stiahnutého obrázka):

| akcia | pred | po | obrázok po |
|---|---|---|---|
| archa-plus-2026-11-18-uvedeni-hry-andre-miri-cipa-v-moji-kuzi | 500×500 | 1920×640 | `archa-plus.cz/images/PressKit-KeyArt-Banner-3840x1280-NoLogo.png` |
| archa-plus-2026-11-19-jose-gonzalez | 500×500 | 1280×836 | `archa-plus.cz/images/gonzalez-press2.jpeg` |
| roxy-2026-11-18-vyprodano-colorfactory | 480×480 | 1400×480 | `roxy.cz/upload/temp/baner-colorfactory-…-1400-500.png` |
| roxy-2026-11-20-drum-bass-pilates | 480×480 | 667×500 | `roxy.cz/upload/temp/img-7878-…-1400-500.JPG` |
| meetfactory-2026-11-21-good-times-only-krest-desky-blue-uandi | 250×376 | 2048×3088 | `meetfactory.cz/media/images/GTO_PROMO_4_Kuba_Zeman.jpg` |
| meetfactory-2026-11-22-music-press-production-arab-strap | 250×250 | 640×640 | `meetfactory.cz/media/images/ab6761…da14eb.jpeg` |
| cross-club-2026-11-19-up-tone-w-marathon | 150×150 | 2048×1073 | `crossclub.cz/files/2026/listopad/up.jpg` |
| cross-club-2026-11-20-moordoor | 150×150 (fotka interiéru z cache) | 1735×907 | `crossclub.cz/files/2026/listopad/mord.jpg` |
| palac-akropolis-2026-11-20-vltava-sto-let-s-vami | 480×288 | 590×393 | `…/Vltava_40_let_web_event.jpg` |
| palac-akropolis-2026-11-21-claptrap-fr | 480×288 | 590×472 | `…/Claptrap___Tristan_d_Hervez_2_web_event.jpg` |
| epic-2026-11-20-slvl | – | 1080×1080 | `epicprague.com/upload/temp/events/1000x1000-irg2gp5zj6-1920-1080.png` |
| epic-2026-11-21-video-oldies-ruda-tuceka | – | 1080×1080 | `…/1000x1000-nl32l263vc-1920-1080.png` |
| forum-karlin-2026-11-18-omah-lay | 600×300 | 1920×640 | `forumkarlin.cz/wp-content/uploads/2026/07/2400x800.png` |
| forum-karlin-2026-11-21-stahlzeit | 600×300 | 1920×640 | `…/2025/09/Stahlzeit_2400x800_fkcrop.jpg` |
| citarna-unijazz-2026-11-19-jakub-eden-krest-debutoveho-alba | 2560×1675 (spoločný) | 1000×1000 | `…/2026/10/album-photoshoot-3.jpg` |
| citarna-unijazz-2026-11-24-freshwater-dogs-… | 2560×1675 (spoločný) | 1000×665 | `…/2026/10/tmsb-Blavoj-Zvonimir.jpg` |

Ručné overenie na webe (stránky stiahnuté 2026-11-18, uložené v `tests/fixtures/img066/`): každý riadok vyššie je URL nájdená na stránke akcie (`og:image`, banner, lightbox, galéria, slideshow, slider), rozmer zistený stiahnutím. Roxy `https://www.roxy.cz/events/detail/5143/lambrini-girls` má aj na stránke len `no-image-1400-500.png`, preto `null`.

### 3. Náhľady a `image_detail`
- `thumbs.py`: URL sa pred stiahnutím kódujú (`urllib.parse.quote`), test na cyrilickom `х`, ZWJ a `ö`. Všetky akcie Forum Karlín a MeetFactory s obrázkom majú teraz `image_thumb` (v 064 chýbal pri 4 + 1).
- Náhľad 480×480 (stredový štvorec), nové pole `image_detail` (`img/events/detail/<id>.jpg`, bez orezu, dlhšia strana ≤ 1200 px, nezväčšuje sa), zapísané v `data-model.md`. Jedno stiahnutie pre oba súbory; hash obsahuje veľkosť výstupu, takže sa raz prepočítalo všetko. Limit stiahnutí za beh **jednorazovo 400 (inak 150)** pre behy 44301346294 a 44304250499; v commite s reportom vrátený na 150. Prvý beh new=330, druhý new=64 / cache=269; adresár náhľadov 39,2 MB.
- **2 obrázky EPIC sa nedajú dekódovať** (`epic-2026-11-19-almost-weekend`, `epic-2026-12-13-sunday-rituals-urban-music`): PNG na serveri sú neúplné (stiahne sa celá dĺžka podľa `content-length`, Pillow hlási „image file is truncated“). `image_url` ostáva, `image_thumb` aj `image_detail` sú `null`. Neopravené.

### Čísla (beh 44304250499 vs. pred 066 = beh 44202801880)

| podnik | akcie | s obrázkom pred → po | medián kratšej strany pred → po | `image_thumb` | `image_detail` | `cancelled` |
|---|---|---|---|---|---|---|
| palac-akropolis | 85 | 84 → 85 | 288 → 393 | 85 | 85 | 0 |
| archa-plus | 60 | 60 → 60 | 500 → 1076 | 60 | 60 | 0 |
| roxy | 44 | 41 → 37 (3 zástupné + 4 nové bez obrázka na webe = `null`) | 480 → 480 (banner 1400×480) | 37 | 37 | 0 |
| meetfactory | 35 | 35 → 35 | 250 → 1366 | 35 | 35 | 0 |
| epic | 35 | 0 → 35 | – → 1080 | 33 | 33 | 0 |
| bike-jesus | 25 | 0 → 0 | – | 0 | 0 | 0 |
| forum-karlin | 24 | 24 → 24 | 300 → 640 | 24 | 24 | **2** |
| fuchs2 | 20 | 21 → 20 | 1080 → 1080 | 20 | 20 | 0 |
| citarna-unijazz | 16 | 16 → 8 (spoločný obrázok = `null`) | 1675 → 1534 | 8 | 8 | 0 |
| cross-club | 15 | 15 → 14 (logo = `null`) | 150 → 982 | 14 | 14 | 0 |
| kasarna-karlin | 15 | 15 → 15 | 4500 → 4500 | 15 | 15 | 0 |
| **spolu** | 374 | 311 → 333 | | 331 | 331 | 2 |

(„Pred“ bolo 372 akcií; Roxy „pred“ 41 obrázkov vrátane 3 zástupných.) Akropolis: 79/85 už má `_web_event`, 6 ešte `_web_hp` (limit 40 detailov za beh, doplní najbližší denný beh).

### 4. Meranie pravidiel orezu (nič neimplementované)
Skript `scripts/review/crop-rules.py` na variantoch hárku 064 (lokálna cache `docs/tasks/064/sheet/v/`) a `docs/tasks/064/choices.json` (236 volieb). **Vynechané sú štvorcové obrázky (0,95 ≤ š/v ≤ 1,05), 61 riadkov**: stred, tváre aj zhora sú tam ten istý štvorec. Pravidlo sa navyše počíta ako zhoda, keď je jeho variant prakticky zhodný s voleným (priemerný rozdiel pixelov < 2 z 255; napr. „zhora“ pri obrázku na šírku je to isté ako „stred“). Porovnaných 175.

| pravidlo | zhoda | % |
|---|---|---|
| R1 vždy stred | 120/175 | 69 % |
| R2 na výšku zhora | 114/175 | 65 % |
| R3 | 30/175 | 17 % |
| R4 | 35/175 | 20 % |

Po pomere strán (zhody R1/R2/R3/R4): na výšku 23: 13/7/7/7 · na šírku 127: 94/94/16/16 · banner 25: 13/13/7/12. Voľby Mateja: na výšku stred 13, zhora 7, tváre 3; na šírku „zhora“ (= stred) 64, stred 30, celý 29, tváre 4; banner „zhora“ (= stred) 11, celý 8, tváre 4, stred 2.

Najlepšie je R1; 10 prípadov, kde nesedí (spolu 55):

| id | pomer š/v | tváre | voľba Mateja | R1 |
|---|---|---|---|---|
| meetfactory-2026-11-25-cancer-house-kailas | 0,72 na výšku | 0 | zhora | stred |
| meetfactory-2026-12-01-shaking-hand-wreckberries | 0,75 na výšku | 2 | zhora | stred |
| meetfactory-2026-12-06-satoshi-viva-moldova-europe-tour | 0,74 na výšku | 1 | zhora | stred |
| meetfactory-2026-12-11-selection-mighty-oaks-june-carousel | 1,51 na šírku | 3 | celý | stred |
| meetfactory-2027-02-16-live-nation-look-mum-no-computer | 0,76 na výšku | 1 | zhora | stred |
| meetfactory-2027-02-21-rfp-concerts-dead-poet-society | 1,24 na šírku | 4 | tváre | stred |
| meetfactory-2027-02-28-protomartyr | 1,52 na šírku | 0 | celý | stred |
| meetfactory-2027-04-02-fource-nieve-ella | 0,56 na výšku | 1 | zhora | stred |
| meetfactory-2026-12-12-michel-houellebecq-serotonin | 0,67 na výšku | 1 | tváre | stred |
| meetfactory-2026-12-19-oliver-lovrenski-kdyz-nam-bylo-min | 0,67 na výšku | 4 | tváre | stred |

Pozor: hárok 064 vznikol z menších alebo už orezaných zdrojov (Archa a Roxy štvorce, MeetFactory 250 px). S väčšími obrázkami z časti 2 sa pomery strán zmenia (Archa, Roxy, Forum Karlín sú teraz väčšinou na šírku alebo banner), takže meranie by sa oplatilo zopakovať na novom hárku.

### 5. Rodičia podžánrov (na Matejovu kontrolu)
Pridané do `data/genre_hierarchy.json`:
- `tech-house` → `house`
- `death-metal` → `metal`
- `metalcore` → `metal`
- `grindcore` → `metal`, `punk`
- `goregrind` → `grindcore`
- `jungle` → `drum-and-bass`
- `dubstep` → `bass-music`
- `uk-bass` → `bass-music`
- `bassline` → `uk-garage`
- `dancehall` → `reggae`
- `dub` → `reggae`
- `ebm` → `industrial`
- `orchestral` → `classical`

`deep-house`, `afro-house`, `minimal-techno` ani `black-metal` v zozname žánrov nie sú. Bez rodiča som nechal nejednoznačné: `hardcore` (punk aj techno), `edm`, `electro`, `synthwave`, `electro-swing`, `hardstyle`, `breakbeat`, `grime`, `rave`. Dôsledok C7: `metal` vedľa `metalcore` sa teraz vyhodí (upravené 2 testy). Test konzistencie prechádza.

### Rozhodnutia urobené samostatne
- Unijazz: obrázok z prvého prvku slidera; akcia bez slidera má `null` (nie spoločný obrázok webu).
- EPIC: obrázok zo stránky akcie (1080 px) má prednosť, zoznam je len záloha 620×360 (farebná verzia; sivá je hover).
- Cross Club: odkaz lightboxu (originál `/files/…`, overené 200 OK a rozmery), inak `420x0-`.
- Výber obrázka zo stránky sa drží v `pipeline_state.json` (`detail_image`), nie v `events.json` (dátový model sa nemení); detail sa znova nesťahuje, kým sa nezmení URL stránky.
- Limit detailov 40 na podnik a beh som nezvyšoval; Akropolis dobehne v najbližšom dennom behu.

### Otvorené
- 6 akcií Akropolis ešte so starým `_web_hp` (doplní najbližší denný beh).
- 2 neúplné PNG na serveri EPIC, preto bez náhľadu.
- Zrušenia a presuny v ostatných adaptéroch (viď časť 1), neopravené.
- Zobrazenie v appke (orez v mriežke, `image_detail` v detaile) čaká na návrh; meranie orezu zopakovať na väčších obrázkoch.
- Náhľad podniku Cross Club: v behu `thumbs: cross-club — HTTP Error 404` (obrázok podniku vo `venues.json`, nesúvisí s 066, neriešené).
