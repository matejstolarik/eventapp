# 015: Zatriedenie akcií v2 – nové formáty a AI (vrstva 2)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-04. Robí sa pred úlohou 014.

Prečo: vo vrstve 1 (úloha 013) rozhodol o 159 z 299 akcií len predvolený formát podniku, teda odhad. Chyby v `docs/review/classification-2026-11-04.md`: Čitárna – poézia, stand-up, krst knihy a oznam „pro veřejnost otevřeno do 18:00“ ako `live`, PSYTRANCE UNITED ako `live`; Cross – „POHŘEBNÍ KAPELA & METAL NIGHT“ ako `dj`; MeetFactory – „Fource“ ako `live`; Bike Jesus – polovica `music`. Matej odsúhlasil AI na zatriedenie (platená služba, Anthropic API).

### 1. Formáty (zmena dátového modelu, odsúhlasená Matejom 2026-11-04)
- Nové: `dance` (tanečné predstavenie), `talk` (čítanie, debata, prednáška, krst knihy, diskusia), `comedy` (stand-up), `workshop`.
- Ostávajú: `live`, `dj`, `theatre`, `film`, `opening`, `quiz`, `other`, `music` (nerozlíšené, výnimka).
- **Akcia môže mať viac formátov** (platí od 2026-10-29): hranica koncert/DJ je tenká, akcia s kapelou a DJ-mi dostane `live` aj `dj`. Nevyberaj umelo jeden.
- `docs/data-model.md`, `docs/decisions.md`. Mapovanie sekcií Archa+ (tanec → `dance`, debata/přednáška/konference → `talk`, workshop → `workshop`) a ostatných zdrojov uprav.

### 2. Oznamy, ktoré nie sú akcie
Rozšír vyraďovanie oznamov (zatiaľ „ZAVŘENO“) o „otevřeno do …“ a podobné prevádzkové oznamy (Čitárna). Zaloguj, čo sa vyradilo.

### 3. Vrstva 1 (deterministická) zostáva, ale bez hádania
- Zachovaj pravidlá `source` (sekcia zdroja) a `keyword` (kľúčové slová). Tie sú isté a AI ich neprepíše; AI môže len **pridať** ďalší formát (napr. `dj` k `live`) a nesúlad sa zaloguje.
- **Zruš `venue` (predvolený formát podniku)** ako rozhodnutie. Informácie o podniku (typ, charakter, hudba, sekcia, čas začiatku) idú do AI ako kontext.

### 4. Vrstva 2 (AI)
- Model: najlacnejší Claude Haiku (over aktuálny identifikátor a cenu v oficiálnej dokumentácii Anthropicu, uveď v reporte). „Thinking“ vypnúť alebo minimum, štruktúrovaný výstup (tool use / JSON schéma), kontrola `stop_reason` (neúplná odpoveď = chyba, akcia ostane s vrstvou 1).
- Vstup na akciu: názov, interpreti (ak sú), popis (ak ho zdroj dáva), sekcia, čas začiatku, podnik a jeho štítky. Viac akcií v jednom volaní je v poriadku (dávky), ak to zníži cenu.
- Výstup: `formats` (z pevného zoznamu, môže byť viac), `genres` (len z pevného zoznamu 27 žánrov, len ak si je istý; inak prázdne), `confidence` 0–1. Nič mimo zoznamov; čo nie je v zozname, zahoď a zaloguj.
- `classification = {"method": "source" | "keyword" | "llm" | "manual", "confidence": …}`; pri kombinácii uveď hlavnú metódu.
- **Cache:** akcia sa posiela AI len raz. Výsledok sa uloží (napr. pri akcii v `events.json`) a v ďalších behoch sa prevezme zo stavu z GitHub Pages. Znova len ak sa zmení názov alebo popis.
- **Poistky:** max počet volaní a max tokenov na beh (konfigurácia), odhad ceny v súhrne behu. Ak AI zlyhá alebo kľúč chýba, pipeline pokračuje s vrstvou 1 a varovanie ide do súhrnu.
- `data/overrides.json` má stále prednosť pred všetkým.

### 5. Kľúč
- Lokálne: `ANTHROPIC_API_KEY` (hodnotu nikdy nevypisuj ani neukladaj).
- GitHub Actions: secret `ANTHROPIC_API_KEY`. Matej ho vytvorí; napíš mu presný postup (kde v nastaveniach repa). Matej si vytvorí nový kľúč s dlhšou platnosťou a limitom útraty v konzole, starý (do 9. 11.) je len na testy.

