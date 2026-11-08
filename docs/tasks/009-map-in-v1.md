# 009: Mapa vo v1 (dokumentácia a súradnice podnikov)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02, **aktualizované 2026-11-08 pred odovzdaním** (úloha sa doteraz nerobila; medzitým pribudli podniky a rozhodnutia o mape). Len dokumentácia a `venues.json`, PWA sa ešte nestavia.

Rozhodnutie Mateja 2026-11-02: mapa akcií patrí do v1 (doteraz bola v backlogu „mimo v1“). Use case: som v meste a hľadám, kam ďalej; mapa ukazuje, čo je dnes blízko.

1. `docs/project.md`: presuň mapu z „Mimo v1“ do rozsahu v1. Rozsah mapy v1 (Matej 2026-11-02 a 2026-11-03): podniky s akciami v zvolenom dni ako body na mape, ťuknutie → akcie podniku; filter „moje podniky / všetky“ a **rozšírené filtre podľa preferencií** (formát vrátane `party`, žáner, typ podniku, charakter, veľkosť); poloha používateľa len so súhlasom (bez súhlasu mapa funguje bez nej). Fuchs2 a Bike Jesus majú rovnaké súradnice (Štvanica) – body sa prekrývajú, mapa to musí zvládnuť (napr. zoskupenie). Ak je mapa v `project.md` ešte v časti „Mimo v1“/backlog, presuň ju. Nový riadok v `docs/decisions.md`.
2. `data/venues.json`: Kasárna Karlín a Čitárna Unijazz nemajú `address`, `lat`, `lng` (stav 2026-11-08). Pri ostatných 9 podnikoch over, že súradnice sedia s adresou (niektoré majú len 4 desatinné miesta), a oprav, ak nie. Doplň adresu z webu podniku (uveď URL, kde si ju našiel) a súradnice. Súradnice ber z overiteľného zdroja (napr. OpenStreetMap / Nominatim pre presnú adresu) a zdroj uveď v reporte; nič neodhaduj. Do `docs/data-model.md` dopíš, že `lat`/`lng` sú pre podnik v appke povinné (bez nich nie je na mape).
3. Do pravidiel pridávania podnikov (`docs/status.md` alebo `docs/tasks/README.md`, kde sa hodí): nový podnik musí mať adresu a súradnice.
4. Mapový podklad (len zistiť, nevyberať): pre PWA porovnaj 2–3 bezplatné možnosti (napr. Leaflet + OpenStreetMap dlaždice, MapTiler free tier, Mapbox free tier): podmienky použitia, limity zadarmo, či vyžadujú API kľúč. Over v aktuálnych podmienkach poskytovateľov, uveď odkazy a dátum overenia. Výber je rozhodnutie pre Mateja (náklady, kľúč).

## Report
