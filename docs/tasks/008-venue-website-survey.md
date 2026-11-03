# 008: Prieskum webov zvyšných podnikov

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02. Robí sa **pred úlohou 007**. Len prieskum: žiadne adaptéry, žiadna zmena `venues.json` ani pipeline. Spúšťať na normálnej sieti (Wi-Fi vo vlaku blokovala twistbar.co).

Cieľ: pre každý podnik zistiť, ako rýchlo a akým spôsobom ho vieme pridať. Od toho závisí, či LLM vôbec potrebujeme (úloha 007) a na ktorých weboch ho testovať.

### Podniky
Známy web z auditu (2026-10-29), nájdi stránku s programom:
- Twist: https://twistbar.co/music
- Forum Karlín: forumkarlin.cz
- Archa+: archa-plus.cz
- Jazz Republic: jazzrepublic.cz
- Futurum Music Bar: futurum.musicbar.cz
- Fuchs2: fuchs2.cz (v audite odkazuje na RA; RA nikdy nesťahuj, len zisti, či má program aj na vlastnom webe)
- Bike Jesus: bikejesus.com (rovnako ako Fuchs2)

Web neauditovaný, nájdi oficiálny web a stránku s programom; uveď, ako si overil, že ide o ten podnik (adresa, IG), a nič nedomýšľaj:
- Kino Aero, Strecha Radost (over presný názov), Kolektor, Acid Kafe, El Magico

### Pre každý podnik zisti
1. URL stránky s programom (ak existuje). Ak program na webe nie je (len IG/FB/RA), napíš to.
2. Štruktúrované zdroje: RSS/iCal, schema.org Event (JSON-LD), verejné API alebo JSON endpoint, ktorý web sám používa.
3. Ak nič štruktúrované: ako pravidelné je HTML (opakujúci sa blok na akciu, kde je dátum/čas/názov), či sa obsah renderuje cez JS (statické HTML prázdne?), stránkovanie.
4. Aké údaje sú k dispozícii: dátum (s rokom?), čas, názov, interpreti, cena, lístky, sekcia/žáner.
5. `robots.txt` pre URL programu.
6. Či web odpovedá nášmu `fetch.py` (User-Agent, bez prehliadača). Ak nie, prečo (HTTP kód, TLS chyba, ochrana typu Cloudflare).
7. Počet akcií v okne +180 dní (približne).
8. Odhad náročnosti: **rýchle** (štruktúrovaný zdroj), **parser** (pravidelné HTML), **ťažké** (nepravidelné HTML, JS, voľný text) alebo **bez zdroja**.

Ulož 1 vzorku HTML programu na podnik do `tests/fixtures/survey/` (poslúži pre adaptéry aj pre úlohu 007).

### Report navyše
- Tabuľka všetkých 12 podnikov s bodmi 1 až 8.
- Odporúčané poradie pridávania (najrýchlejšie najprv).
- Ktoré weby sú kandidáti na test LLM (kategória **ťažké**). Ak žiadne, napíš to.
- Podniky na potvrdenie Matejom (neauditované weby).

## Report

Dátum: 2026-11-03. Prieskum vykonaný skriptom (`fetch.py` User-Agent, bez prehliadača). Fixtures: `tests/fixtures/survey/` (12/12 podnikov). Acid Kafe = Acid Coffee, URL potvrdená Matejom (2026-11-03).

---

### Tabuľka podnikov

