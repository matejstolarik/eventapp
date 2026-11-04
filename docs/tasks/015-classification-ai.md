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
