# 085: Nové podniky – dávka 1 (Lucerna Music Bar, O2 arena, O2 universum, Jazz Republic)

## Zadanie

**Schválené Matejom 2026-11-20 22:50** (po prieskume 083). Mení dáta → **jeden beh pipeline na konci**, raz počkaj. Čo nie je jasné, spýtaj sa.

**Čítaj:** report úlohy **083** (sekcie Tabuľka, Dôležité zistenia, Riziká – to je zdroj pravdy o weboch), fixtures `tests/fixtures/survey2/` (Lucerna, O2, Jazz Republic), existujúce adaptéry ako vzor (`pipeline/adapters/html_forum_karlin.py`, `html_roxy.py`, `jsonld.py`), `docs/data-model.md` (miesto, akcia, veľkosť miesta, `doors_time`), `data/venues.json` (vzor záznamu), `docs/venue-capacity.md`. `docs/decisions.md` – `grep -n` „GoOut“, „obrázky“, „cudzích priestoroch“, „doors“.

**Pravidlá:** každý zdroj = samostatný adaptér `fetch(venue, source_config) -> list[RawEvent]`; limit požiadaviek a časový limit na zdroj; detail akcie len pre nové/zmenené akcie (cache), nie každý deň všetky; nič nedomýšľať (`null`); dátum a čas ako pražský miestny čas. Ak sa web od fixtures z 083 líši tak, že plán nesedí (iný typ zdroja, JS), **zastav a napíš** (`CLAUDE.md`).

### Rozhodnutia Mateja (z 083)
1. **Šport na O2 sa nepridáva** (HC Sparta, OKTAGON, florbal, jazdectvo, nohejbal…) – vyradiť podľa „Typ akce“ v detaile alebo filtra `/filter/sport/`; vyradené logovať.
2. **Obrázky Lucerna Music Bar z CDN GoOut (`static.goout.cloud/…`) sa berú** – je to vlastný web podniku (rozhodnutie 2026-11-17 „obrázky z GoOut nie“ platí pre stránky goout.net, nie pre web podniku). Zapíš do `docs/decisions.md`.
3. Bez času začiatku: **ak je len otvorenie (Jazz Republic 20:00), ukáž otvorenie** ako pri MeetFactory (`doors_time`, `start_time` null); inak čas prázdny.

### 1. Lucerna Music Bar
- Zdroj `https://musicbar.cz/cs/program/` (HTML). **Čas vo výpise = otvorenie, `data-start` = začiatok** (083: líši sa v 71 zo 74) → `doors_time` + `start_time`. Vypredané = `.sold-out` → `sold_out: true`. JSON-LD v detaile je neplatný JSON – nespoliehať sa naň (len ak ho opravíš tolerantne, inak HTML). Velký sál (lucerna.cz) sa nepridáva – musicbar.cz má len akcie Music Baru (overené v 083).

### 2. O2 arena + O2 universum (jeden adaptér, dve miesta)
- Zdroj `https://www.o2arena.cz/events/` (a/alebo `o2universum.cz/events/`): **stránka obsahuje obe sekcie** → priradiť akciu miestu podľa sekcie (`<h2 class="toLeft">`) alebo domény odkazu. Žiadna akcia nesmie byť dvakrát.
- **JSON-LD v detaile má chybnú zónu `+00:00`** pri pražskom čase → brať len miestnu časť (20:00 = 20:00 v Prahe). Otvorenie z detailu do `doors_time`, ak je.
- **Karta s viacerými termínmi** (napr. 4. + 5. 12.) = samostatná akcia pre každý termín.
- Cena „od–do“ z detailu, ak je; inak `null`.

### 3. Jazz Republic
- Zdroj `https://www.jazzrepublic.cz/cz/program` (v 008 bolo 404, v 083 už 200). Výpis `li.indexlist1`: dátum ISO v URL (`/cz/program/2026-11-21-…`), názov, obrázok. Detail: otvorenie (napr. 20:00–24:00) → `doors_time`, zostava a popis. Cenu / voľný vstup len ak je uvedená na stránke (nepredpokladať).