| # | Podnik | Program URL | Štrukt. zdroj | HTML pravidelné | JS | robots.txt | fetch.py | Polia | Akcií ≈ | Náročnosť |
|---|--------|------------|--------------|-----------------|-----|-----------|---------|-------|---------|-----------|
| 1 | Twist | twistbar.co/music | — | nie (JS) | **áno** | OK | len menu text | — | neznámo | **ťažké** |
| 2 | Forum Karlín | forumkarlin.cz/program/ | — | áno (WP, 64 event-divov) | nie | OK | ✓ 200 | dátum, názov, obrázok | ~30+ | **parser** |
| 3 | Archa+ | archa-plus.cz/cz/program/ | — | áno (vlastný CMS, 49 `program-item`) | nie | OK | ✓ 200 | dátum ISO, čas, názov, sekcia, vstupenky | 49 | **parser** |
| 4 | Jazz Republic | jazzrepublic.cz/ (root; /program → 404) | — | áno (PHP CMS, slug `/en/program/YYYY-MM-DD-*`) | nie | OK | ✓ 200 | dátum v slugu, názov | 90 (nov–jan) | **parser** |
| 5 | Futurum Music Bar | futurum.musicbar.cz/program | RSS `/feed/` (len 10 položiek, pubDate ≠ dátum konania) | áno (WP, `event-lines`, dátumy `DD.MM.YYYY`) | nie | OK | ✓ 200 | dátum, názov, sekcia | ~15 viditeľných | **parser** |
| 6 | Fuchs2 | fuchs2.cz/events (/program → 404) | **JSON-LD Event** (Wix SSR) | áno (Wix) | áno (Wix) | OK | ✓ 200 | name, startDate, url | ? (Wix paging) | **rýchle** |
| 7 | Bike Jesus | bikejesus.com/api/events (SvelteKit, /program → 404) | **Strapi REST API** (`/api/events`) | — | áno (SvelteKit) | 404→OK | ✓ 200 na API | Title, Date, Link, Description, Subtitle | 25 (okt 2026–apr 2027) | **rýchle** |
| 8 | Kino Aero | kinoaero.cz/ (root; /program → redirect na root) | **JSON-LD Event** (32 na stránke) | áno | nie | OK | ✓ 200 | name, startDate+čas, url | 32 (1 týždeň; kino) | **rýchle** |
| 9 | Střecha Radost | strecharadost.cz/#program (anchor; /program → 404) | — | sezónna pauza | nie | OK | ✓ 200 | — | 0 (zima; sezóna 1.5–15.10) | **bez zdroja** |
| 10 | Kolektor | kolektorcafe.cz | — | "Pripravujeme nový web" | nie | OK | ✓ 200 | — | 0 | **bez zdroja** |
| 11 | Acid Coffee | acidcoffee.cz (Wix, root; /program → 404) | — | Wix, žiadna stránka s programom | áno (Wix) | OK | ✓ 200 | — | 0 | **bez zdroja** |
| 12 | El Magico | elmagico.cz/program/ | RSS `/feed/` (WP general feed, nie akcie) | áno (WP + Bricks Builder, `hp-datum-akce`, `hp-mesic-akce`) | nie | OK | ✓ 200 | deň, mesiac, rok (oddelené polia), stránkovanie | 4/týždeň + paging | **parser** |

---

### Detaily per podnik

**1. Twist** (`twistbar.co/music`, 200)
- HTML má 43 KB, ale po odfiltrovaní JS/CSS ostane len navigácia: „T W I S T MENU MUSIC RESERVATIONS CONTACT TWIST AT RA.CO".
- Program je plne JS-renderovaný (SolidPixels CMS), žiadny textový obsah bez prehliadača.
- Stránka odkazuje na RA profil Twist (`TWIST AT RA.CO`) — ale RA nesťahujeme.
- Žiadne API endpointy (`/api/events`, `/feed`, `/rss` → 404).
- Fixture: `twist.html` (43 KB, len navigácia).
- **robots.txt**: povolené; **fetch.py**: HTTP 200, ale obsah prázdny.

**2. Forum Karlín** (`forumkarlin.cz/program/`, 200, presmerovanie z `/program`)
- WordPress, 80 KB. 64 divov s triedou `event`, 172 zmienok 2025/26.
- Bloky akcií: obrázok (alt = názov akcie: Shinedown, Rammstein Symphonic Experience), dátum, odkaz.
- Fixture: `forum-karlin.html`.

