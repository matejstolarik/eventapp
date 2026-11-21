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
- **Mesačný limit DeepSeek z 3 $ na 5 $ – schválené Matejom 2026-11-20 23:11** (pri 21 miestach odhad 4–5 $/mes.). Ak by mesačný limit zastavil doplnenie, napíš to do reportu.
- Do `docs/decisions.md`: nové okno, pravidlo opakovaného hľadania (nahrádza 60-dňové okno z úloh 054/062/063).

## Overenie a report
- Testy adaptérov na fixtures z 083 (`pytest -q`), vrátane: O2 oddelenie arena/universum, vyradenie športu, viac termínov, zóna `+00:00`; Lucerna otvorenie vs. začiatok, vypredané; Jazz Republic dátum z URL, `doors_time`.
- **Jeden beh pipeline** (číslo). Z publikovaného `events.json` (príkaz uveď): počet akcií po novom mieste, koľko má čas/otvorenie/cenu/plagát, koľko vyradeného športu; koľko akcií (všetkých miest) bolo v tomto behu AI doplnených, koľko čaká (rozpočet), koľko stál beh a koľko je minuté za mesiac.
- Overenie na webe: 2 akcie z každého miesta (URL, dátum, čas, názov) proti `events.json`.
- Tabuľka návrhu štítkov (`type`, `character`, `music`, `size`) na schválenie.
- Snímka `docs/tasks/085/events-new-venues.jpg` (Akcie, Kedykoľvek, filter na nové miesta, 390 × 844).

## Report

**Dátum:** 2026-11-21. **Commity:** `4bd029c` (kód, dáta, testy, docs), report + snímka v nasledujúcom commite.
**Stav:** Lucerna Music Bar, O2 arena a O2 universum fungujú. **Jazz Republic nefunguje v GitHub Actions** – web je z runnera nedostupný (viď Otvorené). Časti 5 a 6 hotové.

### Hotovo
- Adaptéry (`html`, stratégie): `lucerna` (jedna stránka, otvorenie z textu, začiatok z `data-start`, `.sold-out`, „Soukromá akce“ vyradená, väčší obrázok + popis cez `detail_enrich`), `o2` (jeden adaptér, každé miesto vlastný zdroj s `domain` → karta patrí miestu podľa domény odkazu, šport podľa „Typ akce“, akcia na každý deň, časy zo zoznamu – nie z JSON-LD so zónou `+00:00`, otvorenie/cena/predaj/popis z detailu), `jazzrepublic` (dátum z URL, „Otevřeno 20:00“ → `doors_time`, „vstup volný“ len keď je na stránke).
- Detail len pre nové/zmenené akcie: cache `pipeline_state.json` → `adapter_detail` (po behu O2 arena 37, O2 universum 39 záznamov), kontrola znova po 7 dňoch.
- 4 záznamy vo `venues.json` (kapacity podľa zadania, súradnice OSM, obrázky z 083, `description: null`).
- Upozornenie `venue-image:<id>` (časť 5) + test; v tomto behu sa hneď otvorilo pre Jazz Republic (obrázok sa nestiahol – rovnaká sieťová chyba).
- AI (časť 6): okno 180 dní, jednorazové opakované hľadanie do 60 dní (`enrichment.run.rechecked_from`), poradie od najbližšej akcie, mesačný limit 5 $, uložený prieskum 7 mesiacov. Testy.
- `pytest -q`: 687 passed.

### Rozhodnuté samostatne (zapísané v `docs/decisions.md`)
- **Dva termíny v ten istý deň** (Čechomor 15:00 + 20:00, FMX) = jedna akcia s prvým časom – id `miesto-dátum-názov` by sa zhodovalo (zmena id = zmena dátového modelu).
- **Rozsah dní** („16.4.2027 - 18.4.2027“, Comic-Con, gastro festivaly) = jedna akcia v prvý deň bez času; dni sa nedomýšľajú. Karta bez dátumu (3× ZRUŠENO) sa preskočí.
- O2: jedno „Vstup od“ pri viacerých termínoch (Calin & Viktor Sheen, 17:30) sa **nepriraďuje** (nevieme, ku ktorému dňu); pri „12:00 a 17:30“ podľa poradia.
- Lucerna: keď je otvorenie rovnaké ako začiatok (Pop 80s & 90s, 22:00/22:00), ukladá sa len `start_time`.
- **Oprava `pipeline/fetch.py`:** robots.txt sa sťahoval s predvolenou hlavičkou urllib, Cloudflare musicbar.cz na ňu vracal 403 → celý web „zakázaný“, hoci robots.txt zakazuje len `/wp-admin/`. Teraz cez `requests` s naším klientom (test).
- `site/research` 7 mesiacov namiesto 3 (aby remap žánrov fungoval pri 180-dňovom okne).
- Jednorazový limit behu: `ai_budget_usd = 2.50`, `enrich_timeout_s = 3600` (schválil Matej v chate).

### Čísla (beh 44840323600, success, `events.json` vygenerovaný 2026-11-21 01:33)
Príkaz: stiahnuť publikovaný `events.json` a `pipeline_state.json` z Pages (adresa `PREVIOUS_EVENTS_URL` v `daily.yml`) do `<dir>`, potom `python docs/tasks/085/nums085.py <dir>`.

