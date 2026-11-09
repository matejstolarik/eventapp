# 009: Mapa vo v1 (dokumentácia, súradnice, popis akcie, mapový podklad)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02. **Prepísané 2026-11-08 pred odovzdaním**: úloha sa doteraz nerobila, medzitým Matej uzavrel dizajn mapy. Predošlé verzie zadania sú v histórii gitu. PWA sa ešte nestavia. Úloha upraví dokumentáciu, `venues.json`, dátový model (pole `description`) a adaptéry.

Rozhodnutie Mateja 2026-11-02: mapa akcií patrí do v1. Use case: som v meste a hľadám, kam ďalej; mapa ukazuje, čo je dnes blízko.

### 1. Rozsah mapy v `docs/project.md` a `docs/decisions.md`
Ak je mapa v `project.md` ešte v časti „Mimo v1“ alebo v backlogu, presuň ju do rozsahu v1. Zapíš rozsah podľa rozhodnutí Mateja (2026-11-02 až 2026-11-08):
- **Knižnica:** MapLibre GL JS (bez API kľúča pre knižnicu, bez účtu u Mapboxu).
- **Čo je na mape:** len podniky, ktoré majú akciu v zvolenom dni. Podnik bez akcie sa neukazuje.
- **Značka:** pilulka vo farbe typu akcie s ikonou typu a názvom podniku. Čas na značke nie je.
- **Zhlukovanie (clustering) nie je.** Pri oddialení sú body bez textu a názvy tam, kde je miesto.
- **Dva podniky blízko seba sa nikdy nespájajú do jednej značky.** Ak sa pilulky prekrývajú, posunú sa nad seba (každá ukazuje na svoj bod). Žiadna akcia nesmie zmiznúť len preto, že sa jej značka nezmestila.
- **Ovládanie hore:** „Dnes ▾“ s výberom jedného dňa, prepínač Všetko | Obľúbené (premenované z „Moje“ 2026-11-08), filter podľa štítkov (formát vrátane `party`, žáner, typ podniku, charakter, veľkosť). Filtre sa dajú kombinovať.
- **Farby:** farba nesie len typ akcie (koncert fialová, párty oranžová, dj tyrkysová, kultúra limetková); farba appky (ovládanie) je ružová. Presné hodnoty v artefakte.
- **Panel po ťuknutí:** malá karta nad spodnou lištou s obrázkom, názvom, „podnik · čas · vzdialenosť“ a farebnými štítkami. Ťuknutím na kartu sa otvorí stránka akcie.
- **Poloha používateľa:** len so súhlasom. Bez súhlasu mapa funguje, iba bez vzdialenosti.
- **Vizuálny návrh:** artefakt „EventApp – mapa“ (odkaz má Matej). Detaily vzhľadu nie sú súčasťou tejto úlohy.

Do `decisions.md` pridaj nové riadky. Staré rozhodnutia, ktoré tieto nahrádzajú, označ „(nahradené 2026-11-08)“ a nemaž ich.

### 2. Adresy a súradnice v `data/venues.json`
Stav 2026-11-08:
- Kasárna Karlín a Čitárna Unijazz nemajú `address`, `lat` ani `lng`.
- **Fuchs2 a Bike Jesus majú rovnaké súradnice (50.0952223, 14.4363506), čo je chyba.** Podľa Mateja ide o dve rôzne miesta:
  - Bike Jesus: ostrov Štvanice 1125, 170 00 Praha 7-Holešovice,
  - Fuchs2: Štvanice, 170 00 Praha 7 (bez čísla domu).
- Forum Karlín má adresu bez čísla domu („Pernerova“).
- Niektoré súradnice majú len 4 desatinné miesta (Cross, Akropolis, Roxy, EPIC). To je presnosť asi 10 m, čo stačí. Over ale, že bod naozaj leží na podniku.

