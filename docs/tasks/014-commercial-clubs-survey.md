# 014: Prieskum komerčných klubov

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-04 (doplnené URL pred odovzdaním). Robí sa po úlohe 013. Len prieskum ako v úlohe 008: žiadne adaptéry, žiadna zmena `venues.json` ani pipeline.

Matej chce pred PWA pridať 2–3 veľké komerčné kluby (ťahák, chodí tam veľa ľudí pravidelne). Kandidáti a stránky s programom (od Mateja 2026-11-04):
- EPIC: https://www.epicprague.com/program
- Duplex: https://www.duplex.cz/duplex-events/
- Roxy: https://www.roxy.cz/club/#program
- Lucerna Music Bar (len Music Bar, nie Velký sál): https://musicbar.cz/cs/program/

### Pre každý podnik zisti (ako v úlohe 008)
1. Či podnik funguje (aktuálny program, nie zatvorený/premenovaný). Oficiálny web over (adresa, IG), nič nedomýšľaj.
2. URL stránky s programom; či program nie je len na Instagrame/Facebooku/RA (RA nikdy nesťahuj).
3. Štruktúrované zdroje: RSS/iCal, schema.org Event (JSON-LD), JSON rozhranie webu.
4. Ak nič: pravidelnosť HTML, JavaScript, stránkovanie.
5. Údaje: dátum, čas, názov, interpreti/DJ, cena, lístky, sekcie.
6. `robots.txt`, odpoveď nášmu `fetch.py`.
7. Počet akcií v okne +180 dní (približne).
8. Náročnosť: rýchle / parser / ťažké / bez zdroja.

### Podklady pre štítky (nové typy podnikov, štítky sa budú riešiť po prieskume)
Pre každý podnik zapíš so zdrojom (URL): ako sa sám popisuje, aká hudba a typy večerov (napr. hity 80. a 90. rokov, R&B, house, techno…), kapacita, či ide o turistický/študentský/klubový podnik. Ak niečo nenájdeš, napíš to.

Ulož 1 vzorku HTML programu na podnik do `tests/fixtures/survey/`.

### Report navyše
- Tabuľka podnikov s bodmi 1–8.
- Odporúčanie, ktoré 2–3 pridať pred PWA (najväčší ťahák a zároveň rýchle), a čo odložiť.
- Podklady pre štítky so zdrojmi.

## Report

Dátum: 2026-11-04. Prieskum vykonaný skriptom (fetch.py User-Agent, bez prehliadača). Fixtures: `tests/fixtures/survey/` (4/4 podnikov).

---

### Tabuľka podnikov

| # | Podnik | Program URL | Štrukt. zdroj | Datetime inline | robots.txt | fetch.py | Polia | Akcií ≈ | Náročnosť |
|---|--------|-------------|---------------|-----------------|------------|---------|-------|---------|-----------|
| 1 | EPIC Prague | epicprague.com/program | — | `<time datetime="YYYY-MM-DD HH:MM">` v listingu | OK (galerie/data zakázané) | ✓ 200, 54 KB | dátum, čas, názov, link | 27 (Nov–Feb) | **rýchle** |
| 2 | Duplex | duplex.cz/duplex-events/ | JSON-LD Event na detail stránkach | nie v listingu; detail: startDate ISO8601 | OK (WP štandard) | ✓ 200, 180 KB | startDate+čas (detail), názov, link | 67+ (stránkovaný) | **parser** |
| 3 | Roxy | roxy.cz/club/ | — | `<time datetime="YYYY-MM-DD HH:MM">` v listingu | OK (prázdny) | ✓ 200, 67 KB | dátum, čas, názov, krajina, link, hashtags | 51 (Nov 2026–Jun 2027) | **rýchle** |
| 4 | Lucerna MB | musicbar.cz/cs/program/ | — | HTML komentár: `<!-- <span class="timestamp">DD.MM.YYYY HH:MM</span> -->` | OK (len /wp-admin/) | ✓ 200, 264 KB | dátum, čas (komentár), názov, link, sold-out | 40/strana + stránky | **parser** |

---

### Detaily per podnik

#### 1. EPIC Prague (`epicprague.com/program`, 200)

