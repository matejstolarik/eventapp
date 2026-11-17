# 060: Gemini variant D v dennom behu, poistky, ceny (GoOut, vlny), ručné doplnky, prepočítanie

## Zadanie

> **ZMENA 2026-11-17 večer (Matej, pred spustením) – platí pred všetkým nižšie.**
> Podmienky Gemini API (sekcia „Grounding with Google Search“, `https://ai.google.dev/gemini-api/terms`) zakazujú náš spôsob použitia: výsledky sa smú len zobraziť používateľovi, ktorý poslal prompt, so Search Suggestions; zakázané je ich cachovať, analyzovať, vyťahovať z nich odkazy a používať odkazy na určenie stránok na sťahovanie. **Gemini s Google hľadaním sa v pipeline nepoužíva.** Náhrada sa testuje v úlohe 061 (DeepSeek).
> **Rob len:**
> - **Časť 3** bez odseku „GoOut ako prvý zdroj ceny“ v pôvodnej podobe (AI hľadanie). Namiesto neho: ak stránka akcie alebo nákupu na webe podniku odkazuje na GoOut (odkaz na lístky alebo `src` iframe, napr. Akropolis `page_id=42027`), pipeline otvorí tú jednu stránku GoOut a vezme cenu (bez AI, 1 GET na akciu, cache). Podmienky GoOut over pred zavedením; ak zakazujú, zastav túto časť. Oprava kontroly ceny a cenové vlny platia.
> - **Časť 4** (`data/manual.json`) celá.
> - **Časť 6** len: zahodiť Spotify odkazy od AI, ktoré nie sú v `manual.json`.
> - **Časť 7** len z odkazu GoOut z webu podniku (rovnaké načítanie ako cena v časti 3), nie z výsledkov hľadania.
> - **Časť 8** celá.
> - Navyše: workflow `gemini-test.yml` vypnúť (odstrániť `workflow_dispatch` alebo súbor `git rm`) a v kóde zabezpečiť, že denný beh nikdy nevolá Gemini s nástrojom `google_search` (test). Kód `_Gemini2` a `research_store.py` ostávajú (prompty a uloženie prieskumu použije 061).
> **Nerob:** časti 1, 2, 5 (presúvajú sa do úlohy po 061). Denný beh ostáva na `ENRICH_PROVIDER: claude` (kredit ~0,19 $ – AI v behu prakticky nebeží, beh musí bez nej dobehnúť).
> Report: ako je uvedené, bez čísel prepočítania.

**Nahrádza časti 2 a 5 úlohy 058** (prechod a prepočítanie). **Schválené Matejom 2026-11-17.** Kredit Gemini ~1,8 $, bez automatického dobíjania; prepočítanie (~245 akcií × ~0,0045 $) sa doň zmestí. Pri HTTP 402 zastaviť AI, beh pokračuje.

