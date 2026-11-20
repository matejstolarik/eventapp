# 083: Veľký prieskum webov nových podnikov – priorita 1 (rozšírenie v1)

## Zadanie

Zadal: hlavný chat (Matej), 2026-11-20. **Len prieskum:** žiadne adaptéry, žiadna zmena `venues.json`, pipeline ani appky. Pipeline sa nespúšťa. Štýl ako úloha `008-venue-website-survey.md` (prečítaj jej zadanie aj report – rovnaké body a tabuľka), rozšírený o detail akcie, obrázky a údaje o mieste.

Cieľ: pre každý podnik zistiť, **ako ho vieme pridať, čo bude ľahké, čo ťažké a čo chýba**, aby Matej vybral poradie a vedel, čo doplní sám (Matej veľa údajov vie dohľadať a doplniť ručne).

**Pravidlá (`CLAUDE.md`):** Resident Advisor (ra.co) nikdy nesťahuj – len zapíš, či web podniku na RA odkazuje. **GoOut ani predpredajové weby (Ticketmaster, Ticketportal…) nie sú zdroj programu** – ak má podnik program len tam, zapíš to ako zistenie. Instagram/Facebook nie sú zdroj. Ohľaduplne: jedna požiadavka naraz na web, User-Agent z `fetch.py`, cache, pár desiatok požiadaviek na podnik najviac. Nič nedomýšľaj – čo nezistíš, napíš „nezistené“.

### Podniky (priority podľa Mateja)

**Priorita 1 – určite:**
- Jazz Republic – https://www.jazzrepublic.cz/cz/program (Matej: pekný program, detail akcie má všetko aj s obrázkom). Pozn.: v 008 bolo `/program` 404 – over aktuálny stav.
- El Magico – https://elmagico.cz/program/ (**zvláštny, pozri nižšie**)
- Lucerna Music Bar
- ~~Palác Lucerna – Velký sál~~ (**zrušené 16:56, Matej: nezaujíma** – pri Lucerna Music Bar len zisti, či zdieľa web s Velkým sálom a ako sa akcie odlíšia, aby sa Velký sál nepridal omylom)
- SaSaZu
- O2 arena
- O2 universum
- Sportovní hala Fortuna
- Duplex
- Karlovy Lázně (5 klubov na 5 poschodiach – jeden podnik alebo viac? ako web akcie rozlišuje)
- Kongresové centrum Praha (veľa kongresov – dá sa oddeliť kultúra od konferencií?)

**Priority 2–4 sa presúvajú do úlohy 084** (zmena 16:56, Matej: „určite sprav rozdelenie“ – úloha by bola na kredity priveľká). V 083 len priorita 1 vyššie (10 podnikov) + El Magico OCR. Twist, Kino Aero, Rock Café, Jazz Dock, Reduta, Café V Lese, 007 Strahov, Ankali, Mecca, Malostranská beseda, Chapeau Rouge, Vagon, Rudolfinum a Obecní dům **v 083 nerob**.

Oficiálny web nájdi a over (adresa, odkaz z webu na IG alebo zhoda s prague.eu); ak si nie si istý, že ide o ten podnik, napíš to.

### El Magico – špeciálny prípad
Matej: na https://elmagico.cz/program/ je vždy **veľký plagát so všetkými akciami mesiaca** (bez detailov, ale z textu plagátu sa dá spraviť akcia) a **pri dvoch najbližších akciách sú hneď vedľa detaily aj s plagátom**. Zisti:
1. Kde je obrázok mesačného plagátu (URL, rozlíšenie, ako sa mení názov každý mesiac), či je text na ňom strojovo čitateľný.
2. **Skús text z plagátu vytiahnuť** lokálne bezplatným OCR (napr. `tesseract` s češtinou) a porovnaj s tým, čo na plagáte vidíš: koľko akcií, dátumy, názvy, časy sa prečítali správne. Výsledok (text OCR + tvoje porovnanie) ulož do `docs/tasks/083/elmagico/`.
3. Ako sú v HTML dve najbližšie akcie s detailmi (polia, plagát) – a či sú v HTML aj ďalšie akcie (v 008: WordPress + Bricks, `hp-datum-akce`, stránkovanie).
4. Odhad: OCR spoľahlivé / nespoľahlivé; alternatíva bez OCR (len HTML akcie). **Nepoužívaj platený model ani nový API kľúč** – ak by to bez neho nešlo, len to napíš.

