# 014: Prieskum komerčných klubov

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-04. Robí sa po úlohe 013. Len prieskum ako v úlohe 008: žiadne adaptéry, žiadna zmena `venues.json` ani pipeline.

Matej chce pred PWA pridať 2–3 veľké komerčné kluby (ťahák, chodí tam veľa ľudí pravidelne). Kandidáti podľa Mateja: **EPIC, Duplex, Roxy, Lucerna**. Pri Lucerne zisti, či ide o Lucerna Music Bar (klub) a/alebo Palác Lucerna (Velký sál); uveď oboje, ak majú vlastný program.

### Pre každý podnik zisti (ako v úlohe 008)
1. Či podnik funguje (aktuálny program, nie zatvorený/premenovaný). Oficiálny web over (adresa, IG), nič nedomýšľaj.
2. URL stránky s programom; či program nie je len na Instagrame/Facebooku/RA (RA nikdy nesťahuj).
3. Štruktúrované zdroje: RSS/iCal, schema.org Event (JSON-LD), JSON rozhranie webu.
4. Ak nič: pravidelnosť HTML, JavaScript, stránkovanie.
5. Údaje: dátum, čas, názov, interpreti/DJ, cena, lístky, sekcie.
6. `robots.txt`, odpoveď nášmu `fetch.py`.
7. Počet akcií v okne +180 dní (približne).
8. Náročnosť: rýchle / parser / ťažké / bez zdroja.

### Podklady pre štítky (nové typy podnikov, štítky sa budú riešiť po prieskume)
Pre každý podnik zapíš so zdrojom (URL): ako sa sám popisuje, aká hudba a typy večerov (napr. hity 80. a 90. rokov, R&B, house, techno…), kapacita, či ide o turistický/študentský/klubový podnik. Ak niečo nenájdeš, napíš to.

Ulož 1 vzorku HTML programu na podnik do `tests/fixtures/survey/`.

### Report navyše
- Tabuľka podnikov s bodmi 1–8.
- Odporúčanie, ktoré 2–3 pridať pred PWA (najväčší ťahák a zároveň rýchle), a čo odložiť.
- Podklady pre štítky so zdrojmi.

## Report