**Čítaj:** report 059 (tabuľka variantov, Časť 3, Otvorené); `docs/ai-rules.md`; report 058 (Časť 1 – kontrola ceny); kód Gemini providera (`enrich_ai.py`, `_Gemini2`), `pipeline/research_store.py`, `pipeline/price.py`, `pipeline/genres.py`, `data/overrides.json`.

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`.

### 1. Variant D v dennom behu
- Krok 1 prieskum `gemini-3.6-flash` low; krok 2 rozhodnutie `gemini-3.1-flash-lite` minimal; krok 3 preklad Flash-Lite minimal (ako variant D v 059).
- `ENRICH_PROVIDER=gemini` pre AI doplnenie **aj** AI zaradenie (`classify_ai.py`) – denný beh nesmie potrebovať Claude.
- Limit 4 500 hľadaní / mesiac. Vstup `reenrich_from_research` do denného workflow (krok 2 z uloženého prieskumu bez hľadania).
- Matej vyhodnotí D po mesiaci podľa týždenných reportov; prepnutie na B (krok 2 `gemini-3.6-flash` low) musí ísť jednou premennou.

### 2. Poistky proti slabinám D (v kóde, nie len v prompte)
- **Odkazy:** ukladá sa len URL, ktorá bola vo výsledkoch hľadania (už platí) – over aj pre `source_url` ceny, typu, popisu.
- **Žánre:** každý žáner musí mať v `genre_facts` citát z faktov prieskumu a v citáte sa musí objaviť názov žánru alebo jeho schválené synonymum (`genre_aliases.json`, varianty pravopisu). Inak sa žáner zahodí (zapísať do `dropped`). Testy.
- **Cena bez opory:** ak vo faktoch prieskumu ani v texte stránky podniku nie je suma ani výraz pre vstup zdarma/dobrovoľné, cena ostane prázdna (Text-appeal). „Tba“, „TBA“, „bude upřesněno“ a podobné nie sú cena → prázdne.

### 3. Ceny
- **Kontrola ceny (oprava):** stránka sa načítala a suma na nej nie je → zahodiť (ako doteraz). Stránka sa nedá prečítať (prázdna / JS / 403) **a** zdroj je predpredaj (goout.net, smsticket.cz, oazis.app, ticketportal.cz, ticketstream.cz) → cenu ponechať s `enrichment.price_text.verified: false`. Stránka podniku nečitateľná → zahodiť.
- **GoOut opraviť:** Matej 2026-11-17 ručne overil, že GoOut mal správnu cenu pri Bad Karma Boy (350 Kč), Keo (490), Family Therapy (450) – kontrola ich zamietla. Zisti prečo (formát „CZK 350“, JS, iná stránka) a oprav. Testy na uložených vzorkách GoOut.
- **GoOut ako prvý zdroj ceny** pre `palac-akropolis`, `kasarna-karlin`, `fuchs2` (cena tam nie je na webe podniku): v prompte prieskumu pri týchto podnikoch hľadať cenu najprv na GoOut a ako zdroj uviesť stránku GoOut. Pred zavedením over podmienky použitia GoOut (automatické otvorenie jednej stránky na overenie) a výsledok napíš do reportu; ak to podmienky zakazujú, **zastav túto časť** a napíš to.
- **Cenové vlny** (1./2./3. vlna, early bird): `price` = rozpätie min–max všetkých známych vĺn (napr. PSH 600–700 Kč).

### 4. Súbor ručných doplnkov
- `data/manual.json` (zapisuje hlavný chat podľa Mateja): `artist_links` (meno interpreta → `open.spotify.com/artist/…`), `events` (oprava poľa pri `event_id`: typ, žánre, cena, čas, popis) a `series` (opakujúca sa séria: kľúč podniku + vzor názvu → typ, žánre, krátky popis série).
- Pipeline: ručné doplnky majú prednosť pred AI aj zdrojom (okrem `status` zrušené/vypredané zo zdroja). Spotify podľa mena interpreta sa pripojí ku každej akcii s týmto interpretom. **Pri známej sérii AI nehľadá typ a žánre**, len doplní účinkujúcich a popis večera (šetrí hľadania).
- Formát a príklad do `docs/data-model.md`. Testy.

### 5. Prepočítanie a žánre na kontrolu
- Po častiach 1–4: všetky akcie v najbližších 60 dňoch cez D (ignorovať cache). Ak dôjde kredit, zvyšok dobehne postupne.
- `docs/tasks/060/genres-review.md` (pôvodne 058 časť 3): všetky mapovania a kandidáti po prepočítaní.

### 6. Spotify bez AI (Matej 2026-11-17)
- Z prieskumu (krok 1) vyhodiť hľadanie „<meno> spotify“ (`docs/ai-rules.md` G). Odkazy na Spotify len z `data/manual.json`.
- Odkazy na Spotify od AI v existujúcich dátach (054, 058) zahodiť, ak nie sú v `manual.json`.
- Limit hľadaní v prieskume tým klesá na 3 na akciu.

### 7. Obrázok z GoOut ako náhrada (Matej 2026-11-17, napr. Bike Jesus)
- Len ak akcia **nemá obrázok z webu podniku** a pipeline už má stránku akcie na `goout.net` (z `ticket_url` alebo z výsledkov hľadania pri cene). Vziať `og:image` z tej istej stránky, **pri tom istom načítaní ako kontrola ceny** (žiadne ďalšie hľadanie, nanajvýš 1 GET na akciu). GoOut sa nikdy nevyhľadáva len kvôli obrázku.
- Pôvod do `enrichment.image_url.source_url`. Náhľad ako doteraz.
- **Podmienka:** podmienky použitia GoOut (časť 3) musia dovoľovať aj použitie obrázka. Ak nie, alebo nie je jasné, **zastav túto časť** a napíš to do reportu. Výsledok overenia podmienok (URL, citát) do reportu.
- Report: koľko akcií bez obrázka pred a po.

### 8. Tlačidlo Spotify v appke (`docs/design.md` §7, „Spotify len s overeným odkazom“)
- Tlačidlo Spotify len pri `artist_links[0].spotify_url`; inak sa nevykreslí a zvyšné 4 tlačidlá sa rovnomerne rozložia. Vyhľadávanie `open.spotify.com/search` zrušiť.
- Screenshoty (Playwright, `docs/tasks/060/`): `detail-spotify.jpg` (akcia s odkazom), `detail-bez-spotify.jpg` (bez odkazu). Ak žiadna akcia odkaz nemá, na screenshot dočasne testovací `manual.json` záznam len lokálne, necommitovať.

## Overenie a report
- `pytest -q`, `npm test` (`--reporter=dot`), build OK.
- Z `site/events.json` posledného behu (s príkazom): počty s cenou (overenou / neoverenou), časom, žánrami, popisom, Spotify pred a po (časť 6); zahodené žánre a ceny poistkami (počty + 5 príkladov); hľadania a cena prepočítania.
- Ručne over 5 akcií (URL + čo tam je), z toho aspoň 2 ceny z GoOut.

## Report

**2026-11-17** · commity `8b44ed1` (Gemini poistka, workflow), `1e6317e` (časť 3), `82a52bd` (časti 4 + 6), `0663917` (časť 8), report + screenshoty v nasledujúcom commite. Beh pipeline: GitHub Actions run 44140299759 (manuálny, `ENRICH_PROVIDER: claude`), `events.json` `generated_at` 2026-11-17T18:51.

### Hotové
- **Gemini s Google hľadaním vypnuté:** `gemini-test.yml` odstránený (`git rm`). `make_provider()` pri `ENRICH_PROVIDER=gemini` vráti „refused“, AI doplnenie sa preskočí a beh pokračuje. Testy `tests/test_no_gemini_search.py`: provider sa nevytvorí, `requests.post` sa nezavolá, `daily.yml` má `claude`. `_Gemini2`, `gemini_test.py`, `research_store.py` ostávajú pre 061.
- **Časť 3, kontrola ceny:**
  - Príčina zamietnutia správnych cien GoOut (Bad Karma Boy, Keo, Family Therapy):
    - stránka akcie GoOut píše cenu ako „Entry CZK 852“ a parser nepoznal menu pred sumou;
    - stránka lístkov `goout.net/cs/listky/…` cenu v HTML nemá, kreslí ju JavaScript (`priceCents`).
  - Oprava:
    - parser berie `CZK/Kč <suma>`;
    - nečitateľná predpredajná stránka (GoOut, smsticket, oazis, ticketportal, ticketstream; GET chyba / 403 / prázdna / bez jedinej sumy) → cena ostane s `enrichment.price_text.verified: false`;
    - načítaná stránka s inou sumou → zahodiť;
    - nečitateľná stránka podniku → zahodiť.
  - Testy na zmenšenej vzorke stránky lístkov GoOut (`tests/fixtures/goout/listky_js_price.html`) a na 403.
- **Cenové vlny:** parser už dával rozpätie min–max všetkých súm. Doplnené testy (1./2./3. vlna 600–700, early bird, „CZK 350“, TBA → bez ceny).
- **Časť 4:** `data/manual.json` (prázdny, plní hlavný chat), modul `pipeline/manual.py`, formát a príklad v `docs/data-model.md`, testy `tests/test_manual.py`. Ako funguje:
  - séria a záznam akcie sa použijú pred AI zaradením aj po AI doplnení a majú prednosť pred AI aj zdrojom;
  - `status` a `sold_out` sa zadať nedajú;
  - pri známej sérii prompt AI hovorí, že typ a žánre sú pevné a nehľadajú sa;
  - pôvod hodnôt je `by: "manual"`; ručné hodnoty sa necachujú ako AI.
- **Časť 6:** `artist_links` len z `manual.json`. Odkazy od AI sa zahodia a z cache sa už neprenášajú. Ručný odkaz sa pripojí podľa mena v `artists` alebo celej časti názvu.
- **Časť 8:** tlačidlo Spotify len pri `artist_links[0].spotify_url`. Vyhľadávanie `open.spotify.com/search` je zrušené; bez odkazu tlačidlo chýba a ostatné sa rozložia (`flex: 1`). Screenshoty `docs/tasks/060/detail-spotify.jpg`, `detail-bez-spotify.jpg` (skript `tests/playwright/screenshots-060.spec.ts`). Testovací odkaz je len v Playwright route, nič sa necommitlo.

### Zastavené (podmienky GoOut)
- **Časť 3 (cena z GoOut cez odkaz z webu podniku) a časť 7 (obrázok z GoOut) neimplementované.**
- Podmienky užitia GoOut: https://terms.goout.net/article/450-podminky-uziti, čl. II „Autorská a licenční práva“. Obsah (výslovne aj fotografie a texty) „lze bez souhlasu GoOut použít pouze pro soukromé účely“; zverejňovať, kopírovať a šíriť ho bez písomného súhlasu je zakázané.
- Cena aj `og:image` by sa zverejnili v `events.json` na GitHub Pages. `robots.txt` GoOut stránky akcií nezakazuje, podmienky áno.
- Akcie bez obrázka: 61 pred, 61 po (časť 7 nebola zavedená).

### Rozhodnutia urobené samostatne
- Časti 4 a 6 sú v jednom commite (rovnaký modul).
- Nový `description_source = "manual"` a `enrichment.*.by = "manual"` (pôvod ručných hodnôt; v `data-model.md`).
- Predpredajná stránka „bez jedinej sumy“ sa berie ako nečitateľná (JS). Stránka, ktorá ukazuje inú sumu, sa berie ako prečítaná → cena sa zahodí.
- Zápis všetkého je v `docs/decisions.md` (7 riadkov 2026-11-17, task 060).

### Čísla (posledný beh, `events.json` 2026-11-17T18:51, pred = zverejnený 2026-11-17T14:37)
Príkaz: `python count060.py pub_pred.json pub_po.json`. Súbory sú stiahnuté z `https://matejstolarik.github.io/eventapp/events.json`. Skript počíta akcie s `price`, `enrichment.price_text` od AI s/bez `verified: false`, `start_time`, `genres`, `descriptions|description`, `artist_links` a bez `image_url`.