### Pre každý podnik zisti (body 1–8 ako v 008, plus 9–14)
1. URL stránky s programom; ak program na webe nie je, kde je (RA/GoOut/predpredaj/FB) – len zapísať.
2. Štruktúrované zdroje: RSS/iCal, schema.org Event (JSON-LD), verejné API alebo JSON endpoint, ktorý web sám používa.
3. Ak nič štruktúrované: pravidelnosť HTML, či sa obsah renderuje cez JS, stránkovanie / „načítať viac“.
4. Údaje vo výpise: dátum (s rokom?), čas začiatku, otvorenie dverí, názov, interpreti, cena, lístky, sála, žáner/kategória, zrušené/vypredané.
5. `robots.txt` pre URL programu.
6. Či web odpovedá `fetch.py` (bez prehliadača); ak nie, prečo (HTTP kód, TLS, Cloudflare…).
7. Počet akcií v okne +180 dní (približne) a koľko je **neverejných / nekultúrnych** (konferencie, súkromné, športové zápasy) – či sa dajú odfiltrovať.
8. Náročnosť: **rýchle** / **parser** / **ťažké** / **bez zdroja**, s jednou vetou prečo.
9. **Detail akcie:** existuje stránka akcie? čo je navyše oproti výpisu (čas, cena, popis, plagát, lístky, žáner); koľko požiadaviek by to stálo denne.
10. **Plagáty akcií:** majú akcie obrázok? v akom rozlíšení a tvare (na výšku / na šírku / štvorec), zdieľaný obrázok webu namiesto plagátu?
11. **Obrázok miesta:** kandidát na `image_url` (og:image alebo fotka na webe – URL, rozmery, či je to fotka alebo logo). Pravidlo: každé miesto musí mať obrázok.
12. **Údaje o mieste z webu:** adresa, kapacita (s URL zdroja), Instagram (len handle z odkazu na webe), či web odkazuje na RA (len zapísať ID z odkazu, ra.co neotvárať), otváracie hodiny, ak sú.
13. **Prekryv s inými podnikmi:** zdieľa web s iným podnikom (Lucerna, Karlovy Lázně, O2 arena/universum)? akcie mimo samotného miesta?
14. **Čo chýba / čo vie doplniť Matej ručne** (kapacita, obrázok, štítky charakteru, typ akcií…).

Ulož 1 vzorku HTML/JSON programu (a 1 detailu akcie, ak existuje) na podnik do `tests/fixtures/survey2/`.

## Report
- Tabuľka všetkých podnikov s bodmi 1–14 (v reporte stručne; plné znenie v Exceli).
- **Excel `docs/tasks/083/venue-survey.xlsx`** (pre Mateja): hárok **Podniky** – riadok na podnik, stĺpce: priorita, podnik, web, URL programu, typ zdroja, náročnosť, dôvod, akcií/180 dní, nekultúrne akcie, dátum/čas/cena/lístky/sála/žáner (áno/nie), detail akcie, plagáty (áno/nie, tvar), obrázok miesta (URL, fotka/logo), adresa, kapacita + zdroj, IG, RA odkaz, prekryv, čo chýba, čo doplní Matej, poznámka. Hárok **El Magico** – výsledok OCR. Prvý riadok zmrazený, stĺpce čitateľnej šírky, náročnosť farebne (rýchle zelená, parser žltá, ťažké oranžová, bez zdroja sivá). Bez vzorcov netreba nič počítať.
- **Odporúčané poradie pridávania** v dávkach po ~4–5 podnikoch (najrýchlejšie a najvyššia priorita najprv), s odhadom, čo ktorá dávka obnáša.
- Kde treba nový typ zdroja alebo spôsob sťahovania (napr. OCR pre El Magico) – **neimplementuj, len popíš a odhadni náklady**; o novom type zdroja rozhoduje Matej (`CLAUDE.md`).
- Riziká: weby s ochranou proti robotom, podniky, kde je program len na GoOut/predpredaji, veľké objemy (Kongresové centrum, O2), duplicity medzi podnikmi.
- Pipeline nespúšťať; čísla v reporte sú z prieskumu, nie z `events.json` (uveď to).

## Report (výsledok, 2026-11-20)

