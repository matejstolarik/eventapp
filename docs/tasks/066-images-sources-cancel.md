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