**3. Archa+** (`archa-plus.cz/cz/program/`, 200, presmerovanie z `/program`)
- Vlastný CMS, 97 KB. 49 blokov `program-item` s triedami `performance-date`, `performance-title`, `tags-tickets`.
- Vzor: „Út 03 11, 21:00 Lenka Vagnerová & Company: Apartment 24 tanec EN friendly 2026-11-03 21:00 Vstupenky".
- ISO dátumy prítomné (`2026-11-03 21:00`). Akcie pokrývajú november a ďalej.
- Fixture: `archa-plus.html`.

**4. Jazz Republic** (`jazzrepublic.cz/`, 200; `/program` → 404 error page)
- Vlastný PHP CMS. Root stránka obsahuje 90 event-liniek tvaru `/en/program/YYYY-MM-DD-event-slug` s mesačnými záložkami (november, december, január).
- Vzor: `/en/program/2026-11-03-acoustic-cabinet`, `/en/program/2026-11-04-symphony-of-ebony`.
- Dátum je priamo v URL slugu — parser môže extrahovať bez followovania detailu.
- Fixture: `jazz-republic.html`.

**5. Futurum Music Bar** (`futurum.musicbar.cz/program`, 200)
- WordPress, 120 KB. RSS na `/feed/` funguje (200, 26 KB) s titulmi akcií (TRANSMISSION THE SOUND OF JOY DIVISION, INGESTED, LYNCH MOB...) ale `pubDate` je dátum zverejnenia, nie konania — RSS nepoužiteľný ako primárny zdroj.
- HTML má triedy `event-lines`, `event-lines_title`, dátumy formátu `04.11.2026`, `05.11.2026` až `19.11.2026` (viditeľné v 120 KB).
- Fixture: `futurum.html`.

**6. Fuchs2** (`fuchs2.cz/events`, 200; `/program` → 404)
- Wix stránka (860 KB full HTML, server-side rendering zachováva JSON-LD).
- Nájdené: JSON-LD Event, napr. `"name": "LATIN CORE THURSDAYS: Addly Muff ☆ Gatita Tribalera ☆ Swine Daily", "startDate": "2026-11-26T23:00:00+01:00"`.
- Fixture 50 KB zobrazila len 1 akciu; plný HTML má viac (Wix stránkovanie).
- RA profil: `ra.co/clubs/162121` (odkaz, nesťahujeme).
- Fixture: `fuchs2.html`.

**7. Bike Jesus** (`bikejesus.com`, root SvelteKit; `/api/events` → 200)
- SvelteKit app, root HTML má len JS chunky (žiadny obsah bez JS).
- REST API: `https://bikejesus.com/api/events` → Strapi JSON, 25 akcií.
- Vzor: `{"id":498, "Title":"Gurriers (IE) + Support: Enola Gay", "Date":"2026-11-21", "Link":"https://fb.me/...", "Description":null, "Subtitle":null}`.
- Rozsah dátumov: 2026-10-29 až 2027-04-11.
- robots.txt: 404 (nenájdené = povolené).
- Fixture: `bike-jesus.html` (uložený API JSON, 12 KB).

**8. Kino Aero** (`kinoaero.cz/`, 200; `/program` → presmerovanie na root)
- Root stránka 411 KB, server-side rendering.
- 32 JSON-LD Event skriptov: napr. `"name":"Osamělý vlk", "startDate":"2026-11-03T15:00:00+01:00"`.
- Rozsah: 2026-11-03 až 2026-11-10 (1 týždeň; ~4-5 premietaní/deň).
- Adresa: Žižkov; IG: `kino.aero`.
- ⚠ Kino Aero je artové kino, nie hudobný klub. Akcie = filmové premietania + špeciálne udalosti.
- Fixture: `kino-aero.html` (81 KB).

**9. Střecha Radost** (`strecharadost.cz`, 200; `strechaklubradost.cz` → DNS fail)
- Single-page site s navigáciou Menu → `#program`.
- Program sekcia: „Program na sezónu 2027 připravujeme." Sezóna 1.5–15.10, zimná prestávka od 15.10.
- Adresa: nám. Winstona Churchilla 2, Praha 3 – Žižkov. IG: `strecha_radosti`.
- Keď bude otvorená, program bude v `#program` anchor (HTML text) — treba overiť štruktúru v sezóne.
- Fixture: `strecha-radost.html`.