- **Funguje**: Áno. Live program, aktuálne akcie.
- **Web overený**: `epicprague.com/contact` → adresa: **Revoluční 1003/3, 110 00 Praha 1 – Staré Město**. Instagram handle nenájdený v HTML stránky (len Facebook pixel).
- **CMS**: vlastný PHP/CMS (nie WordPress); server-rendered HTML (žiadny JS framework).
- **Štruktúra listingu**: 27 unikátnych akcií na jednej stránke.
  - `<time class="program__item-datetime" datetime="2026-11-04 22:00"><a href="/program/2047/...">04/11/2026<br>středa</a></time>`
  - `<h2 class="program__item-heading"><a href="/program/2047/...">FCK EXAMS - study abroad</a></h2>`
  - Každá akcia: dátum + čas inline (`<time datetime>`), názov, odkaz na detail.
- **Stránkovanie**: nie – všetky akcie na jednej stránke.
- **Polia**: dátum + čas (listing), názov (listing), link; detail: čas potvrdený (`<time datetime="2026-11-04 22:00:00">`), obrázok, popis.
- **Čas**: všetky akcie začínajú o 22:00 (klub; zdroj: 27/27 datetime hodnôt).
- **RSS**: nie (`/feed/` → 404).
- **API**: `/wp-json/wp/v2/events` → 403 (WP REST prítomné ale zablokované).
- **robots.txt**: povolené; `/galerie/foto/`, `/data/temp/`, `/backend/` zakázané.
- **Počet (+180 dní)**: 27 – Nov 2026 (20), Dec 2026 (5), Jan 2027 (1), Feb 2027 (1).
- **Fixture**: `tests/fixtures/survey/epic-prague.html` (54 KB).
- **Náročnosť**: **rýchle** – server-rendered, `<time datetime>` inline, žiadne detailné fetchovanie.

#### 2. Duplex (`duplex.cz/duplex-events/`, 200)

- **Funguje**: Áno. Aktívny program, pravidelné akcie každý týždeň.
- **Web overený**: Z RSS event popisu: `📍Jindřišská 2, 110 00 Prague 1` (= Václavské náměstí 2 / roh Jindřišskej). Instagram: neoverený v tomto prieskume.
- **CMS**: WordPress; custom post type `tc_events`.
- **RSS** `duplex.cz/duplex-events/feed/`: existuje, ale len 3 najnovšie príspevky; `pubDate` = dátum publikácie, nie konania. Dátum je v titulku ("TEKMEK x DUPLEX – 14.11.2026"), čas nie.
- **JSON-LD na detail stránkach**: `{"@type": "Event", "startDate": "2026-11-14T22:00:00+01:00", ...}` – plné ISO dátum + čas.
- **API**: `/wp-json/wp/v2/events` → 404; `/wp-json/tribe/events/v1/events` → 404.
- **Štruktúra listingu**: 67 unikátnych event slugov na 1. stránke; slug obsahuje dátum: `tekmek-x-duplex-14-11-2026`. Stránkovanie: `/duplex-events/page/2/` funguje (180 KB/strana).
- **Polia**: listing → slug pre dátum (bez času); detail JSON-LD → name, startDate (ISO+čas), url. Cena/lístky: nie v JSON-LD.
- **robots.txt**: OK (WP štandard).
- **Počet (+180 dní)**: ≥ 67 (1 strana) + ďalšie strany; odhad 130+.
- **Fixture**: `tests/fixtures/survey/duplex.html` (180 KB).
- **Náročnosť**: **parser** – listing HTML → slug pre dátum + detail JSON-LD pre čas (cca 67+ GET requestov/strana).

#### 3. Roxy (`roxy.cz/club/`, 200)

- **Funguje**: Áno. Aktívny program, mix koncertov a club nights.
- **Web overený**: Adresa Dlouhá 33, Praha 1 (všeobecne známa; v HTML stránky priamo nenájdená počas tohto prieskumu). Instagram: neoverený.
- **CMS**: vlastný PHP CMS (nie WordPress); server-rendered HTML.
- **Štruktúra listingu**:
  - Všetky akcie preloaded na jednej stránke; mesačný filter je klientsky (JS filtrovanie podľa `data-date` atribútu).
  - `<a data-date="112026" href="/events/detail/5011/..." class="item">`
  - `<time class="date" datetime="2026-11-04 19:00">St 04/11</time>`
  - `<h2 class="title">LENNY - ONE NIGHT ONLY</h2>`
  - `<h3 class="subtitle">(CZ)</h3>`
  - `data-hashtags="#concert"` / `"#party"` atď.