**Commity:** `844a4a0` (fixtures, Excel, plagát El Magico), report v nasledujúcom commite.
**Stav:** prieskum 10 podnikov priority 1 hotový; **OCR El Magico neurobené** (viď nižšie).

Pipeline sa nespúšťal (zadanie). **Čísla sú z prieskumu webov 2026-11-20, nie z `events.json`.** Počty akcií sú spočítané skriptom z uložených stránok (`tests/fixtures/survey2/`), okno 20. 11. 2026 + 180 dní. Sťahovanie: `requests` s User-Agentom z `pipeline/fetch.py`, 1 s medzi požiadavkami, lokálna cache, robots.txt skontrolovaný (všetky povolené), najviac ~15 požiadaviek na podnik. ra.co ani GoOut sa neotvárali.

Plné znenie bodov 1–14: **`docs/tasks/083/venue-survey.xlsx`** (hárky Podniky, El Magico). Fixtures: `tests/fixtures/survey2/` (22 súborov, program + detail pre každý podnik; KCP a Duplex aj CSV/JSON).

### Tabuľka (stručne)

| Podnik | Program | Zdroj | Náročnosť | Akcií/180 d | Čas | Cena | Plagát | Obrázok miesta | Kapacita | IG |
|---|---|---|---|---|---|---|---|---|---|---|
| Jazz Republic | jazzrepublic.cz/cz/program (už 200, v 008 bolo 404) | HTML, dátum v URL | parser | 73 (do 31. 1., web ~2,5 mes. dopredu) | len otvorenie 20:00 (detail) | vždy voľný vstup | 660×480 šírka | fotka 600×400 (malá) | nezistené | jazzrepublic |
| El Magico | elmagico.cz/program/ | HTML len 2 akcie + mesačný plagát | ťažké (celý mesiac) / parser (2 akcie) | 2 v HTML, 21 na plagáte (nov.) | nie | čiastočne v texte | 1366×1920 výška | fotka 1000×667 | nezistené | elmagico_club |
| Lucerna Music Bar | musicbar.cz/cs/program/ | HTML + JSON-LD v detaile | parser | 70 | otvorenie + začiatok | nie | 1920×1080 šírka (CDN GoOut) | og 1920×1080 (CDN GoOut) | nezistené | lucernamusicbar |
| SaSaZu | sasazu-club.com/kalendar | HTML Next.js, JSON v payloade | parser | 23 | nie | nie | 1080×608 šírka | OG grafika 1200×630 | 2000 (web) | sasazuclub |
| O2 arena | o2arena.cz/events/ | HTML + JSON-LD v detaile | parser | 37 | áno (+ otvorenie v detaile) | detail od–do | 1080×1080 / 1322×623 | default FB 1200×630 | až 20 000 (web) | o2arenapraha |
| O2 universum | o2universum.cz/events/ | rovnaká šablóna | parser (spoločný adaptér) | 39 | áno | detail od–do | ako O2 arena | default FB 1200×630 | nezistené | o2universum |
| Sportovní hala Fortuna | sportovnihalafortuna.cz/kalendar-akci | HTML | parser | 6 | áno | detail od–do | banner 1920×600 | **žiadna** | 5 500 sed. + 3 500 stát. (web) | nie je na webe |
| Duplex | duplex.cz/duplex-events/ | **JSON endpoint webu** + JSON-LD | rýchle | ~50 (web ~1 mes. dopredu) | áno, so zónou | áno (EUR) | 2560×1440 šírka | og 2048×1366 | „over 2000“ (web) | duplexprague |
| Karlovy Lázně | karlovylazne.cz/events | HTML (SolidPixels, SSR) | parser | ~8 naraz (týždeň + NYE) | áno | nie | 1920×1080 šírka | og 2048×1363 | nezistené | karlovylazne |
| Kongresové centrum Praha | praguecc.cz/cs/prehled-akci/kultura | HTML + CSV | parser | ~10 (12 do 12/2027) | zriedka, v texte | nie | 800×600 PNG | fotka 4442×3326 (10 MB) | 2 764 Kongresový sál (web) | kongresovecentrumpraha |

Nikde nie je odkaz na RA. Všetky weby odpovedajú bez prehliadača (Duplex a Lucerna sú za Cloudflare, ale vracajú 200 s obsahom). Adresy sú v Exceli.

