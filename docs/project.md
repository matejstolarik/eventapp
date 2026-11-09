# Projekt: Aplikácia na akcie v obľúbených podnikoch (pracovný názov)

## Cieľ
Aplikácia, kde si používateľ pridá obľúbené podniky a na pár klikov vidí, čo sa v nich deje (koncerty, party, kultúra, aj menšie a undergroundové akcie). Začíname v Prahe. Primárne pre autora (Matej), návrh nesmie brániť tomu, aby ju neskôr používali aj iní.

## Hodnota a odlíšenie od GoOut
- **Praktickosť:** v telefóne na dva kliky vidíš, čo sa v meste deje v zvolenom období.
- **Dva hlavné momenty použitia:** nudíš sa doma a pozeráš, čo je dnes či tento týždeň; alebo už si v meste a hľadáš akcie okolo seba.
- **Aktuálnosť** akcií je kľúčová, ale vzdialenejšie akcie (do pol roka) sú tiež k dispozícii.
- UX postavené na „moje podniky”.

## Rozsah v1
- Podniky pridáva autor ručne do `data/venues.json`.
- Zdroje: RSS, schema.org Event (JSON-LD), HTML programy webov. Resident Advisor nie je zdroj dát, len odkaz `ra_url` na profil podniku. Instagram nie je zdroj dát, len odkaz `instagram` v profile podniku.
- Pipeline denne vygeneruje `events.json`, PWA ho číta.
- Predvolený pohľad: hudobné akcie (`live`, `dj`). Divadlo, vernisáže, film, kvízy a iné cez filter.
- Jazyky UI: čeština (primárne), slovenčina, angličtina. Štítky v dátach len anglicky.
- **Obľúbené podniky** („moje podniky”): každý používateľ si vyberá, ktoré podniky sleduje.
- **Onboarding** pri prvom spustení: výber podnikov a formátov, žánre až po vzniku zoznamu; každý krok preskočiteľný; uložený lokálne.
- **Osobné „going”**: lokálne uložený zoznam „moje akcie”.
- **Pridať do kalendára**: tlačidlo na stiahnutie `.ics` súboru akcie.
- **Mapa akcií**: interaktívna mapa podnikov na úvodnej obrazovke. Knižnica: MapLibre GL JS, podklad OpenFreeMap (bez API kľúča). Dizajn, farby, markery, panel a ovládanie podľa `docs/design.md`.
- Bez účtu a bez backendu v1. Profil a obľúbené cez jednu vrstvu (napr. `profileStore`), aby sa neskôr dala vymeniť za sync s účtom bez prepisovania UI.
- Odkazy na akcie a podniky musia fungovať bez prihlásenia a stáť na nemennom `id`.

## Mimo v1 (backlog)
- Sociálne „going” (kto ešte ide) a push notifikácie.
- Účty a registrácia.
- Odkaz na interpreta na Spotify.
- Natívna appka pre Play Store a App Store (pravdepodobne React Native / Expo), ak sa projekt osvedčí.

### Odložené nápady (bez plánu)
- **Instagram ako zdroj** (odložené 2026-11-02): Graph API (Business Discovery), extrakcia z postov LLM. Dôvod odloženia: zložité na nastavenie (Meta developer účet, business účty podnikov); takmer každý podnik má web s programom. Podmienka návratu: ak sa ukáže, že dôležité podniky majú program len na Instagrame. Podniky, ktoré program zverejňujú len na Instagrame, majú v appke profil bez akcií.

## Fázy vydania
1. **v1 PWA** pre Mateja a kamarátov, bez účtu; onboarding, personal going, .ics.
2. **Verejná PWA + Play Store** (Trusted Web Activity) s účtami: registrácia na začiatku s možnosťou preskočiť, sync profilu, mazanie účtu v appke, sociálne „going”, push notifikácie.
3. **App Store a natívna appka** (pravdepodobne React Native / Expo) až pri dôvere v projekt.

Dôsledok pre v1: odkazy na akcie a podniky musia fungovať bez prihlásenia a stáť na nemennom `id`.

## Poradie práce
1. Audit zdrojov (hotové pre vzorku 12 podnikov)
2. Dátový model (hotové okrem zoznamu žánrov)
3. Adaptéry pre súčasné podniky (Cross Club, MeetFactory, Kasárna, Čitárna, Akropolis) — **hotové**
4. Pipeline end-to-end, denný beh + GitHub Pages
5. Test LLM extrakcie nad HTML (Twist, Akropolis ako kontrola) → rozhodnutie: vlastné parsery vs. LLM
6. Ďalšie podniky (pred PWA; len tie, ktoré pôjdu rýchlo — zložité parsery na mieru až po PWA)
7. Zatriedenie akcií aspoň podľa sekcie zdroja (bez neho je predvolený pohľad `live` + `dj` prázdny)
8. Minimálna PWA