- **Stránkovanie**: nie – všetky akcie na jednej stránke, klientsky filter podľa mesiaca. URL `?month=2026-12` vráti rovnaké HTML (66 980 B) – filter je JS.
- **Polia**: dátum + čas inline (`<time datetime>`), názov, krajina/popis (`subtitle`), link, hashtag kategória.
- **RSS**: nie (`/feed/` presmeruje na homepage).
- **API**: nie (žiadne endpointy).
- **robots.txt**: prázdny (bez obmedzení).
- **Počet (+180 dní)**: **51** – Nov 2026 (24), Dec 2026 (4), Jan 2027 (4), Feb 2027 (4), Mar 2027 (10), Apr 2027 (2), May 2027 (2), Jun 2027 (1). Pokrýva do júna 2027. Tlačidlá mesiacov existujú až do Aug 2027, ale akcie ešte nie sú publikované.
- **Fixture**: `tests/fixtures/survey/roxy.html` (67 KB).
- **Náročnosť**: **rýchle** – server-rendered, `<time datetime>` inline, žiadne stránkovanie, všetky mesiace na jednej stránke.

#### 4. Lucerna Music Bar (`musicbar.cz/cs/program/`, 200)

- **Funguje**: Áno. Aktívny program.
- **Web overený**: Instagram `instagram.com/lucernamusicbar` – potvrdené v HTML musicbar.cz/cs/ (zdroj: priamy fetch). Adresa Štěpánská 61, Praha 1 (Lucerna Palace) – všeobecne známa; v HTML tejto stránky priamo nenájdená. Kapacita: nenájdená na webe.
- **Poznámka**: Prieskum len pre Music Bar (nie Velký sál Lucerna), ako zadal Matej.
- **CMS**: WordPress 7.1.4.
- **Štruktúra listingu**: 40 unikátnych event URL na 1. stránke; stránkovanie: `/cs/program/page/2/` existuje.
  - Event link: `<a class="program-item" href="https://musicbar.cz/cs/program/[slug]/">`
  - Dátum + čas v HTML komentáry: `<!-- <span class="timestamp">04.11.2026\xa018:30</span> -->` (non-breaking space medzi dátumom a časom; komentár je konzistentný pre každú akciu).
  - Sold-out: `<span class="sold-out">– VYPRODÁNO</span>`.
  - Lístky cez GoOut widget: `href="...#goOutWidget"`.
- **RSS** `musicbar.cz/cs/feed/`: existuje (1.4 MB!); `pubDate` = dátum publikácie, nie konania. Kategória "Program" v RSS. Pre event dátum nutné parsovaie HTML alebo detail stránky.
- **RSS program-specific** `cs/program/feed/` → 404.
- **API**: žiadne event-specific WP REST endpointy.
- **robots.txt**: OK – pôvodný `allowed=False` v urllib.robotparser bol falošne negatívny; priamym fetchom overené: len `/wp-admin/` zakázané, `/cs/program/` povolené.
- **Detail stránka**: timeout pri fetchi (veľká stránka / pomalý server – 264 KB listing page napovedá veľké stránky).
- **Počet (+180 dní)**: 40 na 1. stránke + ≥ 1 ďalšia stránka; odhad 60–80+.
- **Fixture**: `tests/fixtures/survey/lucerna-music-bar.html` (264 KB).
- **Náročnosť**: **parser** – HTML komentáre pre dátum/čas (`re` alebo BS4 comment extraction), stránkovanie nutné, veľké stránky (timeout riziko).

---

### Podklady pre štítky

#### EPIC Prague
- **Zdroj**: `epicprague.com/contact`, `epicprague.com/program` (2026-11-04)
- **Popis**: "Nejmodernější klub v Praze" (z kontaktnej stránky). Adresa: Revoluční 1003/3, Praha 1 – Staré Město.
- **Hudba a typy večerov** (z programu): club nights každý deň o 22:00; štýly: house (Ministry of House, Music is the Answer, Weekend Warmup), D&B (Let It Roll × Pendulum DJ Set), hardstyle (Sickmode), reggaeton & latino (Sunday Rituals), mainstream (Sunday Rituals Mainstream), techno (Dimitri K × Yoshiko, Anderex × Exproz), student parties (FCK Exams – Study Abroad, Study Abroad Thursday).
- **Kapacita**: nenájdená na webe.
- **Charakter**: veľký komerčný klub, každodenná prevádzka, zameraný na turistov a študentov, medzinárodný program.