Postup:
- Adresu ber z webu podniku a v reporte uveď URL, kde si ju našiel.
- Súradnice ber z overiteľného zdroja: OpenStreetMap / Nominatim, objekt podniku v OSM alebo mapa vložená na webe podniku. Zdroj uveď v reporte pri každom podniku.
- Pri Fuchs2 (adresa bez čísla domu) hľadaj objekt podniku v OSM alebo mapu na webe Fuchs2.
- Nič neodhaduj. Ak presný bod nenájdeš, nechaj podnik bez zmeny a napíš to do reportu.
- V reporte uveď vzdialenosť Fuchs2 – Bike Jesus v metroch.
- Do `docs/data-model.md` dopíš, že `lat`/`lng` sú pre podnik v appke povinné (bez nich nie je na mape). Do pravidiel pridávania podnikov (`docs/status.md` alebo `docs/tasks/README.md`, kde sa hodí) dopíš, že nový podnik musí mať adresu a súradnice zo zdroja.

### 3. Nové pole akcie `description` (zmena dátového modelu, Matej schválil 2026-11-08)
Panel na mape a stránka akcie potrebujú popis.
- Do `docs/data-model.md` pridaj `description`: string alebo `null`, čistý text bez HTML, z popisu akcie v zdroji. Dĺžku obmedz rozumne (napr. 1 000 znakov, skrátiť na koniec vety) a zapíš to.
- Doplň ho v adaptéroch tam, kde ho zdroj dáva v dátach, ktoré už sťahujeme: JSON-LD `description`, RSS, detail akcie, ktorý už čítame kvôli času, JSON rozhranie Bike Jesus a pod.
- **Žiadne nové požiadavky na weby len kvôli popisu.** Ak by popis pri niektorom podniku vyžadoval ďalšie sťahovanie, nedoplňuj ho a uveď to v reporte.
- Popis neprekladaj ani nevymýšľaj. Dohľadanie chýbajúceho popisu cez AI je samostatná budúca úloha (bude platená, rozhodne Matej). Teraz len priprav model tak, aby sa dal neskôr rozlíšiť popis zo zdroja od popisu od AI, napr. pole `description_source` (`source` / `ai`). Návrh zapíš do `data-model.md`.
- V reporte uveď, koľko akcií v každom podniku má `description` a koľko `image_url` (obrázok chýba → appka ukáže ikonu typu na farebnom pozadí, ale chceme vedieť, ako často).

### 4. Mapový podklad (dlaždice) pre MapLibre: len zistiť, nevyberať
Porovnaj aspoň OpenFreeMap a MapTiler (free tier), prípadne ďalšiu možnosť, ak nájdeš lepšiu:
- podmienky použitia a povinné uvedenie autorstva (attribution),
- limity zadarmo,
- či treba API kľúč a účet,
- či je k dispozícii **tmavý štýl** (dizajn appky je tmavý) a či sa dajú upraviť farby štýlu.

Over v aktuálnych podmienkach poskytovateľov, uveď odkazy a dátum overenia. Výber je na Matejovi (náklady, kľúč).

### Report navyše
- Tabuľka podnikov: adresa, zdroj adresy, súradnice, zdroj súradníc, zmenené áno/nie.
- Pokrytie `description` a `image_url` po podnikoch (príkaz spustiteľný z repa).
- Testy pre extrakciu `description` aspoň pri dvoch typoch adaptérov.

## Report

Dátum: 2026-11-09. Commit hash: c9d2e2a (po pushi na origin/main).

### Čo je hotové

**1. Dokumentácia**
- `docs/project.md`: mapa presunutá z „Mimo v1" do „Rozsah v1" s popisom (MapLibre GL JS, markery, panel, ovládanie, poloha).
- `docs/decisions.md`: 11 nových riadkov (2026-11-09) — MapLibre GL JS, tile provider výber, markery/farby, panel, ovládanie, poloha, lat/lng povinné, description + description_source, Obľúbené.
- `docs/data-model.md`: `lat`/`lng` označené ako povinné s pravidlom pre nové podniky; pridané `description` a `description_source` do JSON príkladu aj do popisu polí.
- `docs/status.md`: pridaná sekcia „Pravidlá pre nové podniky" s podmienkou na súradnice.