### Dôležité zistenia
- **Jazz Republic:** výpis `li.indexlist1` – dátum ISO v URL (`/cz/program/2026-11-21-live-united`), názov, obrázok. Detail: otvorenie 20:00–24:00, zostava, popis. Čas začiatku koncertu nie je uvedený (len „druhý set od 22:30“) → `start_time` null, alebo len otvorenie.
- **El Magico:** v HTML vždy len 2 najbližšie akcie (`hp-datum-akce`/`hp-mesic-akce`, Bricks stránkovanie `data-max-pages="1"`). WP REST `/wp-json/wp/v2/program` existuje, ale **dátum akcie neposkytuje** (je len v HTML detailu). Plagát: `/wp-content/uploads/YYYY/MM/program-<mesiac>-YYYY-el-magico.jpg` (1358×1920), názov nie vždy rovnaký (`-FINAL`, `-korekce-01`); dá sa nájsť cez `/wp-json/wp/v2/media?search=program` alebo odkaz na `/program/`. Plagát nemá časy ani ceny; 21 akcií v novembri, ~8 sú turnaje/kvízy/beer pong.
- **Lucerna Music Bar:** čas vo výpise = **otvorenie**, `data-start` = **začiatok** (overené: Thom Artway výpis 18:00, detail „Doors 18:00 Start 19:00“, JSON-LD 19:00); líši sa v 71 zo 74 akcií. Vypredané = `.sold-out`. JSON-LD v detaile je **neplatný JSON** (chýba čiarka v `image`). **Velký sál sa omylom nepridá**: má vlastný web lucerna.cz, musicbar.cz má len akcie Music Baru.
- **SaSaZu:** oficiálny web klubu je **www.sasazu-club.com** (overené: prague.eu naň odkazuje, IG `sasazuclub` zhodný). sasazu.com je reštaurácia, jej odkaz na klub padá na TLS chybe. Čas akcie nie je ani v detaile.
- **O2 arena / O2 universum:** obe stránky `/events/` obsahujú **obe sekcie** (O2 arena 60 + O2 universum 50 kariet) → oddeliť podľa `<h2 class="toLeft">` alebo podľa domény odkazu. Jeden adaptér pre obe. Šport (HC Sparta, OKTAGON, florbal, jazdectvo, nohejbal) sa dá vyradiť podľa „Typ akce“ v detaile alebo `/filter/sport/`. JSON-LD má **chybnú zónu `+00:00`** pri pražskom čase (20:00 je 20:00 miestneho) – brať len miestnu časť. Karta môže mať viac termínov (Calin & Viktor Sheen 4.+5. 12.).
- **Duplex:** web sám publikuje JSON `https://www.duplex.cz/wp-json/duplex/v1/agent/events` (v `<link rel="alternate">`, „Events and tickets (JSON)“) – 50 akcií s časom (+01:00), obrázkom, kategóriami a cenami (EUR). 16 z 50 sú **boat party** (loď od Dock 16, Dvořákovo nábř., potom afterparty v Duplexe). Web obsahuje aj návod pre AI asistentov na nákup lístkov – ignorované, nič sa nekupovalo.
- **Karlovy Lázně:** jeden podnik; 5 poschodí je len v popise akcie (DJ na poschodie). Výpis = generické noci aktuálneho týždňa (aj minulé dni) + NYE.
- **KCP:** kultúra je na samostatnej stránke (kongresy na `/prehled-akci/kongres`, teraz prázdne) → oddelenie je jednoduché. CSV `/akce-budouci.csv` = tých istých 12 akcií, len dátum od–do, názov, kapacita sály, bez času a odkazu; UTF-8 s BOM na každom riadku. Monte Cristo = jedna karta s ~30 predstaveniami v texte.