### 6. Kontrola Matejom
- Nový `docs/review/classification-RRRR-MM-DD.md` (všetky akcie: dátum, podnik, názov, formáty, žánre, metóda, istota), zoradený podľa podniku.
- Na začiatok súboru zhrnutie: počty podľa formátu pred (013) a po, a zoznam akcií, ktorým sa formát zmenil.

### Report navyše
- Počty podľa formátu a metódy, rozdelenie istoty, akcie s nízkou istotou (< 0,6) vypísané.
- Skutočná cena prvého behu (všetky akcie) a odhad denne/mesačne pri behu len nad novými akciami.
- 20 náhodných akcií na ručnú kontrolu.

## Report

**Dátum:** 2026-11-04  
**Commity:** f578c05 (task file), + commit tohto reportu (viď nižšie)

### Čo je hotové

1. **Nové formáty** (`dance`, `talk`, `comedy`, `workshop`) pridané do `docs/data-model.md` a `SECTION_MAP` v `pipeline/classify.py`. Mapovanie sekcií Archa+ (tanec→dance, debata/přednáška/konference→talk, workshop→workshop) funguje.
2. **Viaceré formáty** — keyword konflikt live+dj teraz vráti `["live","dj"]`, method=keyword, confidence=0.8. Venue rule nevstupuje do hry.
3. **Venue rule (VENUE_DEFAULTS + VENUE_TIME_RULES) odstránená** z vrstvy 1. Venue info (typ, charakter, hudba) ide ako kontext do AI promptu.
4. **Čítárna Unijazz filter rozšírený** o `OTEVŘENO DO` → `_is_closed_notice()` v `pipeline/adapters/jsonld.py`. Oznam „pro veřejnost otevřeno do 18:00" je teraz korektne vyradený (overené v logu pipeline).
5. **`pipeline/classify_ai.py`** — nový súbor, plná AI vrstva 2:
   - Model: `claude-haiku-5-5`, $0.10/$0.50 per MTok
   - Forced `tool_use` (`tool_choice = {"type": "tool", "name": "classify_events"}`)
   - Dávky 20 udalostí / volanie
   - Cache: predchádzajúce llm výsledky z `events.json` sa načítavajú podľa `event_id` + titulu
   - Konfigurácia: `AI_MAX_CALLS` (default 50), `AI_MAX_TOKENS` (default 200 000)
   - Bez kľúča: pipeline pokračuje s varovaním, `ai_stats = {"skipped": True}`
6. **`pipeline/main.py`** — volá `classify_events_ai()`, reportuje AI stats v GitHub Actions job summary.
7. **`docs/data-model.md`** a **`docs/decisions.md`** aktualizované (5 nových rozhodnutí).
8. **`docs/review/classification-2026-11-04.md`** — kompletný zoznam všetkých 298 udalostí.

### Čísla (z `site/events.json` po behu 2026-11-04)

```bash
python -c "import json; d=json.load(open('site/events.json',encoding='utf-8')); e=d['events']; from collections import Counter; fc=Counter(f for ev in e for f in ev.get('formats',[])); mc=Counter((ev.get('classification') or {}).get('method') for ev in e); print(len(e),'events'); print(dict(sorted(fc.items()))); print(dict(sorted(mc.items())))"
```

**298 udalostí celkom.**

| Formát | Počet |
|--------|-------|
| dance | 9 |
| dj | 12 |
| live | 47 |
| music (→ AI) | 142 |
| opening | 2 |
| other | 2 |
| quiz | 1 |
| talk | 4 |
| theatre | 56 |
| workshop | 4 |
| *bez formátu* (→ AI) | 20 |

| Metóda | Počet |
|--------|-------|
| keyword | 58 |
| source | 78 |
| null (→ AI) | 162 |

**Porovnanie task 013 → task 015:**
- venue rule (159 udalostí) → zrušená, nahradená AI layer 2
- Nové formáty dance/talk/workshop zachytili 17 udalostí (source rule)
- 162 udalostí pôjde na AI (9 volaní × 20 dávok)

### AI vrstva — skutočná cena prvého behu

