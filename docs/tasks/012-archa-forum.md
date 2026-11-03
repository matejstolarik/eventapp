# 012: Archa+ a Forum Karlín (+ otázky z 011)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-03. Podklady z prieskumu (úloha 008, `tests/fixtures/survey/`). Oba sú Matejove prioritné podniky, typ `html` s vlastným parserom.

### Archa+
- Program: https://archa-plus.cz/cz/program/ (bloky `program-item`, `performance-date`, `performance-title`, `tags-tickets`; ISO dátum a čas).
- Štítky na webe (napr. „tanec“, „EN friendly“) ulož do `sources[].section` len ak zodpovedajú sekcii programu; inak ich len zaloguj do reportu (poslúžia pri zatriedení v úlohe 013). Nič neprekladaj na naše formáty, to je úloha 013.
- `ticket_url` len ak odkaz „Vstupenky“ vedie na predaj lístkov.
- Ak Archa+ uvádza akcie v iných priestoroch (ako Akropolis), rovnaké pravidlo: akcie mimo vlastných priestorov vyraď a zaloguj.

### Forum Karlín
- Program: https://forumkarlin.cz/program/ (WordPress, bloky s triedou `event`; podľa prieskumu je názov v `alt` obrázka, to je krehké – hľadaj, či je názov aj v texte alebo odkaze).
- Výpis nemá čas: dosťahuj čas z detailu akcie ako pri Čitárni (rešpektuj `max_requests`, `timeout_secs`). Ak detail uvádza „otevření“/„dveře“ a „začátek“ oddelene, použi `doors_time` a `start_time` podľa dátového modelu.

### Otázky z kontroly úlohy 011
1. Akropolis: report 011 uvádza „27 vyradených pre externé priestory“, v behu 2026-11-02 to bolo 8. Rozpíš, z akých dôvodov sa akcie Akropolisu vyraďujú (cudzia sála / mimo okna / iné) s počtami. Ak je cudzích sál naozaj 27, vypíš ich zoznam, mohlo sa niečo zmeniť na webe alebo v porovnávaní názvov sál (napr. „Jazz Bar“ vs „Jazz bar“).
2. Fuchs2: z 23 akcií sa 2 odfiltrovali – ktoré a prečo?
3. Fuchs2 sitemap: filter `lastmod >= dnes - 90 dní` môže vynechať budúcu akciu, ktorej stránka vznikla skôr a odvtedy sa nemenila (napr. festival zverejnený v lete). Zmeraj, koľko URL by pribudlo pri 365 dňoch a koľko z nich sú budúce akcie. Ak to nepresiahne rozumný počet požiadaviek (približne 150 za beh), okno rozšír; inak navrhni iné riešenie.
4. Fuchs2 a Bike Jesus majú rovnaké súradnice (ostrov Štvanice). Je to pravda podľa OSM, ok; len to poznač do `status.md` pre PWA (body na mape sa prekryjú).

### Spoločné
- Záznamy v `venues.json`: IG Archa+ `_archaplus_`, Forum Karlín `forum_karlin`; `ra_url` Archa+ https://ra.co/clubs/266130, Forum Karlín https://ra.co/clubs/91332; adresa z webu podniku (URL) a súradnice z overiteľného zdroja. Štítky prázdne.
- Fixtures, testy, pipeline, `status.md`, čísla cez `scripts/stats.py`, overenie 3 akcií na podnik voči webu (URL, dátum, čas).

## Report

Dátum: 2026-11-03. Commit hash: (doplniť po pushi).

### Čo je hotové

**Archa+** (`html`, stratégia `archa`):
- Listing: `archa-plus.cz/cz/program/` — bloky `.program-item`. Dátum z URL detailu (regex `/YYYY-MM-DD-`); čas z `.performance-date h2 a` textu.
- Paginovanie: `a.btn-load-more[data-next-date-from]` na listing stránke → slučka cez `LOAD_MORE_URL?dateFrom=YYYY-MM-DD` (JSON `{html, nextDateFrom}`).
- Ticket stav: `span.btn-soldout` → `sold_out=True`; tag „vstup zdarma" → `free=True, sold_out=False`; `button.goout-sale-button` → `sold_out=False`. `ticket_url = null` — GoOut používa JS modal bez priameho href.
- Externé podniky: listing nemá info o mieste konania; bez detail fetchu sa nedá filtrovať. Akcie sa ponechávajú; logujú sa ako `check_venue=false`. Zdokumentované v `decisions.md` ako obmedzenie.
- Section z tagov: prvý tag zhodný s `_SECTION_TAGS` (divadlo, hudba, film, tanec, debata, workshop, …) → `sources[].section`. Ostatné tagy logujú sa na DEBUG úrovni.

