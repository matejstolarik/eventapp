# 088: Prieskum webov 4 podnikov (Café V Lese, Klub 007 Strahov, OX Club, Kampus Hybernská)

## Zadanie

Zadal: hlavný chat (Matej), 2026-11-22. **Len prieskum** (žiadne adaptéry, `venues.json`, pipeline ani appka). Výsledok sa použije v úlohe **089** (dávka 3 adaptérov: Karlovy Lázně, El Magico + tie z týchto štyroch, ktoré pôjdu). Môže bežať súbežne s 087 (nemení appku).

**Metóda a pravidlá presne ako `083-venue-survey-v1-expansion.md`** (prečítaj zadanie a report 083): body 1–14 pre každý podnik, vzorky do `tests/fixtures/survey2/`, ra.co nikdy, GoOut/predpredaj/IG/FB nie sú zdroj, ohľaduplne, nič nedomýšľať, nový typ zdroja len popísať.

### Podniky
- **Café V Lese** (Krymská, Vršovice) – koncerty indie/punk/hardcore.
- **Klub 007 Strahov** (koleje Strahov) – punk, hardcore, alternatíva.
- **OX Club** – over, ktorý podnik v Prahe to je (oficiálny web, adresa); ak je viac kandidátov alebo už nefunguje, napíš to.
- **Kampus Hybernská** – kultúrne centrum (koncerty, diskusie, výstavy, kino?); zisti, ktoré akcie sú verejné kultúrne a či sa dajú oddeliť od akademických/interných; či majú viac priestorov.

## Report
- Tabuľka bodov 1–14 (ako 083) + **hárok/tabuľka v Exceli `docs/tasks/088/venue-survey-4.xlsx`** v rovnakom formáte ako 083 (náročnosť farebne).
- Pre každý podnik jasné **odporúčanie pre 089:** pridať / pridať s výhradou (aká) / nepridávať (prečo).
- Kapacita so zdrojom, obrázok miesta (fotka/logo), IG – Matej doplní, čo chýba.

## Report (výsledok, 2026-11-22)

**Commit:** fixtures + Excel + report v jednom commite (hash v zhrnutí pre hlavný chat).
**Stav:** prieskum 4 podnikov hotový.

Pipeline sa nespúšťal (zadanie: len prieskum). **Čísla sú z prieskumu webov 2026-11-22, nie z `events.json`.** Počty spočítané skriptom z uložených odpovedí, okno 22. 11. 2026 + 180 dní (do 21. 5. 2027). Sťahovanie: `requests`, 1 s medzi požiadavkami, lokálna cache, robots.txt skontrolovaný (všetky 4 povolené). ra.co, GoOut ani Eventlook sa neotvárali. **User-Agent:** generický (`eventapp-venue-survey/1.0`, personal non-commercial project) – UA z `pipeline/fetch.py` som nepoužil, lebo čítanie toho súboru zablokoval privacy plugin session.

Plné znenie bodov 1–14: **`docs/tasks/088/venue-survey-4.xlsx`** (hárok Podniky, rovnaké stĺpce ako 083 + stĺpec „Odporúčanie pre 089“, náročnosť farebne). Fixtures v `tests/fixtures/survey2/`: `cafevlese_home.html`, `cafevlese_events_feed.xml`, `cafevlese_mec_ajax_202612.json`, `cafevlese_detail.html`, `klub007_home.html`, `klub007_detail.html`, `oxclub_program.html`, `kampushybernska_program.html`, `kampushybernska_detail.html`.

### Tabuľka (stručne)

| Podnik | Program | Zdroj | Náročnosť | Akcií/180 d | Čas | Cena | Plagát | Obrázok miesta | Kapacita | IG |
|---|---|---|---|---|---|---|---|---|---|---|
| Café V Lese | cafevlese.cz/#programme | JSON-LD + MEC admin-ajax (existujúca stratégia `mec_ajax`) | rýchle | 45 | 19:30 pri 44/45 (asi predvolený) | nie (JSON-LD „0 USD“ = nezmysel) | 1600×900 šírka | bez og:image; fotky pozadia 636×1091 výška | nezistené | cafevlese |
| Klub 007 Strahov | klub007strahov.cz (titulka) | JSON-LD (EventON), všetko na 1 stránke | rýchle | 33 | áno, začiatok | v popise 12/34 | 600×600 / 2048×1070 | og 1200×630 (FB grafika) | 180 (web /informace/) | nezistené (odkaz na príspevok) |
| OX Club Prague | oxclubprague.com/program | žiadny – šablóna | bez zdroja | – | – | – | – | galéria 2048×1365 | nezistené (tretie strany 1000 / 1200) | oxclubprague |
| Kampus Hybernská | kampushybernska.cz/program | HTML Webflow, 4 strany po 20 | parser | 64 (len ~1 mes. dopredu), z toho 8 koncertov | od–do | áno (text) | 1600×1067 šírka | og 2400×1260 (grafika) | nezistené | kampus.hybernska |

Nikde nie je odkaz na RA. Všetky weby odpovedajú bez prehliadača (Café V Lese a Kampus za Cloudflare, ale 200 s obsahom). Adresy v Exceli.