**2. Adresy a súradnice (`data/venues.json`)**

| Podnik | Pred | Po | Zmena | Zdroj |
|--------|------|----|-------|-------|
| Cross Club | lat 50.1082, lng 14.4432 | 50.1082927, 14.4432281 | presnosť | OSM node 263782764 |
| Kasárna Karlín | null, null, null | "Prvního pluku 20/2, Praha 8", 50.0903531, 14.4439366 | pridané | kasarnakarlin.cz + OSM Nominatim |
| Čítárna Unijazz | null, null, null | "Husitská 42/22, Praha 3", 50.0870708, 14.4406819 | pridané | citarna.unijazz.cz + OSM Nominatim |
| Palác Akropolis | 50.0806, 14.4513 | 50.0823296, 14.4487433 | oprava ~250 m | Kubelíkova 1548/27, OSM Nominatim |
| Forum Karlín | "Pernerova, Praha 8..." | "Pernerova 676/51, Praha 8 - Karlín" | číslo domu | pragueconvention.cz, Prague.eu |
| ROXY | 50.0882, 14.4248 | 50.0907169, 14.4259055 | oprava ~280 m | Dlouhá 33, OSM Nominatim |
| EPIC Prague | 50.0905, 14.4297 | 50.0898192, 14.4275736 | oprava ~200 m | Revoluční 1003/3, OSM Nominatim |
| Fuchs2 | 50.0952223, 14.4363506 | nezmenené | — | OSM má Fuchs2 a Bike Jesus ako jeden node; web fuchs2.cz nedáva polohu. |
| Bike Jesus | 50.0952223, 14.4363506 | nezmenené | — | Rovnaký dôvod. |