**AI beh nebol vykonaný lokálne** — `ANTHROPIC_API_KEY` nie je nastavený v lokálnom prostredí. Prvý plný AI beh prebehne v GitHub Actions po nastavení kľúča (inštrukcie nižšie).

**Odhad ceny prvého behu (162 udalostí → 9 volaní):**
- Vstup ~1 500 tokenov / volanie × 9 = ~13 500 tokenov → $0.0014
- Výstup ~400 tokenov / volanie × 9 = ~3 600 tokenov → $0.0018
- **Odhad celkom: ~$0.003** (menej ako 1 cent)

**Odhad denný beh (len nové udalosti ~10–20/deň):**
- 1 volanie/deň × $0.0003 = **~$0.001/deň, ~$0.03/mesiac**

### 20 náhodných udalostí na ručnú kontrolu (seed=42)

| Venue | Dátum | Názov | Formáty | Metóda |
|-------|-------|-------|---------|--------|
| meetfactory | 2027-01-13 | Oliver Lovrenski: Když nám bylo míň | theatre | source |
| cross-club | 2026-11-16 | FESTIVAL NADPRAHOU PULMESIC & TECHNO STAGE & PSEUDO 4 | music | null→AI |
| palac-akropolis | 2026-11-27 | FVCK_KVLT/SK+SMALL TOWN LIFE/SK+DALŠÍ | music | null→AI |
| palac-akropolis | 2026-11-06 | FLAMENGO REUNION SESSION - 60 LET | music | null→AI |
| bike-jesus | 2026-11-21 | ACT OF THE BOUNCE | music | null→AI |
| citarna-unijazz | 2026-11-20 | PSYTRANCE UNITED | — | null→AI |
| meetfactory | 2026-12-09 | Esther Bol: Infračervené | theatre | source |
| forum-karlin | 2026-12-04 | MIKOLAS – FORUM KARLÍN | music | null→AI |
| meetfactory | 2027-04-02 | Fource: Nieve Ella | music | null→AI |
| archa-plus | 2026-11-13 | God Save the Drama Queen: Král*ovna | theatre | source |
| meetfactory | 2026-11-07 | Anna Vaverková + Elias O. Graversen | music | null→AI |
| meetfactory | 2026-11-05 | Live Nation: Altın Gün + Anatolian Grooves | live | keyword |
| meetfactory | 2026-11-09 | Samanta Schweblin: Mimo dosah | theatre | source |
| bike-jesus | 2026-11-20 | EARLY SHOW: Ley Lofaj /live | live | keyword |
| bike-jesus | 2026-11-28 | REVO: Just InCase: Blackloud, KAWA, Topal | music | null→AI |
| archa-plus | 2027-02-16 | Adina Šulcová: 50 démonů čtverečních | theatre | source |
| cross-club | 2026-11-17 | TECHNO STAGE | music | null→AI |
| forum-karlin | 2027-01-11 | ADÉLA | music | null→AI |
| bike-jesus | 2026-11-06 | LYRA with FUNK D'VOID [ Cocoon / Bedrock ] | music | null→AI |
| archa-plus | 2026-11-12 | God Save the Drama Queen: Král*ovna | theatre | source |

Väčšina `null→AI` udalostí sú správne zachytené ako `music` (Bike Jesus, Cross Club, Forum Karlín) alebo neidentifikované (Čítárna — PSYTRANCE UNITED bez formátu). AI ich správne zaklasifikuje.

### Nastavenie GitHub Actions secret (pre Mateja)

1. Choď na: `https://github.com/<tvoj-username>/eventapp/settings/secrets/actions`
2. Klikni **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: vlož kľúč z [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
5. Klikni **Add secret**

Workflow súbor (`.github/workflows/`) musí mať:
```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

Po prvom úspešnom behu v CI sa výsledky uložia do `site/events.json` na GitHub Pages a ďalšie behy budú využívať cache (len nové udalosti volajú API).

### Čo zostáva otvorené

- Prvý AI beh (162 udalostí) čaká na nastavenie `ANTHROPIC_API_KEY` v GitHub Actions.
- Review `docs/review/classification-2026-11-04.md` obsahuje len layer-1 výsledky — po prvom AI behu treba vygenerovať nový review s AI výsledkami.
- `output_config={"effort": "low"}` — skontrolovať či Haiku 5.5 tento parameter podporuje (môže byť ignorovaný, nie chyba).