#### Duplex
- **Zdroj**: `duplex.cz/duplex-events/feed/` (RSS), `duplex.cz/duplex-events/tekmek-x-duplex-14-11-2026/` detail stránka (2026-11-04)
- **Popis**: "Nightclub Prague" / "Duplex Club Prague" (z RSS titulku). Adresa: Václavské náměstí 2 / Jindřišská 2, Praha 1 (Lucerna komplex, terasa).
- **Hudba a typy večerov**: týždenné formáty (Anthems Wednesday – mainstream, Tasty Thursday, Friday Madness, Saturday Night Fever – pop/disco, Magic Monday, Sunday Funday) + hosťujúci DJs (Vini Vici – psy-trance, TEKMEK – German Techno, Hard Techno); Silvestrovská párty (New Year's Eve).
- **Kapacita**: nenájdená na webe.
- **Charakter**: komerčný klubový podnik, rooftop terasa, Václavské nám. (turistická oblasť), VIP sekcia, pravidelné nočné formáty.

#### Roxy
- **Zdroj**: `roxy.cz/club/` (2026-11-04)
- **Hudba a typy večerov** (z `data-hashtags` a názvov): `#concert` (Lenny CZ, Grey256 CZ, Currents × ERRA), `#party` (techno, D&B – Let It Roll × Mandidextrous), art night (Roxy Visuals Vol.19 – Contemporary Art at Night), Techno Pilates (neformálna zábava).
- **Popis**: Web sa nazýva "ROXY PRAGUE". Adresa Dlouhá 33, Praha 1 (Staré Město) – overená na `roxy.cz`.
- **Kapacita**: nenájdená na webe.
- **Charakter**: alternatívny/kultúrny podnik, mix koncertov a club nights, nie čisto komerčný, art-space prvky.

#### Lucerna Music Bar
- **Zdroj**: `musicbar.cz/cs/` (IG), `musicbar.cz/cs/program/` (program), `musicbar.cz/cs/feed/` (RSS, 2026-11-04)
- **Instagram**: `lucernamusicbar` (overené z HTML musicbar.cz/cs/).
- **Hudba a typy večerov** (z programu a RSS kategórií): Transglobal Underground (world/electronic, UK), Horkýže Slíže (SK – ska/rock, vypredané), Vidiek (SK), Slobodná Európa + Chiki Liki Tu-a (SK), Lyapis Trubetskoy (BY – rock), Búty (CZ), Currents + ERRA (metal, USA), Pokáč (CZ folk), MIG 21 (CZ rock), Pop 80s/90s DJ nights. Kategórie v RSS: Electronic, World, Program.
- **Kapacita**: nenájdená na webe.
- **Charakter**: mid-size koncertná sála, veľmi pestrý program (rock, folk, world, pop, metal, elektronika), veľa SK a CZ kapiel, historická budova Lucerna.

---

### Odporúčanie

| Poradie | Podnik | Dôvod pridania | Dôvod odkladu |
|---------|--------|----------------|---------------|
| 1 | **Roxy** | rýchle (inline `<time datetime>`), 51 akcií (Nov 2026–Jun 2027) na jednej stránke, žiadne stránkovanie, pestré akcie, `data-hashtags` pre formát | — |
| 2 | **EPIC Prague** | rýchle (inline `<time datetime>`), 27 akcií, veľký komerčný klub (ťahák) | — |
| 3 | **Lucerna Music Bar** | prominentný podnik, 40+ akcií/strana, parser ale čas v HTML komentároch, konzistentná štruktúra | stránkovanie + veľké stránky (264 KB), timeout riziko na detail; nie najrýchlejší |
| odložiť | **Duplex** | 67+ akcií, JSON-LD na detail stránkach (spoľahlivé) | stránkovanie + každý event nutí detail GET pre čas → ~130+ requestov; ako prvý krok dátum zo slugu (bez času) |

**Odporúčané poradie pred PWA**: Roxy + EPIC Prague (oba rýchle, každý 1–2 h práce). Lucerna ako tretí (parser ~3–4 h). Duplex odložiť – buď po PWA, alebo ako optimalizáciu (slug → dátum, bez času).
