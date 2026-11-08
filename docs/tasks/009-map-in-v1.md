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
- **Ovládanie hore:** „Dnes ▾“ s výberom jedného dňa, prepínač Všetko | Moje, filter podľa štítkov (formát vrátane `party`, žáner, typ podniku, charakter, veľkosť). Filtre sa dajú kombinovať.
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
