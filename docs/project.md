# Projekt: Aplikácia na akcie v obľúbených podnikoch (pracovný názov)

## Cieľ
Aplikácia, kde si používateľ pridá obľúbené podniky a na pár klikov vidí, čo sa v nich deje (koncerty, party, kultúra, aj menšie a undergroundové akcie). Začíname v Prahe. Primárne pre autora (Matej), návrh nesmie brániť tomu, aby ju neskôr používali aj iní.

## Hodnota a odlíšenie od GoOut
- **Praktickosť:** v telefóne na dva kliky vidíš, čo sa v meste deje v zvolenom období.
- **Dva hlavné momenty použitia:** nudíš sa doma a pozeráš, čo je dnes či tento týždeň; alebo už si v meste a hľadáš akcie okolo seba.
- **Aktuálnosť** akcií je kľúčová, ale vzdialenejšie akcie (do pol roka) sú tiež k dispozícii.
- UX postavené na „moje podniky“.
- Pokrytie malých podnikov, ktoré zverejňujú program len na Instagrame, príde vo v2.

## Rozsah v1
- Podniky pridáva autor ručne do `data/venues.json`.
- Zdroje: Resident Advisor, RSS, schema.org Event, HTML programy webov. Instagram až vo v2.
- Pipeline denne vygeneruje `events.json`, PWA ho číta.
- Predvolený pohľad: hudobné akcie (`live`, `dj`). Divadlo, vernisáže, film, kvízy a iné cez filter.
- Jazyky UI: čeština (primárne), slovenčina, angličtina. Štítky v dátach len anglicky.

## Mimo v1 (backlog)
- Instagram ako zdroj (Graph API, Business Discovery, extrakcia z postov LLM).
- Mapa akcií dnes v Prahe (obľúbené alebo všetky podniky, s filtrami).
- Follow podnikov a „going“ pri akciách; onboarding s výberom podnikov a záujmov.
- Účty a registrácia.
- Odkaz na interpreta na Spotify.
- Natívna appka pre Play Store a App Store (pravdepodobne React Native / Expo), ak sa projekt osvedčí.

## Poradie práce
1. Audit zdrojov (hotové pre vzorku 12 podnikov)
2. Dátový model (hotové okrem zoznamu žánrov)
3. Adaptéry zdrojov
4. Pipeline end-to-end, týždeň prevádzky
5. PWA
