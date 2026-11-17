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

## Report – časti 1–5 (STOP: Matej vyberá variant)

**Dátum:** 2026-11-17. **Stav: test hotový, čakám na výber variantu.** Denný beh má stále `ENRICH_PROVIDER: claude`, nič sa neprepočítalo.

**Commity:**
- kód častí 1, 3, 4: `bff1971`. Všetky tri časti menia tú istú triedu `_Gemini2`, preto nie sú v samostatných commitoch;
- testovací skript (časť 2): `23eef46`, `ad40b33`;
- Excel, hodnotenie a report: v commite s týmto reportom.

**Výstup pre Mateja:** [`docs/tasks/059/gemini-tuning.xlsx`](059/gemini-tuning.xlsx)
- hárok **Varianty**: 058 a varianty A–F;
- hárok **Akcie**: 10 akcií, 058 vs. B vs. D;
- hárok **Typ 50**: typ pri každej akcii a variante.

Surové výsledky sú v `docs/tasks/059/tune.json` (beh [44117620480](https://github.com/matejstolarik/eventapp/actions/runs/44117620480)) a `docs/tasks/059/tune_a10.json` (beh [44119562024](https://github.com/matejstolarik/eventapp/actions/runs/44119562024)). Moje hodnotenie je v `docs/tasks/059/verdicts.json`.

**Cena úlohy: $0.97**
- skúška na 3 akciách $0.10 ([44117223620](https://github.com/matejstolarik/eventapp/actions/runs/44117223620));
- D, B, C na 53 akciách $0.76;
- A na 10 akciách $0.11.

Čísla sú sčítané z tokenov podľa cenníka https://aistudio.google.com/docs/pricing (2026-11-17). Hľadania spadajú do 5 000 zadarmo za mesiac.

### Časť 1 – úspora (kód)
- Každý krok má vlastný model a úroveň premýšľania:
  - krok 1, prieskum: `gemini-3.6-flash`, low;
  - krok 2, rozhodnutie: podľa variantu;
  - krok 3, preklad: `gemini-3.1-flash-lite`, minimal (najlacnejší Flash-Lite v API), preloží CZ popis do SK a EN.
- Krok 2 píše len CZ popis a vracia len JSON.
- Prieskum: v prompte najviac 3 hľadania + 1 „<meno> spotify“, len pri hudobníkovi alebo DJ-ovi. Výsledok sú stručné riadky faktov (`P:` / `E:` / `U:`), max. ~150 slov.
- Pravidlo B5 (party vs. dj v komerčnom klube) je v prompte podľa `ai-rules.md` 2026-11-17. Video Oldies je preto teraz príklad v prompte. Bez príkladov ostáva 37 akcií namiesto 38.

### Časť 2 – test
Všetky varianty majú rovnaký prieskum (krok 1 prebehol raz pre každú akciu). 53 akcií = 50 z `labels-matej.csv` + SOYUZ, Animaglajz, Spitfire & PAST.

| variant | typ 50 | bez príkladov | nepodložené žánre | výst. tokeny/akcia | hľadania/akcia | $/akcia | od 1. 1. 2027 | $/mes. 280 / 1 300 | od 2027 |
|---|---|---|---|---|---|---|---|---|---|
| 058 (Flash, predvolené premýšľanie) | 47/50 | 35/38 | 0 | 5 793 | 6,5 | 0.026 | 0.052 | 7.34 / 34.08 | 14.68 / 68.17 |
| A: rozhodnutie Flash medium (len 10 akcií) | 7/7 | 5/5 | 1 z 10 akcií | 2 573 | 2,4 | 0.0127 | 0.0250 | 3.55 / 16.47 | – |
| **B: rozhodnutie Flash low** | **48/50 (96 %)** | **36/37 (97 %)** | **3** | 1 248 | 2,58 | **0.0076** | 0.0148 | 2.13 / 9.88 | 4.14 / 19.24 |
| C: rozhodnutie Flash-Lite low | 46/50 (92 %) | 35/37 | neposudzované (13 na kontrolu) | 2 592 | 2,57 | 0.0062 | 0.0081 | 1.74 / 8.07 | – |
| **D: rozhodnutie Flash-Lite minimal** | **46/50 (92 %)** | **34/37 (92 %)** | **7** | 1 364 | 2,58 | **0.0043** | 0.0062 | 1.22 / 5.65 | 1.74 / 8.06 |
| E/F: prieskum Flash-Lite | vyradené | | | | | | | | |

- **E/F:** Flash-Lite ako prieskumník v skúške pri 2 z 3 akcií vôbec nehľadal, ani po opakovanom pokuse. Preto som ho na 50 akciách nemeral.
- **A:** stredné premýšľanie stojí ~$0.013 na akciu, čo je 2,5× nad cieľom aj bez prieskumu. Kvôli rozpočtu ~1 $ som ho meral len na 10 akciách, nie na 50.
- **Nepodložené žánre:** ručne som skontroloval všetky žánre, ktorých názov nie je vo faktoch z prieskumu, a všetky žánre pri 10 akciách.
  - B (3): .THEMAYREVOLUTION `indie` (fakt hovorí alternative rock), Student Wednesday `electronic` (len štýl klubu), Tygroo `trance`.
  - D (7): Up Tone `techno` (len názov stage), Resident Evil `electronic`, High Speed Fairytales `bassline` („heavy bass“, pravidlo C6), Asta Hiroki `ambient` (bez faktu), Křižovatka `uk-garage` + `dubstep` („DJs in this scene“), Family Therapy `hip-hop` (odvodený z grime).
- **Chyby typu:**
  - B: REVO → `music` (nič nenašiel, pravidlo H), Tinlicker → `dj`.
  - D: navyše REEAL TIME 3 → `other` a Asta Hiroki → `dj`.
  - **Tinlicker:** https://www.roxy.cz/events/detail/5077/tinlicker má nadpis „TINLICKER OVLÁDNOU ROXY SVÝM DJ SETEM“ a v texte, že vystupujú ako živá kapela. Treba skontrolovať, či štítok `concert` stále platí.
- **Implicitná cache** takmer nefunguje: 4 000 z 233 000 vstupných tokenov. Ceny v tabuľke ju zahŕňajú.
- **Hľadania:** priemer 2,58 na akciu, ale 7 akcií z 53 malo 4–6 hľadaní. Limit 3 + 1 je len v prompte, API ho nevie vynútiť. Pri 1 300 akciách za mesiac je to ~3 350 hľadaní, teda v rámci 5 000 zadarmo.

**Odporúčanie: žiadny variant nespĺňa celý cieľ** (pod $0.005 a typ aspoň 90 % a žiadny nepodložený žáner).
- **D** spĺňa cenu ($0.0043) aj typ (92 %), ale má 7 nepodložených žánrov. Od 1. 1. 2027 stojí $0.0062, teda nad cieľom.
- **B** má najlepší typ (96 %) a najmenej nepodložených žánrov (3, pri 10 akciách 0), ale stojí $0.0076, od 2027 $0.0148. Oproti 058 je ~3,4× lacnejší.
- Ak je prvá kvalita: **B**. Ak je prvá cena: D, ale so slabšími žánrami.
- Lacnejšie možnosti, ktoré som netestoval:
  - pri B kratší vstup kroku 2 (~4 400 tokenov, hlavne pravidlá, zoznam žánrov a schéma);
  - Batch API, ktoré má podľa cenníka −50 % (nie je overené, či podporuje Google Search).
- **STOP – Matej rozhodne.**

### Časť 3 – uloženie prieskumu (kód)
- Súbor `site/research/<YYYY-MM>.json` (`pipeline/research_store.py`) obsahuje pri každej akcii:
  - dotazy, zdroje po rozbalení, riadky faktov a kworb kontroly;
  - model a premýšľanie kroku 1 aj 2;
  - typ, dôvod typu, žánre a `genre_facts`;
  - dátum spracovania.
- Nie je v `events.json`, appka ho nečíta.
- Beh načíta súbory posledných 3 mesiacov z Pages a zapíše ich späť.
- **Veľkosť:** ~2,1 KB na akciu (53 záznamov variantu B = 110 712 B). To je ~0,6 MB za mesiac pri 280 akciách a ~2,7 MB pri 1 300.
- Prepínač `ENRICH_FROM_RESEARCH=all` (alebo id akcií) pustí krok 2 a preklad z uložených faktov bez hľadania. Test: `tests/test_gemini2.py::test_from_stored_research_without_search`.
- Do denného workflow som vstup ešte nepridal. Pridá sa pri prechode na Gemini (058 časť 2).

### Časť 4 – Spotify cez kworb ID
- Kód: z `kworb.net/spotify/artist/<ID>` vo výsledkoch hľadania sa zostaví `https://open.spotify.com/artist/<ID>` a urobí sa jeden GET. Odkaz sa uloží len pri odpovedi 200 a zhode `og:title`/`<title>` s menom interpreta akcie. Lokálne overené: `open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb` → 200, „Radiohead“.
- **Test na 53 akciách:**
  - 30 hľadaní „spotify“;
  - priama stránka `open.spotify.com` vo výsledkoch 0×;
  - kworb ID 1×: José González → https://open.spotify.com/artist/6xrCU6zdcSTsG2hLrojpmI, overené, uložené vo všetkých variantoch;
  - zamietnuté 0 (nie je príklad).
- Spotify teda zostáva skoro vždy na vyhľadávaní podľa mena v appke.

### Časť 5 – ceny Akropolis: **nedá sa bez iného webu**
- Stránka akcie neobsahuje cenu v HTML ani v JS. Napr. SOYUZ: https://palacakropolis.cz/work/33298?event_id=41530&genre=1&no=62&page_id=33824.
  - `/work/32724.js` volá len `/pub/vstupne_6`, ktorý vracia stav predaja (`{"no": 1, "rs": 0}` pre 41530).
- Stránka nákupu (`…&page_id=42027`) vkladá iframe `https://goout.net/cs/listky/sojuz-soyuz-by-pl/hnsnb/…`. Cenu teda zobrazuje GoOut, nie Akropolis.
- Získať ju by znamenalo nový zdroj (GoOut). Nerobil som to, čakám na rozhodnutie.
- **Akropolis pred aj po:** 5 z 85 akcií má cenu, všetky „vstup volný“. Zdroj: zverejnený `events.json` (`generated_at` 2026-11-17 14:37). Príkaz (počet akcií, s cenou): `python -c "import json;d=json.load(open('pub.json',encoding='utf-8'));ev=[e for e in d['events'] if e['venue_id']=='palac-akropolis'];print(len(ev),sum(1 for e in ev if e.get('price_text')))"`

### Overenie
- `pytest -q`: 321 passed.
- `npx vitest run --reporter=dot`: 199 passed.
- `npm run build`: OK.
- Čísla v tabuľke: `python -m pipeline.gemini_test tune-xlsx docs/tasks/059/gemini-tuning.xlsx docs/tasks/059/verdicts.json B,D docs/tasks/059/tune.json docs/tasks/059/tune_a10.json` (vypíše riadok za každý variant).

### Rozhodnutia urobené samostatne (v `decisions.md`)
- Nastaviteľné kroky a ich predvolené hodnoty.
- Presná cena behu po krokoch.
- Rezerva limitu 6 hľadaní na akciu.
- Vyradenie Flash-Lite ako prieskumníka.
- Uloženie prieskumu na 3 mesiace.
- kworb odkaz sa uloží aj vtedy, keď ho krok 2 nevybral.
- A len na 10 akciách kvôli rozpočtu.

### Otvorené – na rozhodnutie Matejovi
- Variant B alebo D (alebo skúsiť zmenšiť vstup kroku 2 pri B, prípadne Batch API).
- Štítok Tinlicker (`concert`) vs. nadpis „DJ SETEM“ na stránke Roxy.
- Akropolis cena len cez GoOut (nový zdroj), alebo ostať bez ceny.
- Po výbere: 058 časti 2 (prechod) a 5 (prepočítanie, teraz s nižšou cenou), plus vstup `reenrich_from_research` v dennom workflow.
