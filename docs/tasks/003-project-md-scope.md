# 003: Zosúladiť docs/project.md s rozhodnutiami z 2026-10-31

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02. Začni až po dokončení úlohy 002. Len dokumentácia, žiadny kód.

`docs/project.md` je v rozpore s rozhodnutiami z 2026-10-31. Oprav:
1. Rozsah v1 obsahuje aj: obľúbené podniky („moje podniky“), onboarding pri prvom spustení (výber podnikov a formátov, žánre až po vzniku zoznamu; každý krok preskočiteľný; uložený lokálne), osobné „going“ (lokálne, zoznam „moje akcie“) a tlačidlo „pridať do kalendára“ (`.ics`). Bez účtu a bez backendu. Profil a obľúbené cez jednu vrstvu (napr. `profileStore`), aby sa neskôr dala vymeniť za sync s účtom bez prepisovania UI.
2. Mimo v1: účty a registrácia, sociálne „going“ (kto ešte ide), push notifikácie, mapa, Spotify, IG, natívna appka. Z backlogu odstráň follow, going a onboarding (sú vo v1).
3. Pridaj sekciu „Fázy vydania“: 1) v1 PWA pre Mateja a kamarátov, bez účtu; 2) verejná PWA aj v Play Store (Trusted Web Activity) s účtami: registrácia na začiatku s možnosťou preskočiť, sync profilu, mazanie účtu v appke, sociálne „going“, push notifikácie; 3) App Store a natívna appka (pravdepodobne React Native / Expo) až pri dôvere v projekt. Dôsledok už pre v1: odkazy na akcie a podniky musia fungovať bez prihlásenia a stáť na nemennom `id`.
4. „Poradie práce“: 1 až 2 hotové; 3 adaptéry pre súčasné podniky (Cross, MeetFactory, Kasárna, Čitárna, Akropolis); 4 test LLM extrakcie nad HTML (Twist, Akropolis ako kontrola) → rozhodnutie vlastné parsery vs. LLM; 5 minimálna PWA; 6 ďalšie podniky.
5. Tieto rozhodnutia (2026-10-31) pridaj do `docs/decisions.md` ako nové riadky.

## Report
