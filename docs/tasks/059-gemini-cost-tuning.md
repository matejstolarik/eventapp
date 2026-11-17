# 059: Zlacnenie Gemini bez straty kvality, uloženie prieskumu, Spotify ID, Akropolis ceny

## Zadanie

**Robí sa pred pokračovaním 058** (časti 2 a 5 z 058 až po tejto úlohe a Matejovom súhlase). **Schválené Matejom 2026-11-17.** Kredit Gemini ~2,8 $, bez automatického dobíjania; táto úloha smie minúť najviac ~1 $.

**Čítaj:** report 058 (Časť 1, Otvorené); `docs/ai-rules.md` (bod B5 zmenený 2026-11-17); kód `pipeline/gemini_test.py`, Gemini provider v `pipeline/enrich_ai.py`.

Východisko (058): `gemini-3.6-flash`, 6,5 hľadania a ~5 800 výstupných tokenov na akciu, **$0.026/akcia** (od 1. 1. 2027 dvojnásobok). Kvalita: typ 14/14 overených, 47/50 Matejových. **Cieľ: < $0.005/akcia pri typ ≥ 90 % na 50 akciách a bez nepodložených žánrov.**

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`.

### 1. Úspora
- **Premýšľanie:** krok 1 (prieskum) nízke; krok 2 (rozhodnutie) stredné. Zmeraj aj krok 2 s nízkym.
- **Model kroku 2:** porovnaj `gemini-3.6-flash` (nízke/stredné premýšľanie) a najlacnejší Flash-Lite. Matej nie je presvedčený, že Lite stačí na rozhodovanie – rozhodne meranie, nie predpoklad.
- **Popis:** krok 2 píše len CZ; SK a EN preloží samostatné volanie najlacnejším modelom (Flash-Lite, bez premýšľania).
- **Hľadania:** najviac 3 na akciu v prieskume + 1 Spotify len pri `concert` / `dj` (nie divadlo, film…).
- **Kratší výstup:** krok 1 vráti stručné fakty (nie súvislý text), krok 2 len JSON.

### 2. Test
- Typ: všetkých 50 akcií z `docs/tasks/056/labels-matej.csv` pre každú variantu z časti 1 (presnosť spolu a bez príkladov z promptu).
- Celé doplnenie (typ, žánre, cena, popis): 10 akcií z testu 058 (vrátane PAST, Athena, Allt, Family Therapy, Video Oldies Ruda Tuček) pre 2 najlepšie varianty.
- **Výstup pre Mateja:** `docs/tasks/059/gemini-tuning.xlsx` – hárok Varianty (model/premýšľanie · typ 50 · bez príkladov · nepodložené žánre · výstupné tokeny/akcia · hľadania/akcia · **$/akcia** · $/mesiac pri ~280 a ~1 300 akciách/mes., aj s cenou od 1. 1. 2027); hárok Akcie (10 akcií, rovnaké stĺpce ako 058 pre 058 vs. 2 najlepšie varianty).
- Odporuč variant (najlacnejší, ktorý spĺňa cieľ kvality). **STOP** – Matej rozhodne.

### 3. Uloženie prieskumu
- Pre každú spracovanú akciu ulož výsledok prieskumu (dotazy, zdroje po rozbalení, fakty, `genre_facts`, dôvod typu, model, dátum) do `site/research/<YYYY-MM>.json` (alebo podobne; **nie** do `events.json`). V appke sa nezobrazuje. Veľkosť do reportu.
- Pri zmene pravidiel musí ísť krok 2 znova z uložených faktov bez nového hľadania (prepínač, napr. `reenrich_from_research`).

### 4. Spotify cez kworb.net ID
- Ak vo výsledkoch hľadania je `kworb.net/spotify/artist/<ID>…`, zostav `https://open.spotify.com/artist/<ID>` a **over**: jeden GET (User-Agent pipeline) vráti 200 a v `<title>` / `og:title` je meno interpreta (porovnanie bez diakritiky a veľkosti). Až potom ulož do `artist_links`. Nič iné z kworb nesťahovať.
- V teste: koľko interpretov dostalo overený odkaz, koľko overenie zamietlo (s príkladmi).

### 5. Ceny Akropolis
Akropolis má cenu na stránke akcie len cez JavaScript. Nájdi, odkiaľ ju stránka berie (zdroj v HTML/JS, iné URL toho istého webu), a vyťahuj ju v adaptéri / `detail_enrich` ako ostatné podniky (len web Akropolisu). Ak sa nedá bez prehliadača, napíš to. Ticketmaster neriešiť.

## Overenie
`pytest -q`, `npm test` (`--reporter=dot`), build OK. V reporte: odkaz na Excel, odporúčaný variant s číslami, cena úlohy, Spotify čísla, Akropolis (koľko akcií má cenu pred/po).