### El Magico – OCR
**Neurobené.** Tesseract nie je nainštalovaný a inštalácia (`winget install tesseract-ocr.tesseract`) bola v tejto session zablokovaná povoľovacím systémom (zásah do systému mimo repa). Namiesto toho: plagát uložený (`docs/tasks/083/elmagico/program-listopad-2026-el-magico.jpg`) a ručný referenčný prepis všetkých 21 akcií (`docs/tasks/083/elmagico/poster-reference-listopad-2026.md`, hárok El Magico v Exceli). Obe HTML akcie (20. a 21. 11.) sa s plagátom zhodujú.
**Odhad bez merania:** čistý bezpätkový font, veľké písmo, jednofarebné pozadie riadkov (biela/žltá na čiernej a červenej) – pre Tesseract skôr priaznivé; riziko je žltý text na červenej, malé písmo dlhých riadkov (11. a 25. 11.) a diakritika. DJ v pravom stĺpci treba oddeliť podľa pozície. Časy na plagáte nie sú vôbec.
**Alternatíva bez OCR:** len 2 HTML akcie (parser, ~2–3 požiadavky denne) – vždy najbližší víkend, nič dopredu.
**Náklady OCR:** nový typ zdroja (obrázok → text) + závislosť (Tesseract v GitHub Actions cez `apt install tesseract-ocr tesseract-ocr-ces`, zadarmo), 1 obrázok mesačne; odhad ~1 deň práce vrátane kontroly. Rozhoduje Matej.

### Odporúčané poradie (dávky)
1. **Dávka 1 – rýchle a hodnotné:** Lucerna Music Bar (parser, 70 akcií, všetko vo výpise), O2 arena + O2 universum (jeden adaptér, ~76 akcií, detail ~76 požiadaviek/deň alebo len nové), Jazz Republic (parser, 73). Pred štartom rozhodnúť šport na O2 a obrázky Lucerny.
2. **Dávka 2:** Duplex (JSON, nová stratégia `api`; rozhodnúť boat party a denné párty), SaSaZu (payload parser, bez časov), Sportovní hala Fortuna (malý parser), KCP (HTML parser; časy len z textu).
3. **Dávka 3 – s otázkou:** Karlovy Lázně (technicky ľahké, ale opakované turistické párty), El Magico (2 akcie z HTML hneď; celý mesiac len s OCR).

### Nový typ zdroja / spôsob sťahovania (neimplementované, rozhoduje Matej)
- **OCR plagátu** (El Magico) – viď vyššie.
- **CSV** (KCP) – netreba, HTML parser dá viac (odkaz na lístky, text s časmi). Odporúčam HTML.
- **JSON endpointy** (Duplex agent JSON, SaSaZu RSC payload) – nové stratégie v existujúcich typoch `api` / `html`, nie nový typ.

### Riziká
- **Obrázky Lucerna Music Bar sú na CDN GoOut** (`static.goout.cloud/musicbarcz/…`) – web podniku stavia GoOut. Rozhodnutie 2026-11-17 „obrázky z GoOut sa neberú“ sa týkalo stránok GoOut; tu ide o vlastný web podniku – **treba rozhodnutie Mateja**.
- Program len krátko dopredu: Duplex ~1 mesiac, Karlovy Lázně 1 týždeň, El Magico 2 akcie (plagát 1 mesiac).
- Bez časov: SaSaZu, KCP (väčšina), El Magico, Jazz Republic (len otvorenie).
- Chybné dáta zdroja: O2 JSON-LD zóna +00:00, Lucerna neplatný JSON-LD → brať HTML / miestny čas.
- Duplicity: O2 arena a universum na jednej stránke; Duplex boat party mimo klubu; Lucerna Music Bar vs. Futurum (sesterské weby, rôzne podniky).
- Objemy sú malé (najviac ~76 akcií spolu na O2); KCP kongresy oddelené; žiadna ochrana proti robotom nebránila.
- Žiadny podnik nemá program len na GoOut/predpredaji.

### Rozhodnuté samostatne
- SaSaZu = klub na www.sasazu-club.com (nie reštaurácia sasazu.com) – overené cez prague.eu a IG.
- El Magico = Chemická 953, Praha 4 – Chodov (ten istý podnik ako v 008; IG `elmagico_club`, adresa na plagáte aj webe).
- Karlovy Lázně ako jeden podnik (návrh; poschodia nie ako samostatné miesta).
- Lucerna Music Bar: čas vo výpise je otvorenie, nie začiatok.

### Čo ostáva otvorené
- OCR El Magico (čaká na povolenie inštalácie Tesseractu).
- Obrázky miest som neotváral (podľa CLAUDE.md); „fotka/logo“ pri og:image je odhad z názvu súboru, overené len rozmery.
- Kapacita nezistená: Jazz Republic, El Magico, Lucerna Music Bar, O2 universum, Karlovy Lázně.
- Rozhodnutia Mateja: šport na O2, boat party / denné párty Duplex, Karlovy Lázně áno/nie, študentské akcie El Magico, obrázky Lucerny z CDN GoOut.
