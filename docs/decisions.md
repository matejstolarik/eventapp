# Rozhodnutia

Platia, kým ich výslovne nezmeníme. Nové rozhodnutie = nový riadok (dátum, rozhodnutie, dôvod). Zmenené rozhodnutie sa neprepisuje, pridá sa nový riadok, ktorý ho nahrádza.

| Dátum | Rozhodnutie | Dôvod |
|---|---|---|
| 2026-10-29 | Najprv spoľahlivé dáta, potom appka | UI nad zlými dátami nemá zmysel |
| 2026-10-29 | Podniky pridáva Matej ručne do `data/venues.json` | Počet podnikov je konečný, ručne = presné |
| 2026-10-29 | Instagram odložený na v2; v1 len RA, RSS, schema.org Event, HTML programy | Žiadny z 12 auditovaných podnikov nemá IG ako jediný zdroj; IG je najdrahšia a najkrehkejšia časť |
| 2026-10-29 | Vo v2 IG len cez oficiálne Graph API (Business Discovery), stories nescrapujeme | Zadarmo, stabilné; scraping je proti ToS a krehký |
| 2026-10-29 | Každý zdroj je samostatný adaptér s jednotným výstupom | Nové zdroje (vrátane IG) bez zásahu do zvyšku systému |
| 2026-10-29 | Štruktúrované zdroje majú prednosť pred HTML; priorita polí `ra` > `jsonld` > `rss` > `html` | Spoľahlivosť |
| 2026-10-29 | Údaje zo zdrojov neberieme naslepo, nesúlad sa označí príznakom, nie potichu opraví | Napr. Kasárna majú vo výpise prehodený deň a mesiac |
| 2026-10-29 | Dátumy a časy ako text v pražskom čase, nikdy cez UTC | Cross RSS dáva polnoc ako 23:00 GMT predošlého dňa |
| 2026-10-29 | Pri neistote akcie nezlučujeme | Duplicita je menšia chyba než zlúčenie dvoch rôznych akcií |
| 2026-10-29 | Pipeline v Pythone, denne cez GitHub Actions | Knižnice na RSS, schema.org aj HTML; Matej Python ovláda; bez servera |
| 2026-10-29 | Úložisko v1: statický JSON na GitHub Pages, žiadna databáza | Jeden používateľ, stovky akcií; nulové náklady; DB až s viacerými používateľmi |
| 2026-10-29 | Frontend v1: PWA v Reacte | Android aj iOS hneď, bez poplatkov Apple a bez Macu |
| 2026-10-29 | Natívna appka (pravdepodobne React Native / Expo) až neskôr, nie zabalená PWA | Apple pravidlo 4.2 zamieta prebalené weby |
| 2026-10-29 | Logika PWA (načítanie, filtrovanie, typy) oddelená od UI | Lacnejší neskorší prechod na natívnu appku |
| 2026-10-29 | Štítky podniku (type, character, music, size, features) ručne, len v angličtine | Filtre sú hlavne vlastnosť podniku; štítky sú bežne anglické |
| 2026-10-29 | Formáty akcie ako zoznam: `live`, `dj`, `theatre`, `opening`, `film`, `quiz`, `other` | Hranica koncert/party je tenká; kvízy sú v Prahe časté |
| 2026-10-29 | Predvolený pohľad `live` + `dj`, ostatné cez filter; výstavy len ako vernisáž | Hlavný účel je hudba, kultúra bez zaplavenia |
| 2026-10-29 | Kategorizácia v troch vrstvách: zdroj, LLM bez internetu, LLM s webom len pri nízkej istote (cache podľa interpreta) | Presnosť bez platenia za vyhľadávanie pri každej akcii |
| 2026-10-29 | Časové okno: akcie od včera do +180 dní | Aktuálnosť je hlavná hodnota, ale aj vzdialenejšie akcie majú byť dostupné |
| 2026-10-29 | Podniky bez zdroja akcií (Magneto, Popocafepetl) ostávajú v dátach | Profil a odkazy v appke, akcie môžu pribudnúť neskôr |
| 2026-10-29 | Podnik má súradnice (`lat`, `lng`) od začiatku | Budúca mapa akcií |
| 2026-10-29 | UI v CZ (primárne), SK, EN | Cieľové publikum v Prahe |
| 2026-10-29 | Náklady na nule alebo jednotkách eur mesačne | Osobný projekt, free tiery |
