# 060: Gemini variant D v dennom behu, poistky, ceny (GoOut, vlny), ručné doplnky, prepočítanie

## Zadanie

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

## Overenie a report
- `pytest -q`, `npm test` (`--reporter=dot`), build OK.
- Z `site/events.json` posledného behu (s príkazom): počty s cenou (overenou / neoverenou), časom, žánrami, popisom, Spotify pred a po; zahodené žánre a ceny poistkami (počty + 5 príkladov); hľadania a cena prepočítania.
- Ručne over 5 akcií (URL + čo tam je), z toho aspoň 2 ceny z GoOut.