### Odporúčanie pre 089
- **Café V Lese – PRIDAŤ.** Web používa plugin MEC (rovnako ako Čitárna Unijazz) → `jsonld` / `mec_ajax`. Jediný rozdiel: kalendár na titulke nemá číselné skin ID (`mec1` bez `atts[id]`), takže adaptér musí poslať reťazec `atts` zo stránky namiesto `skin_id` (overené: 6 POST na dec.–máj vrátilo 16+3+6+4+5+2 akcií s JSON-LD). Je to malá úprava existujúcej stratégie, nie nový spôsob sťahovania. RSS `/events/feed/` má `mec:startDate`/`mec:startHour`, ale len 10 najbližších akcií (`?paged=` ignoruje) – ako náhrada nestačí. Výhrady: JSON-LD čas má chybnú zónu `+00:00` (brať miestnu časť, ako pri O2); čas je 19:30 pri 44 zo 45 akcií – pravdepodobne jednotný predvolený čas, detail akcie čas neukazuje → **Matej: brať 19:30 ako začiatok, alebo null?** Cena v JSON-LD „0 USD“ → null.
- **Klub 007 Strahov – PRIDAŤ.** Najjednoduchší: JSON-LD všetkých 34 akcií na titulke (1 požiadavka). Výhrada: dátumy nie sú platné ISO (`2026-12-3T19:00+1:00`) – súčasný `_parse_iso_date` ich zahodí (overené), treba tolerantný parser. `endDate` 22:00 = koniec živej hudby (web: „konec živé hudby je ve 22.00“). Žáner je v HTML podtitule (`evcal_event_subtitle`, napr. „Stoner Psych Rock“) – voliteľne. Detail netreba.
- **OX Club – NEPRIDÁVAŤ.** Podnik je jednoznačný: OX Club Prague, Francouzská 75/4, Praha 2 (oficiálny web oxclubprague.com, zhoda s prague.eu a kudyznudy.cz). Stránka programu je však statická šablóna: všetky karty 29. 09., prázdne odkazy „info“, opakované „Savage in ox club“, záložky září–prosinec. Vstupenky cez Eventlook (predpredaj – nie zdroj). Skutočný program na webe nie je.
- **Kampus Hybernská – PRIDAŤ S VÝHRADOU.** Kultúrne centrum UK v areáli s ~40 priestormi (budovy A–E). Zo 64 nadchádzajúcich akcií je len 8 koncertov („HYB4 Hudba:“), 4 filmy, 4 literárne večery (Čítárna), 4 galéria; zvyšok sú workshopy, kurzy šitia, prednášky, študentské večery, konferencia. Výhrada: brať len kultúru – buď podľa predpony názvu „HYB4 Hudba:“ (+ príp. Film/Čítárna/Galerie), alebo podľa „Druh akce“ z detailu (len nové akcie cez detail cache). **Matej: ktoré kategórie?** Program len ~1 mesiac dopredu. Kľúč stránkovania `?9857990c_page=N` je hash Webflow – pri prestavbe webu sa môže zmeniť (→ 0 akcií, chytí to existujúce varovanie).

### Rozhodnuté samostatne
- OX Club = OX Club Prague na Francouzskej (jediný kandidát).
- Kampus Hybernská ako jeden podnik (miestnosti len ako sála).
- Café V Lese hodnotené „rýchle“, lebo stratégia `mec_ajax` už existuje (rozhodnutie 2026-10-31).

### Čo ostáva otvorené / chyby
- Kapacita nezistená: Café V Lese, OX Club (na webe nie je), Kampus Hybernská.
- IG Klubu 007 nezistený (ikona vedie na príspevok `instagram.com/p/B9cipaKHwzK/`).
- Obrázky miest som neotváral (CLAUDE.md); „fotka/logo“ je odhad z názvu a rozmerov.
- Pri Kampuse som omylom stiahol ~30 strán zoznamu mesiacov (nie akcií) – spolu ~40 požiadaviek na kampushybernska.cz; pri Café V Lese ~10 zbytočných požiadaviek na `?paged=`. Inak do ~15 požiadaviek na podnik.
- Rozhodnutia Mateja: čas 19:30 pri Café V Lese, kategórie Kampusu.

### Doplnenie po spätnej väzbe Mateja (2026-11-22)
- **OX Club – oprava: PRIDAŤ (parser).** Prvý prieskum bol chybný: statické karty v HTML `/program` sú len šablóna, ale skutočný program je v tom istom HTML ako base64 XML v inline skripte `dios_xml_akce`, z ktorého karty vykresľuje JS. Dekódované: **9 akcií** (22. 11. 2026 – 17. 4. 2027), polia `index`, `nazev`, `popis` (HTML), `datumakce` (`D.M.YYYY`), `mpic`/`mpic2`/`mpic3`, `nazevurl`, `djs`, `rezervace`, `neprodavat`. Overené proti webu: Diana Arbenina 22. 11., Private event 27. 11., Separ oficiální afterparty 28. 11., Earth – narozeniny 10. 12., NYE 31. 12., Maniak live 12. 2., Shrek rave 2. 4., Alena Omargalieva 10. 4., Sound of Ibiza 17. 4. Detail = `/shop/b<index>-<nazevurl>.htm` (napr. `/shop/b1088-SEPAR-OFICIALNI-AFTERPARTY.htm`). Obsahuje len ten istý popis, VIP ponuku a Eventlook, takže netreba. Čas je len v texte popisu pri 2/9 („Doors: 19:00 / Start: 20:00“), cena pri 1/9. „PRIVATE EVENT“ (`neprodavat`=1) vynechať. Plagát `mpic` 531×531 (štvorec), `mpic2` 437×776. Stačí 1 GET denne; vzorka `tests/fixtures/survey2/oxclub_program.html` + dekódovaná `oxclub_akce_decoded.xml`.
- **Kampus Hybernská:** Matej chce **všetky** akcie (64 v čase prieskumu), bez filtra kategórií.
- **Café V Lese:** čas 19:30 brať ako začiatok (Matej).
- Zapísané v `docs/decisions.md` (2026-11-22) a v Exceli (riadky OX Club, Kampus, Café V Lese).