### 4. Záznamy vo `venues.json` (vzor ako existujúce miesta)
| Pole | Lucerna Music Bar | O2 arena | O2 universum | Jazz Republic |
|---|---|---|---|---|
| `capacity` | **1000** (Matej) | **20000** (web, 083) | **5200** (Sál A, Matej; celý komplex ~10 000) | **150** (Matej: odhad z plánu stolov, 130 miest + pár navyše) |
| `instagram` | `lucernamusicbar` | `o2arenapraha` | `o2universum` | `jazzrepublic` |
| `image_url` | og:image z 083 (CDN GoOut, povolené) | default FB 1200×630 z 083 | default FB 1200×630 z 083 | fotka 600×400 z 083 |
- `size` podľa kapacity a pravidla v `docs/data-model.md`; do `notes` zdroj kapacity („Matej 2026-11-20“ / URL).
- Adresa a súradnice z oficiálneho webu / OSM (ako v úlohe 009, nie Google Maps). `ra_url` nie (web na RA neodkazuje).
- `type`, `character`, `music`: **návrh** podľa programu (ako úloha 013) – v reporte tabuľka na schválenie Matejom; do `venues.json` daj návrh, Matej ho potvrdí alebo opraví. `closing` (zatváracie časy) z webu, ak sú; inak `null` a napíš to (Matej doplní).
- `description`: `null` (popisy píše Matej).

### 5. Upozornenie na chýbajúci obrázok miesta (Matej 2026-11-20)
- Pravidlo: každá akcia má obrázok (plagát, inak obrázok miesta) → **každé aktívne miesto musí mať obrázok**. V systéme upozornení z 057: keď aktívne miesto nemá `image_url` alebo sa jeho obrázok nepodarí stiahnuť (`image_card` null), vznikne/aktualizuje sa GitHub issue `alert` (rovnako ako iné upozornenia, bez duplicít). Test.

### 6. AI doplnenie pre celý polrok (Matej 2026-11-20 23:07)
- **Okno plného AI doplnenia (`enrich_ai.WINDOW_DAYS`) z 60 na 180 dní** – rovnako ako okno akcií v appke. Platí pre všetky miesta (aj doterajších 11).
- **Opakované hľadanie raz pri vstupe do 60 dní:** akcia doplnená skôr ako 60 dní pred konaním, ktorej po doplnení chýba cena alebo žánre (prípadne čas), sa **raz** znova doplní, keď sa dostane do 60 dní (dôvod: pri vzdialených akciách často ešte nie je zverejnená cena ani zostava a dnešná cache by ich už nikdy znova nehľadala). Raz = označiť v zázname, aby sa neopakovalo každý deň. Testy.
- **Jednorazovo vyšší limit behu** pri behu na konci tejto úlohy (napr. premenná prostredia / vstup workflowu `ai_budget_usd`, predvolene 0,30 $), aby sa nové akcie aj akcie za doterajšími 60 dňami doplnili naraz; Matej pred spustením dobije DeepSeek. Zapíš, akú hodnotu si použil a koľko beh reálne stál.
- **Mesačný limit** ostáva, kým ho Matej nezmení (návrh hlavného chatu: z 3 $ na 5 $ – čaká na Matejov súhlas; ak ho v zadaní nevidíš potvrdený, nemeň ho). Ak by mesačný limit zastavil doplnenie, napíš to do reportu.
- Do `docs/decisions.md`: nové okno, pravidlo opakovaného hľadania (nahrádza 60-dňové okno z úloh 054/062/063).

## Overenie a report
- Testy adaptérov na fixtures z 083 (`pytest -q`), vrátane: O2 oddelenie arena/universum, vyradenie športu, viac termínov, zóna `+00:00`; Lucerna otvorenie vs. začiatok, vypredané; Jazz Republic dátum z URL, `doors_time`.
- **Jeden beh pipeline** (číslo). Z publikovaného `events.json` (príkaz uveď): počet akcií po novom mieste, koľko má čas/otvorenie/cenu/plagát, koľko vyradeného športu; koľko akcií (všetkých miest) bolo v tomto behu AI doplnených, koľko čaká (rozpočet), koľko stál beh a koľko je minuté za mesiac.
- Overenie na webe: 2 akcie z každého miesta (URL, dátum, čas, názov) proti `events.json`.
- Tabuľka návrhu štítkov (`type`, `character`, `music`, `size`) na schválenie.
- Snímka `docs/tasks/085/events-new-venues.jpg` (Akcie, Kedykoľvek, filter na nové miesta, 390 × 844).
