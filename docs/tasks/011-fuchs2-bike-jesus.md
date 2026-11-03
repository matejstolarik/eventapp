# 011: Fuchs2 a Bike Jesus

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-03. Podklady z prieskumu (úloha 008, fixtures v `tests/fixtures/survey/`). Obe sú Matejove prioritné podniky.

### Fuchs2 (`jsonld`)
- Program: https://fuchs2.cz/events (Wix, JSON-LD Event v HTML zo servera).
- Zisti, koľko akcií je v HTML a či Wix stránkuje (ďalšie stránky / „načítať viac“). Ak sa nedá dostať k akciám v okne +180 dní bez prehliadača, napíš to do reportu a sprav, čo sa dá.
- **Čas neber naslepo** (poučenie z Kasární, kde JSON-LD mal posunuté časové pásmo): porovnaj čas z JSON-LD s časom zobrazeným na stránke akcie aspoň pri 3 akciách. Ak nesedí, platí čas zo stránky.
- Lístky často vedú na Resident Advisor: odkaz na RA ako `ticket_url` je v poriadku (je to len odkaz). Z RA nikdy nič nesťahuj.

### Bike Jesus (nový typ zdroja `api`, odsúhlasené Matejom 2026-11-03)
- JSON rozhranie, ktoré používa samotný web: https://bikejesus.com/api/events (Strapi). Zapíš nový typ zdroja do `docs/data-model.md` a `docs/decisions.md`: JSON rozhranie webu podniku, len verejne dostupné bez prihlásenia a bez kľúča.
- Polia podľa prieskumu: `Title`, `Date` (bez času), `Link` (často Facebook), `Description`, `Subtitle`. Čas nedomýšľaj. Ak web má vlastnú stránku akcie, daj ju do `sources[].url`; inak zváž, čo je správne (stránka programu podniku vs. odkaz z `Link`) a zdôvodni v reporte.
- Over, či rozhranie nemá stránkovanie (Strapi zvyčajne áno) a či vracia všetky akcie v okne.

### Spoločné
- Záznamy v `venues.json`: IG Fuchs2 `fuchs2stvanice`, Bike Jesus `bike.jesus`; `ra_url` Fuchs2 https://ra.co/clubs/162121, Bike Jesus https://ra.co/clubs/178137; adresa z webu podniku (uveď URL) a súradnice z overiteľného zdroja (napr. OpenStreetMap), nič neodhaduj. Štítky nechaj prázdne.
- Fixtures, testy, pipeline, `status.md`, `scripts/stats.py` v reporte, overenie 3 akcií na podnik voči webu (URL, dátum, čas).

## Report
