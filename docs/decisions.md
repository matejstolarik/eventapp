# Rozhodnutia

Platia, kým ich výslovne nezmeníme. Nové rozhodnutie = nový riadok (dátum, rozhodnutie, dôvod). Zmenené rozhodnutie sa neprepisuje, pridá sa nový riadok, ktorý ho nahrádza.

| Dátum | Rozhodnutie | Dôvod |
|---|---|---|
| 2026-10-29 | Najprv spoľahlivé dáta, potom appka | UI nad zlými dátami nemá zmysel |
| 2026-10-29 | Podniky pridáva Matej ručne do `data/venues.json` | Počet podnikov je konečný, ručne = presné |
| 2026-10-29 | Instagram odložený na v2; v1 len RA, RSS, schema.org Event, HTML programy | Žiadny z 12 auditovaných podnikov nemá IG ako jediný zdroj; IG je najdrahšia a najkrehkejšia časť |
| 2026-10-29 | Vo v2 IG len cez oficiálne Graph API (Business Discovery), stories nescrapujeme | Zadarmo, stabilné; scraping je proti ToS a krehký |
| 2026-10-29 | Každý zdroj je samostatný adaptér s jednotným výstupom | Nové zdroje (vrátane IG) bez zásahu do zvyšku systému |
| 2026-10-29 | Štruktúrované zdroje majú prednosť pred HTML; priorita polí `ra` > `jsonld` > `rss` > `html` | Spoľahlivosť — **nahradené riadkom 2026-10-30** |
| 2026-10-30 | Resident Advisor sa nepoužíva ako zdroj dát; v1 zdroje sú len RSS, schema.org Event (JSON-LD), HTML. Priorita polí: `jsonld` > `rss` > `html`. Podnik môže mať `ra_url` ako odkaz na jeho RA profil. | Podmienky RA zakazujú boty a scrapery bez písomného povolenia. |
| 2026-10-31 | Čitárna Unijazz: `jsonld` adaptér, strategy `mec_ajax` — POST na `admin-ajax.php` pre aktuálny + 2 nasledujúce mesiace; `start_time = null`. Skin ID (47) v source config. | Stránka je JS-renderovaná; JSON-LD je v AJAX odpovediach MEC pluginu. WP REST API (`mec-events`) nevhodné — `date` je dátum publikácie, nie konania eventu. |
| 2026-10-31 | Kasárna Karlín: listing fetchujeme z `/en/program` (nie `/program`); `/program` dáva CS linky s `/index.php/` prefixom v statickom HTML. | Statické HTML `/program` vracia Drupal server-side render s CS slugmi; EN listing má správne EN linky. |
| 2026-10-31 | MeetFactory: listing je stránkovaný (`?page=N`, link `a.endless_more`); fetchujeme všetky stránky v okne +180 dní; hudba má 4 strany (~36 eventov), divadlo 2 strany (~11 eventov). | Prvá strana má len 10 eventov z ~36; bez stránkovania by pipeline vynechala väčšinu programu. |
| 2026-10-31 | Kasárna: `_parse_time_line` nemá limit na počet riadkov (pôvodný limit 50 bol príliš malý; reálne stránky majú čas na riadku ~374 surového textu). | Regex je dostatočne špecifický (`^HH:MM$`, `^H:MM AM/PM$`) — falošné zhody nehrozia. |
| 2026-10-31 | Čitárna Unijazz: po AJAX listingu fetchujeme detail každej akcie a parsujeme čas z `.event-time` (`DD. MM. YYYY HH:MM`). `follow_details: true, max_requests: 30` v source config. | Detail má čas, listing nie. |
| 2026-10-31 | Cross Club: `start_time` ostáva `null`. Detail stránky (3 overené) nemajú čas začiatku — ani standalone text, ani JSON-LD startDate s časom. | Čas nie je k dispozícii v žiadnom fetchovateľnom formáte na crossclub.cz. |
| 2026-10-31 | Spolupráca: rozhoduj samostatne; pýtaj sa len pri zmene dátového modelu, rozpore s decisions.md, novom type zdroja, prepise git histórie/force push, platenej službe alebo novom API kľúči. Ostatné zaznamenaj do decisions.md/status.md a zhrň v záverečnej správe. | Efektivita — väčšina rozhodnutí je technická a jednoznačná. |
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
| 2026-10-31 | v1 rozsah zahŕňa: obľúbené podniky („moje podniky"), onboarding pri prvom spustení (výber podnikov a formátov, každý krok preskočiteľný, uložený lokálne), osobné „going" (lokálne), tlačidlo „pridať do kalendára" (.ics). Bez účtu a backendu. | Minimálna ale použiteľná appka bez potreby registrácie. |
| 2026-10-31 | Profil a obľúbené cez jednu vrstvu (napr. `profileStore`), aby sa neskôr vymenila za sync s účtom bez prepisovania UI. | Neskôr budú účty (fáza 2), UI sa nesmie prepísať od základu. |
| 2026-10-31 | Mimo v1: sociálne „going", push notifikácie, mapa, Spotify, IG, natívna appka. Onboarding, personal going a obľúbené sú vo v1. | Viď aktualizovaný backlog v project.md. |
| 2026-10-31 | Fázy vydania: 1) v1 PWA bez účtu; 2) verejná PWA + Play Store (TWA) s účtami; 3) App Store + natívna appka. | Postupné vydávanie podľa dôvery v projekt. |
| 2026-10-31 | Poradie práce: 1–2 hotové; 3 adaptéry pre Cross, MeetFactory, Kasárna, Čitárna, Akropolis; 4 denný beh + GitHub Pages; 5 test LLM extrakcie (Twist, Akropolis ako kontrola); 6 minimálna PWA; 7 ďalšie podniky. | Viď project.md. |
| 2026-10-31 | `sold_out`: `true` len ak zdroj výslovne uvádza vypredané; `false` len ak výslovne ponúka lístky; inak `null`. | Aby sme neklasifikovali predčasne, keď lístky ešte nie sú v predaji. |
| 2026-10-31 | `room`: nepovinné pole, sála alebo priestor tak, ako ho uvádza zdroj. Akropolis: Velký sál, Malá scéna, Jazz Bar. | Relevantné pre podniky s viacerými sálami. |
| 2026-10-31 | Dátum bez roka (napr. Akropolis „4. 11."): dátum pred včerajškom → budúci rok. Ak by padol za +180 dní, akcia sa nezaradí. Pravidlo len pre adaptéry bez roka, s komentárom. | Konzistentné okno +180 dní pre všetky zdroje. |
| 2026-10-31 | Oznamy, ktoré nie sú akciami (napr. Čitárna „ZAVŘENO"), sa vyraďujú v adaptéri a logujú. Pravidlo dokumentované komentárom v adaptéri. | Udržať čistotu výstupu bez mlčanlivého ignorovania. |
| 2026-11-02 | Poradie práce (nahrádza riadok 2026-10-31): 1–2 hotové; 3 adaptéry hotové (Cross, MeetFactory, Kasárna, Čitárna, Akropolis); 4 denný beh + GitHub Pages; 5 test LLM extrakcie (Twist, Akropolis ako kontrola) → rozhodnutie vlastné parsery vs. LLM; 6 ďalšie podniky pred PWA, len tie čo pôjdu rýchlo (zložité parsery až po PWA); 7 zatriedenie akcií aspoň podľa sekcie zdroja; 8 minimálna PWA. | Matej chce mať v appke od začiatku čo najviac podnikov, ak sa dajú pridať rýchlo. Zatriedenie je prerekvizita pre použiteľný predvolený pohľad. |
| 2026-11-02 | Akropolis: akcie s miestom konania mimo vlastných priestorov (Velký sál, Malá scéna, Jazz bar) sa vyraďujú a logujú. Zoznam vlastných priestorov v `source_config.own_rooms` v `venues.json`. Ak akcia nemá sálu vôbec, zostáva (pravdepodobne Akropolis). | Akropolis vo výpise uvádza aj akcie, ktoré organizuje inde (Roxy, Archa+, Jazz Dock…); tieto patria k iným podnikom, ktoré budú mať vlastné zdroje. |
| 2026-11-02 | Akropolis vstupne_6 kódy: 1=predaj (Akropolis), 2=vyprodané, 3=vstup voľný, 4=JIŽ BRZY (ešte nie v predaji), 5=ZRUŠENO, 6=PŘELOŽENO, 11=predaj cez externý URL. Zdroj: `data` atribút `.kas_box6` elementov v HTML výpisu (index = kód, hodnota = text tlačidla). Kód 2 overený na webe (SPITFIRE DVACETJEDNA 2026-11-02 zobrazoval „Vyprodáno!"); kód 5 overený cez data atribút („ZRUŠENO!"). Kód 11: ticket_url = URL z `vstupne_6` (externý predajca). | Kódy odvodené zo stránky Akropolisu; pre spoľahlivosť len kódy s webovým overením nastavujú sold_out/status. |
| 2026-11-02 | commit hash v reporte úlohy = finálny hash na origin/main po pushi; ak sa pri rebase zmení, opraviť v ďalšom commite. Sekcia „Otvorené" nesmie byť „nič" ak sú známe obmedzenia. | Reporty 001–002 uvádzali nesprávny hash (lokálny pred pushom). |
| 2026-11-02 | Denný beh pipeline (GitHub Actions) a GitHub Pages sa zaraďujú pred test LLM (krok 4, nahrádza poradie z predošlého riadku). Dôvod: história prevádzky sa zbiera od začiatku a PWA potrebuje verejnú adresu dát. | História `first_seen`/`last_seen` je cenná od prvého behu. |
| 2026-11-02 | Denný beh nič necommituje do repa. `events.json` sa zverejní len na GitHub Pages (`actions/upload-pages-artifact` + `actions/deploy-pages`). `site/events.json` je v `.gitignore`. | Commity „denná aktualizácia" by sa zrážali s lokálnou prácou a zahltili históriu. |
| 2026-11-02 | Predošlý `events.json` si CI beh stiahne zo zverejnenej Pages adresy (`PREVIOUS_EVENTS_URL` env var). Na prvom behu (404) začne bez stavu a zaloguje to. Adresa nie je natvrdo v kóde. | Umožňuje sledovanie `first_seen`/`last_seen` aj `gone` bez commitovania stavu do repa. |