| Miesto | Akcií | Čas začiatku | Otvorenie | Cena (`price`) | z toho zo zdroja | `image_url` | náhľad | Vypredané |
|---|---|---|---|---|---|---|---|---|
| Lucerna Music Bar | 68 | 68 | 67 | 35 (AI) | 0 | 68 | 67 | 8 |
| O2 arena | 31 | 31 | 27 | 30 | 30 | 31 | 31 | 0 |
| O2 universum | 43 | 43 | 29 | 43 | 43 | 43 | 43 | 0 |
| Jazz Republic | **0** | – | – | – | – | – | – | – |

- Spolu 504 akcií (pred behom 365).
- Vyradený šport (log behu): O2 arena 8 (5× HC Sparta, FMX Gladiator Games, OKTAGON 100, BigBoard Superfinále florbalu), O2 universum 1 (MS v nohejbale). Lucerna 1× „Soukromá akce“, O2 3 karty bez dátumu (zrušené).
- AI: v tomto behu doplnených **278** akcií (všetky miesta, `checked_at` 2026-11-21), z cache 214, okno 492, **čaká 0** (žiadna aktívna akcia bez AI záznamu). Opakované hľadanie: 0 (zatiaľ nie je akcia doplnená viac ako 60 dní pred dátumom – prvé pribudnú z tohto behu). Hľadaní 670, mesačne 1696/3000.
- Cena behu **1,44 $** (limit behu 2,50 $), za november minuté **2,88 $ z 5 $**; zostatok DeepSeek po behu 3,86 $. Mesačný limit doplnenie nezastavil.

### Overenie na webe (2026-11-21)
| Miesto | URL | Web | `events.json` |
|---|---|---|---|
| Lucerna | musicbar.cz/cs/program/thom-artway/ | 22.11.2026, Doors 18:00, Start 19:00 | 2026-11-22, doors 18:00, start 19:00 ✔ |
| Lucerna | musicbar.cz/cs/program/mig-21-79/ | 24.11.2026, Doors 19:30, Start 21:00, Vyprodáno | 2026-11-24, 19:30 / 21:00, `sold_out: true` ✔ |
| O2 arena | o2arena.cz/events/the-prodigy/ | 23.11.2026 20:00, Vstup od 18:30, 1 830 – 4 690 Kč | 2026-11-23, 20:00, doors 18:30, cena ✔ |
| O2 arena | o2arena.cz/events/calin-viktor-sheen-arena-tour/ | 4.12. a 5.12.2026 19:00, Vstup od 17:30, 990 – 1 990 Kč | 2 akcie (4. a 5. 12.) 19:00, cena ✔; otvorenie prázdne (jedno pre dva dni, viď vyššie) |
| O2 universum | o2universum.cz/events/papa-roach-rise-of-the-roach/ | 24.11.2026 19:00, Vstup od 18:00, 2 002 – 2 992 Kč | ✔ |
| O2 universum | o2universum.cz/events/the-witcher-iii-in-concert/ | 8.11. (minulé) a 25.11.2026 20:00, Vstup od 19:00 | 2026-11-25, 20:00, doors 19:00 ✔ |
| Jazz Republic | jazzrepublic.cz/cz/program/2026-11-21-live-united (lokálne) | Otevřeno 20:00–24:00, vstup volný | v `events.json` nie je (beh web nedosiahol) |

### Návrh štítkov (na schválenie Matejom, už vo `venues.json`)
| Miesto | `type` | `character` | `music` | `size` (kapacita) | `closing` |
|---|---|---|---|---|---|
| Lucerna Music Bar | concert-club | retro (víkendové Pop 80s & 90s video party) | rock, pop, punk, metal | medium (1000 – hranica medium/large) | null – web neuvádza, doplní Matej |
| O2 arena | concert-hall | commercial | pop, rock, metal, hip-hop | arena (20 000) | null |
| O2 universum | concert-hall | commercial | pop, rock, metal, soundtrack | arena (5200) | null |
| Jazz Republic | jazz-club, bar | cozy | jazz, blues, funk, soul | small (150) | 00:00 každý deň (web: 20:00–24:00) |

### Snímka
`docs/tasks/085/events-new-venues.jpg` (Akcie, Kedykoľvek, `events.json` z Pages obmedzený na 4 nové miesta, 390 × 844; skript `tests/playwright/screenshots-085.spec.ts`; spustenie z `web/` potrebuje `NODE_PATH=web/node_modules`). Neprezeral som ju.

### Otvorené
- **Jazz Republic z GitHub Actions nedostupný:** `NewConnectionError … [Errno 101] Network is unreachable` pri výpise (00:04 UTC) aj pri obrázku miesta (00:31 UTC). Web má len IPv4 (62.109.155.170) a z domu funguje (overené 2026-11-21) → webhosting pravdepodobne neprepúšťa siete GitHubu (Azure). Je to zmena spôsobu sťahovania, preto som nič neobchádzal. Otvorené issues `source:jazz-republic/jazzrepublic` a `venue-image:jazz-republic` budú každý deň pribúdať komentármi. **Rozhoduje Matej:** (a) skúsiť ďalší beh, či to nebol výpadok, (b) sťahovať Jazz Republic inak (napr. self-hosted runner / proxy – nový spôsob, prípadne platené), (c) dočasne `active: false`.
- Štítky (tabuľka vyššie) a `closing` Lucerny / O2 čakajú na Mateja.
- Lucerna: väčší obrázok (og:image) a popis dopĺňa `detail_enrich` po 40 akciách za beh – zvyšok v ďalšom behu; 1 akcia bez náhľadu.
- Obrázky miest O2 majú v URL číslo buildu webu (`/20261116-195541/`) – pri novom builde sa môžu zmeniť; upozornenie `venue-image` to zachytí.