| | pred | po |
|---|---|---|
| akcie | 374 | 374 |
| s `price_text` / `price` | 146 / – (kľúč `price` ešte nebol) | 146 / 146 |
| cena od AI overená / neoverená | 16 / 0 | 16 / 0 |
| s časom | 331 | 331 |
| so žánrami | 208 | 208 |
| s popisom | 345 | 345 |
| so Spotify | 2 | 0 (oba od AI, `manual.json` je prázdny) |
| bez obrázka | 61 | 61 |

- AI v behu: okno 243, všetky z cache, 0 hľadaní, 0 $ (`enrich_ai: window=243 cached=243 enriched=0 … cost=$0.0000`).
- Poistky zahodili 0 cien (AI nebežala). Zahodené žánre sa nepočítajú (časť 2 sa nerobila).
- Prepočítanie sa nerobilo (časť 5 presunutá).

### Overenie proti webu (5 akcií + 2 ceny GoOut)
- Cross Club Křižovatka 18. 11.: https://www.crossclub.cz/cs/program/8718-krizovatka/ – „Vstupné: zdarma / free entry“, začiatok 20:00 → `free`.
- MeetFactory Allt 19. 11.: http://www.meetfactory.cz/cs/program/detail/pragokoncert-allt-avralize-bite-down – „Vstupenky: od 950 Kč“ → `min 950, max null`.
- Čítárna Jakub Eden 19. 11.: https://citarna.unijazz.cz/events/david-pillow-krest-jakub-eden/ – „v předprodeji 250 Kč / 350 Kč na místě“ → 250–350.
- Roxy Colorfactory 18. 11.: https://www.roxy.cz/events/detail/5137/vyprodano-colorfactory – „Základní vstupné 990 Kč“ → 990.
- EPIC Student Wednesday 18. 11.: https://www.epicprague.com/program/2297/student-wednesday – „BASIC: 290,-kč | VIP: 500,-kč“ → 290–500.
- GoOut (existujúce AI ceny z 054):
  - TERROR/BANE (Akropolis 25. 11.): https://goout.net/en/terror+bane+start-today+peace-of-mind/szujjly/ – „Entry CZK 852“ = 852 Kč.
  - Gurriers (Bike Jesus 21. 11.): https://goout.net/en/gurriers+support-enola-gay/szuuoiy/ – „Entry CZK 490“ = 490 Kč.

### Testy
- `pytest -q`: 350 passed.
- `vitest --reporter=dot`: 199 passed.
- `npm run build`: OK.
- CI beh: testy aj build prešli.

### Otvorené
- **GoOut – na rozhodnutie Matejovi:**
  - V dátach je 6 cien od AI so `source_url` na GoOut (napr. Akropolis TERROR 852 Kč), overené GET na GoOut.
  - Podľa podmienok GoOut ide o zverejnenie ich obsahu. Ponechať, zahodiť, alebo požiadať GoOut o súhlas (to by odblokovalo aj časti 3 a 7)?
  - Kontrola ceny AI jedným GET na GoOut v kóde ostáva.
- Ceny Bad Karma Boy, Keo a Family Therapy sa opätovne neprepočítali (AI nebeží, prepočítanie je presunuté).
- Časti 1, 2, 5 sú presunuté za 061.
- Lokálne spustenie bez `ANTHROPIC_API_KEY` stráca žánre z cache AI zaradenia (208 → 152 lokálne). Je to existujúce správanie `classify_ai`, nie zmena 060; v CI je kľúč.