**10. Kolektor** (`kolektorcafe.cz`, 200)
- Stránka pod výstavbou: „Připravujeme nový web – Kolektor. Kavárna, bistro a bar na Letné."
- IG: `kolektorcafe`, FB: `kolektorcafe`, email: `info@kolektorcafe.cz`.
- robots.txt: `noindex, follow`.
- Fixture: `kolektor.html`.

**11. Acid Coffee** (`acidcoffee.cz`, 200; potvrdené Matejom 2026-11-03)
- Wix stránka (714 KB), kavárna + kultúrne miesto, adresa: Dukelských hrdinů 500/25a, Praha 7 (Strossmayerovo náměstí).
- IG: `acidcoffeecz`. JSON-LD: `LocalBusiness` + `WebSite`, žiadne `Event`.
- Stránka s programom neexistuje (`/program`, `/events`, `/akce`, `/calendar` → 404).
- Text stránky: otváracie hodiny, newsletter, e-shop — žiadny zoznam akcií.
- Fixture: `acid-coffee.html`.

**12. El Magico** (`elmagico.cz/program/`, 200)
- WordPress + Bricks Builder, 146 KB.
- Štruktúrované date polia: `hp-datum-akce` (deň: 03, 04, 05...), `hp-mesic-akce` (Listopad, 2026), `hp-den-akce`.
- Dátumy viditeľné v 146 KB: 3.11., 4.11., 6.11., 7.11.2026. Pagination prítomné (older/next).
- RSS `/feed/` = WordPress general feed, nie akcie (prvá položka: „Novinka v menu! MINIBURGERY od 69,-!").
- `og:title`: „Elmagico Club - Praha 4". IG: `elmagico_club`.
- ⚠ Praha 4 — treba potvrdiť, že ide o správny El Magico.
- Fixture: `el-magico.html`.

---

### Odporúčané poradie pridávania

**Rýchle (strukturovaný zdroj, pridáme prvé):**
1. **Bike Jesus** — Strapi API `/api/events`, čistý JSON, 25 akcií, žiadne HTML parsing
2. **Kino Aero** — JSON-LD na root stránke, 32 akcií/týždeň (po potvrdení, že ho Matej chce zaradiť)
3. **Fuchs2** — JSON-LD na /events (Wix SSR); treba overiť, koľko akcií je dostupných

**Parser (pravidelné HTML):**
4. **Archa+** — 49 akcií, ISO dátumy, najčistejšia HTML štruktúra zo všetkých
5. **Jazz Republic** — 90 liniek, dátum v URL slugu, žiadne followovanie detailu
6. **Forum Karlín** — WordPress, 64 event-divov, štandardná štruktúra
7. **Futurum** — WP s `event-lines` triedou a DD.MM.YYYY dátumami
8. **El Magico** — WP + Bricks Builder, štruktúrované date polia, stránkovanie (po potvrdení, že je to správny podnik)

**Ťažké (odkázané):**
9. **Twist** — JS-rendered, žiadne dáta bez headless browser; odložiť

**Bez zdroja (zatiaľ nepridávať):**
10. **Kolektor** — web pod výstavbou
11. **Střecha Radost** — zimná prestávka do mája 2027
12. **Acid Coffee** — žiadna stránka s programom (acidcoffee.cz, Wix kavárna)

---

### Kandidáti na test LLM (kategória **ťažké**)

- **Twist** — jediný kandidát. Program je JS-rendered; ak sa nájde spôsob fetchu (headless browser alebo API), text bude nepravidelný (len obrázky a popisky). Akropolis (z predchádzajúceho prieskumu) a Twist sú teda testovacie weby pre LLM extrakciu.

Ostatné weby (Forum Karlín, Archa+, Jazz Republic, Futurum, El Magico) sú parsovateľné bez LLM.

---

### Podniky na potvrdenie Matejom

Všetky potvrdené Matejom 2026-11-03. Acid Kafe = Acid Coffee (`acidcoffee.cz`), žiadna stránka s programom.

---

Commit: `16a5ddf`