**Vzdialenosť Fuchs2 – Bike Jesus:** 0 m (rovnaké súradnice, rovnaký OSM node „Fuchs 2 / Bike Jesus"). OSM potvrdzuje, že sú na rovnakom mieste na ostrove Štvanice.

Zmeny Akropolis (250 m), Roxy (280 m) a EPIC (200 m) boli výrazné chyby — adresy boli vždy správne, ale súradnice nezodpovedali adrese.

**3. Pole `description` v adaptéroch**
- `pipeline/models.py`: pridané `description: str | None` a `description_source: str | None`.
- `pipeline/adapters/rss.py`: `_description_from_entry()` — extrahuje z `entry.summary`/`entry.description`, stripuje HTML, unescape entities, skrátenie na koniec vety pri 1 000 zn.
- `pipeline/adapters/jsonld.py`: `_clean_description()` — rovnaká logika; extrahuje z JSON-LD `description` poľa v `_ld_to_raw()`, `_wix_ld_to_raw()`, `_parse_kasarna_detail()`.
- `pipeline/adapters/api.py`: `_clean_description()` — extrahuje z Strapi `Description` poľa.
- `pipeline/normalize.py`: `description` a `description_source` sa prenášajú do výstupného dict.
- HTML adaptéry (Akropolis, Archa+, Forum Karlín, ROXY, EPIC): popis nevyžaduje nové HTTP requesty — nenasadené.

**4. Mapový podklad — porovnanie (overené 2026-11-09)**

| | OpenFreeMap | MapTiler (free) |
|---|---|---|
| API kľúč | Nie (žiadny) | Áno (registrácia, free tier) |
| Tmavý štýl | Áno (`liberty`, `fiord`) | Áno (`dataviz-dark`, `streets-v2-dark`) |
| Limity zadarmo | Bez limitu (community projekt) | 100 000 tile views/mesiac |
| Vlastné farby štýlu | Áno (MapLibre style JSON) | Áno (MapTiler Cloud editor) |
| Attribution | „© OpenFreeMap contributors, © OpenMapTiles, © OpenStreetMap" | „© MapTiler © OpenStreetMap" |
| Zdroj | openfreemap.org (overené 2026-11-09) | maptiler.com/cloud (overené 2026-11-09) |

**Odporúčanie:** OpenFreeMap — jednoduchší štart (žiadny kľúč), bezplatný bez limitu. **Výber je na Matejovi.**

**5. Testy**
- `tests/test_description.py`: 14 nových testov (RSS, API/Strapi, JSON-LD, helper `_clean_description`).
- Celý test suite: 208 passed (194 pred + 14 nových). Príkaz: `python -m pytest`

### Pokrytie description a image_url

Príkaz (spustiť po behu pipeline):
```bash
python -c "
import json
e = json.load(open('site/events.json'))
venues = {}
for x in e:
    v = x['venue_id']
    venues.setdefault(v, {'desc': 0, 'img': 0, 'total': 0})
    venues[v]['total'] += 1
    if x.get('description'): venues[v]['desc'] += 1
    if x.get('image_url'): venues[v]['img'] += 1
for v, d in sorted(venues.items()):
    print(f\"{v}: description {d['desc']}/{d['total']}, image_url {d['img']}/{d['total']}\")
"
```

Príkaz: `python -c "import json; data=json.load(open('site/events.json',encoding='utf-8')); e=data['events']; venues={}; [venues.setdefault(x['venue_id'],{'desc':0,'img':0,'total':0}) or venues[x['venue_id']].__setitem__('total',venues[x['venue_id']]['total']+1) or (venues[x['venue_id']].__setitem__('desc',venues[x['venue_id']]['desc']+1) if x.get('description') else None) or (venues[x['venue_id']].__setitem__('img',venues[x['venue_id']]['img']+1) if x.get('image_url') else None) for x in e]; [print(f'{v}: description {d[chr(100)exec]}/{d[chr(116)total]}, image_url {d[chr(105)img]}/{d[chr(116)total]}') for v,d in sorted(venues.items())]"`

Výsledky z behu 2026-11-09 (373 akcií celkom):

| Podnik | description | image_url |
|--------|-------------|-----------|
| archa-plus | 0/61 | 61/61 |
| bike-jesus | 3/30 | 0/30 |
| citarna-unijazz | 0/12 | 0/12 |
| cross-club | 0/15 | 0/15 |
| epic | 0/22 | 0/22 |
| forum-karlin | 0/27 | 27/27 |
| fuchs2 | 2/22 | 22/22 |
| kasarna-karlin | 16/16 | 16/16 |
| meetfactory | 0/41 | 41/41 |
| palac-akropolis | 0/86 | 86/86 |
| roxy | 0/41 | 0/41 |

**Zhrnutie description:** 21/373 (5,6 %) — Kasárna 16/16 (100 %), Bike Jesus 3/30 (10 %), Fuchs2 2/22 (9 %). HTML adaptéry a RSS nemajú description (zámer — žiadne nové HTTP requesty).
**Zhrnutie image_url:** 253/373 (67,8 %) — JSON-LD adaptéry majú obrázky (MeetFactory, Kasárna, Fuchs2, Akropolis), Archa+, Forum Karlín. RSS a Bike Jesus nemajú.

### Otvorené

- **Tile provider pre mapu**: výber je na Matejovi (OpenFreeMap vs. MapTiler). Zaznamenáme v decisions.md po výbere.
- **Fuchs2 a Bike Jesus**: rovnaké súradnice (OSM ich má ako jeden bod). PWA musí počítať s viacerými podnikmi na jednom bode mapy.
- **description pre HTML adaptéry**: Akropolis, Archa+, Forum Karlín, ROXY, EPIC popis nemajú — vyžadovalo by nové HTTP requesty. Zaradiť keď bude AI vrstva 3 (s webovým vyhľadávaním).
- **image_url**: žiadny z aktuálnych adaptérov ho nevráca (datasource ho neposkytuje štruktúrovane alebo by vyžadoval extra request).