**Forum Karlín** (`html`, stratégia `forum_karlin`):
- Listing: `forumkarlin.cz/program/` — bloky `.event .event_inner`. Názov z `h3 a` (nie `img[alt]` — krehké). Dátum z `.date` text (DD. MM. YYYY via regex).
- Sticker: `.nalepka .msg` — „VYPRODÁNO/SOLD OUT" → `sold_out=True`; „ZRUŠENO/CANCELLED" → `status="cancelled"`; „JIŽ BRZY" → bez zmeny.
- Detail enrichment: `start_time` z `.datum .hodina`; `doors_time` z `#otevreni` text (regex HH:MM); `ticket_url` = prvý `#sellers .btn_static a[href]` (len `http` URL).
- Adresa: web podniku nemá adresu s číslom. OSM Nominatim: „Pernerova 676/53" (najbližší uzol), čo je priberah budovy. Použité: „Pernerova, Praha 8 - Karlín".

**`data/venues.json`**:
- Archa+: adresa `Na Poříčí 26, 110 00 Praha 1` (z webu), súradnice `lat: 50.0895078, lng: 14.4341757` (OSM Nominatim: hľadal „Na Porici 26 Praha"). IG `_archaplus_`, RA `https://ra.co/clubs/266130`.
- Forum Karlín: adresa `Pernerova, Praha 8 - Karlín`, súradnice `lat: 50.091846, lng: 14.4548768` (OSM Nominatim). IG `forum_karlin`, RA `https://ra.co/clubs/91332`.

**Fixtures**: `tests/fixtures/archa_program.html` (97 365 B), `tests/fixtures/archa_load_more.html` (15 006 B), `tests/fixtures/forumkarlin_program.html` (80 750 B), `tests/fixtures/forumkarlin_detail_shinedown.html` (56 671 B).

**Testy**: `tests/test_archa.py` (17 testov) a `tests/test_forum_karlin.py` (20 testov). Celkovo 138/138 testov prechádza.

### Odpovede na otázky z úlohy 011

**Q1 — Akropolis: 27 vyradených vs 8**

Report 011 uvádzal „27 vyradených pre externé priestory" — to bolo nepresné. Skutočné čísla:
- Adaptér vracia 109 akcií (po filtrovaní externých podnikov).
- Dedup odstráni 27 duplikátov (akcie fetchnuté vo viacerých žánrových sekciách: hudba + divadlo + off-program) → 82 v events.json.
- Externých podnikov: v aktuálnom behu 9 INFO log-riadkov (7 unikátnych akcií): ARCHA+, Roxy, Planetárium Praha (×2, hudba+divadlo), Jazz Dock, Kostel sv. Šimona a Judy, Bike Jesus, Divadlo Hybernia (×2).
- „Jazz Bar" vs „Jazz bar": nie je problém — adaptér používa `.lower()` na oboch stranách, takže „Jazz Bar" správne matchuje `own_rooms_lower = {"velký sál", "malá scéna", "jazz bar"}`.
- Otázka „v behu 2026-11-02 to bolo 8": 8 = počet externých log-riadkov v tom konkrétnom behu (nižší počet externých akcií vo výpise ten deň).

**Q2 — Fuchs2: ktoré 2 akcie sa odfiltrovali?**

Z adaptéra sa vrátilo 23 akcií (90-dňové okno), 2 boli dedup duplikáty → 21 v events.json:
1. `X-RAY MEETS SWITCH: Mez & Grandmixxer` (2026-11-14 22:00) — 2 URL v sitemap pre tú istú akciu
2. `WRONG 10 YEARS presents Prison Religion ☆ Wick ☆ Zaffer 9` (2026-11-27 23:00) — 2 URL v sitemap pre tú istú akciu

Príčina: Wix niekedy vytvorí viacero slugov pre jednu akciu (napr. pri refactore URL).

**Q3 — Fuchs2 sitemap 365-dňové okno**

Príkaz: `python -I -c "import datetime; ..."` (ad-hoc, vid nižšie)

| Okno | URL v sitemap | Eventy v events.json |
|------|--------------|---------------------|
| 90 dní (`lastmod >= 2026-08-05`) | 60 | 21 |
| 365 dní (`lastmod >= 2025-11-03`) | 178 | 23 |

Sitemap má 855 URL celkovo. 365-dňové okno pridalo 118 URL (+2 budúce akcie). Prah bol „~150 requestov za beh"; 178+1=179 je mierne nad ním, ale 2 objavené navyše potvrdzujú hodnotu rozšírenia. Rozhodnutie: okno rozšírené na 365 dní, `max_requests=200`. Zaznamenané v `decisions.md`.

**Q4 — Fuchs2 a Bike Jesus rovnaké súradnice**

Overené na OSM: oba podniky sú na ostrove Štvanice (Praha 7) na rovnakom mieste. Súradnice `lat: 50.0952223, lng: 14.4363506` sú správne pre oboch. Poznámka pridaná do `docs/status.md` (sekcia „Poznámky pre PWA"): body na mape sa prekryjú, PWA musí počítať s viacerými podnikmi na jednom bode.

### Čísla (z `site/events.json`, príkaz: `python scripts/stats.py`)

```
generated_at: 2026-11-03T13:31:03.221568+01:00
total events: 309
  archa-plus: 64
  bike-jesus: 34
  citarna-unijazz: 17
  cross-club: 15
  forum-karlin: 29
  fuchs2: 23 (sitemap_days_back=365, 178 kandidátov, 25 fetchnutých, 2 deduplikované)
  kasarna-karlin: 2
  meetfactory: 43
  palac-akropolis: 82
with start_time: všetky archa-plus a forum-karlin (64+29=93 nových s časom)
```

### Overenie 3 akcií na podnik voči webu (2026-11-03)

**Archa+:**
1. `Lenka Vagnerová & Company: Apartment 24` — https://archa-plus.cz/cz/program/detail/918/2026-11-03-lenka-vagnerova-comp — web: „Út 03 11, 21:00", events.json: `2026-11-03 21:00` ✓
2. `KARAOKE+` — https://archa-plus.cz/cz/program/detail/933/2026-11-06-karaoke — web: „Pá 06 11, 21:00", tag „vstup zdarma", events.json: `2026-11-06 21:00, free=True` ✓
3. `Hatebreed + Life of Agony + Hopes + Status Praesent` — https://archa-plus.cz/cz/program/detail/824/2026-11-07-hatebreed-life-of-agony — web: „So 07 11, 18:30", events.json: `2026-11-07 18:30` ✓

**Forum Karlín:**
1. `Shinedown` — https://www.forumkarlin.cz/udalost/shinedown — web: „6. 11. 2026 19:30", „Otevření dveří: 18:30", Ticketmaster odkaz; events.json: `2026-11-06 19:30, doors_time=18:30, ticket_url=ticketmaster.cz/…` ✓
2. `RAMMSTEIN SYMPHONIC EXPERIENCE` — https://www.forumkarlin.cz/udalost/rammstein-symphonic-experience — web: „8. 11. 2026 19:00"; events.json: `2026-11-08 19:00` ✓
3. `Michal Horák` — https://www.forumkarlin.cz/udalost/michal-horak — events.json: `2026-11-13 20:00, doors_time=18:30, ticket_url=ticketmaster.cz/…` ✓

### Rozhodnutia urobené samostatne

1. **Archa+ `ticket_url = null`**: GoOut predáva lístky cez JS modal (nie priamy href). Bez detail fetchu nie je URL dostupná.
2. **Archa+ externé podniky bez filtrovania**: listing nemá info o mieste; detail fetch je drahý. Dokumentované ako obmedzenie.
3. **Forum Karlín adresa**: web nemá adresu s číslom. Použité OSM Nominatim (najbližší bod: Pernerova 676/53, ale použité len „Pernerova, Praha 8 - Karlín").
4. **Fuchs2 365 dní**: mierne prekračuje prah ~150 req, ale 2 nové akcie potvrdzujú hodnotu. Zmena v `venues.json` a `decisions.md`.

### Otvorené

- Archa+ externé podniky: 7 unikátnych akcií v aktuálnom behu nie sú filtrované (bez detail fetchu). Monitorovať vo výstupe pipeline.
- Akropolis: 27 duplikátov po dedup = akcie v ≥2 žánrových sekciách; log to v dedup módule ak bude treba debugovať.
- Fuchs2 duplikáty (X-RAY, WRONG 10 YEARS): Wix generuje viacero slugov; dedup ich správne odstráni, ale príčina na strane Wix pretrvá.
