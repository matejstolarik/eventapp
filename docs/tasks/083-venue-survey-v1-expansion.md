# 083: Veľký prieskum webov nových podnikov (rozšírenie v1)

## Zadanie

Zadal: hlavný chat (Matej), 2026-11-20. **Len prieskum:** žiadne adaptéry, žiadna zmena `venues.json`, pipeline ani appky. Pipeline sa nespúšťa. Štýl ako úloha `008-venue-website-survey.md` (prečítaj jej zadanie aj report – rovnaké body a tabuľka), rozšírený o detail akcie, obrázky a údaje o mieste.

Cieľ: pre každý podnik zistiť, **ako ho vieme pridať, čo bude ľahké, čo ťažké a čo chýba**, aby Matej vybral poradie a vedel, čo doplní sám (Matej veľa údajov vie dohľadať a doplniť ručne).

**Pravidlá (`CLAUDE.md`):** Resident Advisor (ra.co) nikdy nesťahuj – len zapíš, či web podniku na RA odkazuje. **GoOut ani predpredajové weby (Ticketmaster, Ticketportal…) nie sú zdroj programu** – ak má podnik program len tam, zapíš to ako zistenie. Instagram/Facebook nie sú zdroj. Ohľaduplne: jedna požiadavka naraz na web, User-Agent z `fetch.py`, cache, pár desiatok požiadaviek na podnik najviac. Nič nedomýšľaj – čo nezistíš, napíš „nezistené“.

### Podniky (priority podľa Mateja)

**Priorita 1 – určite:**
- Jazz Republic – https://www.jazzrepublic.cz/cz/program (Matej: pekný program, detail akcie má všetko aj s obrázkom). Pozn.: v 008 bolo `/program` 404 – over aktuálny stav.
- El Magico – https://elmagico.cz/program/ (**zvláštny, pozri nižšie**)
- Lucerna Music Bar
- Palác Lucerna – Velký sál (over, či má Music Bar a Velký sál spoločný web/program a ako sa odlíšia)
- SaSaZu
- O2 arena
- O2 universum
- Sportovní hala Fortuna
- Duplex
- Karlovy Lázně (5 klubov na 5 poschodiach – jeden podnik alebo viac? ako web akcie rozlišuje)
- Kongresové centrum Praha (veľa kongresov – dá sa oddeliť kultúra od konferencií?)

**Priorita 2 – chce, ale nie za každú cenu:**
- Twist Bar – https://twistbar.co/music (v 008: program cez JavaScript, statické HTML prázdne). **Zisti, či web nenačítava program z nejakého JSON/API** (sieťové požiadavky stránky, napr. Playwright `page.on('response')` alebo zdroj JS) – ak áno, je to „rýchle“. Inak odhadni, čo by stálo vykresľovanie prehliadačom v GitHub Actions (čas behu, závislosti). Matej: „chcem, ale nie cez mŕtvoly“.
- Kino Aero – kinoaero.cz (v 008 JSON-LD, 32 akcií/týždeň). **Zmeraj:** koľko premietaní denne a za 180 dní, koľko je unikátnych filmov, či sa dajú rozlíšiť špeciálne akcie (premiéry, diskusie, festivaly, koncerty) od bežných premietaní. Matej sa bojí zahltenia (až 4 premietania denne) – rozhodne podľa čísel.

**Priorita 3 – menšia priorita:**
- Rock Café, Jazz Dock, Reduta Jazz Club, Café V Lese, Klub 007 Strahov, Ankali, Mecca, Malostranská beseda, Chapeau Rouge, Vagon

**Priorita 4 – len zistiť:**
- Rudolfinum, Obecní dům – Smetanova síň (klasická hudba; zisti objem a zdroj, Matej rozhodne, či klasika do appky patrí)

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
- **Excel `docs/tasks/083/venue-survey.xlsx`** (pre Mateja): hárok **Podniky** – riadok na podnik, stĺpce: priorita, podnik, web, URL programu, typ zdroja, náročnosť, dôvod, akcií/180 dní, nekultúrne akcie, dátum/čas/cena/lístky/sála/žáner (áno/nie), detail akcie, plagáty (áno/nie, tvar), obrázok miesta (URL, fotka/logo), adresa, kapacita + zdroj, IG, RA odkaz, prekryv, čo chýba, čo doplní Matej, poznámka. Hárok **El Magico** – výsledok OCR. Hárok **Kino Aero** – premietania za deň. Prvý riadok zmrazený, stĺpce čitateľnej šírky, náročnosť farebne (rýchle zelená, parser žltá, ťažké oranžová, bez zdroja sivá). Bez vzorcov netreba nič počítať.
- **Odporúčané poradie pridávania** v dávkach po ~4–5 podnikoch (najrýchlejšie a najvyššia priorita najprv), s odhadom, čo ktorá dávka obnáša.
- Kde treba nový typ zdroja alebo spôsob sťahovania (prehliadač pre Twist, OCR pre El Magico) – **neimplementuj, len popíš a odhadni náklady**; o novom type zdroja rozhoduje Matej (`CLAUDE.md`).
- Riziká: weby s ochranou proti robotom, podniky, kde je program len na GoOut/predpredaji, veľké objemy (Aero, Kongresové centrum), duplicity medzi podnikmi.
- Pipeline nespúšťať; čísla v reporte sú z prieskumu, nie z `events.json` (uveď to).
