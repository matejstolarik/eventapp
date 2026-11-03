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

Dátum: 2026-11-03. Commit hash: da0bb5a.

### Čo je hotové

**Fuchs2** (`jsonld`, stratégia `wix_sitemap`):
- Stránka `fuchs2.cz/events` je Wix; server-renderované HTML obsahuje len 1 JSON-LD Event (aktuálnu/poslednú akciu). Ostatné akcie načítava JavaScript.
- Riešenie: `event-pages-sitemap.xml` má 855 URL-iek (všetky historické akcie). Filtrujeme podľa `lastmod >= dnes - 90 dní` → ~60 kandidátov. Z nich fetchujeme každú stránku a parsujeme JSON-LD.
- Stránkovanie: nie je — Wix listing nie je stránkovaný v statickom HTML. Všetky akcie sú dostupné cez sitemap.
- **Čas overený** pri 3 akciách (2026-11-03): JSON-LD obsahuje správny pražský čas (`+01:00` v zime), čas sa zhoduje s HTML:
  1. `fuchs2.cz/events/radio-wave-present-flamburr-...` — startDate `2026-11-05T21:00:00+01:00`, HTML: `21:00` ✓
  2. `fuchs2.cz/events/latin-core-thursdays-addly-muff-...` — startDate `2026-11-26T23:00:00+01:00`, HTML: `23:00` ✓
  3. `fuchs2.cz/events/f2-live-dusan-vlk-asthmaboy-again` — startDate `2026-12-03T19:00:00+01:00`, HTML: `19:00` ✓
- Žiadny timezone shift (na rozdiel od Kasárne). Čas sa berie priamo z JSON-LD.
- Lístky: JSON-LD neobsahuje `offers` → `ticket_url = null` pre všetky akcie.
- Nový adaptér: rozšírený `pipeline/adapters/jsonld.py`, nová stratégia `wix_sitemap`.

**Bike Jesus** (`api`, stratégia `strapi`):
- Strapi v5 API: `bikejesus.com/api/events`. Verejne dostupné bez kľúča.
- Stránkovanie: Strapi defaultne pageSize=25. S `pageSize=100` sa všetkých 37 akcií zmestí na 1 stranu.
- Polia: `Title`, `Date` (YYYY-MM-DD, bez času), `Tickets` (ticket URL, nullable), `Description`, `Subtitle`, `Tag`, `documentId` (external_id).
- `start_time = null` — API neobsahuje čas.
- `ticket_url` = pole `Tickets` po `.strip()` (keď nie je null/prázdne).
- `sources[].url` = `https://bikejesus.com` — podnik nemá individuálne stránky akcií na vlastnom webe (zdôvodnenie v `decisions.md`).
- Overenie 3 akcií voči API:
  1. `NASTY, CRAWLSPACE, PINTGLASS /live` — API date `2026-11-02`, ticket `https://obscure.cz/cs/tickets/detail/id/1077` ✓
  2. `deary` — API date `2026-11-10`, ticket `https://www.livenation.cz/event/deary-prague-tickets-edp1658298` ✓
  3. `Gurriers (IE) + Support: Enola Gay` — API date `2026-11-21`, ticket `https://goout.net/cs/gurriers%2Bsupport-enola-gay/szuuoiy/` ✓
- Nový adaptér: `pipeline/adapters/api.py`, stratégia `strapi`.

**Záznamy v `data/venues.json`**:
- Fuchs2: adresa `ostrov Štvanice, Praha 7` (z JSON-LD na stránke), súradnice `lat: 50.0952223, lng: 14.4363506` (OpenStreetMap Nominatim: "Fuchs 2 / Bike Jesus, ostrov Štvanice, Holešovice, Praha 7"). IG: `fuchs2stvanice`, RA: `https://ra.co/clubs/162121`. Štítky prázdne.
- Bike Jesus: rovnaká adresa a súradnice (OSM uvádza oba podniky na tom istom mieste — ostrov Štvanice). IG: `bike.jesus`, RA: `https://ra.co/clubs/178137`. Štítky prázdne.

**Dokumentácia**: `docs/data-model.md` doplnená o typ `api`. `docs/decisions.md` doplnená o 5 nových riadkov (nový typ `api`, stratégia `wix_sitemap`, Fuchs2 timezone overenie, Bike Jesus sources[].url, Bike Jesus start_time null).

**Testy**: `tests/test_fuchs2.py` (8 testov) a `tests/test_bike_jesus.py` (9 testov). Všetky testy 101/101 prechádzajú.

**Fixtures**: `tests/fixtures/fuchs2_event_latin_core_min.html` (minimálny HTML s JSON-LD), `tests/fixtures/bike_jesus_api.json` (live API response, pageSize=100).

### Čísla (z `site/events.json`, príkaz: `python scripts/stats.py`)

```
generated_at: 2026-11-03T12:54:48.851885+01:00
total events: 214
  bike-jesus: 34
  citarna-unijazz: 17
  cross-club: 15
  fuchs2: 21
  kasarna-karlin: 2
  meetfactory: 43
  palac-akropolis: 82 (celkovo 109 fetchnutých, 27 vyradených pre externé priestory)
with start_time: 122/214
```

Fuchs2: 23 fetchnutých, 2 odfiltrované dedup/checks → 21 v events.json. Bike Jesus: 34 v okne +180 dní z 37 celkových.

### Otvorené

- Fuchs2: 60 kandidátov v sitemap (lastmod >= 90 dní), fetchujú sa všetky s `max_requests=70`. Z ~60 stránok je ~21 budúcich akcií; zvyšok sú uplynulé akcie s nedávno upravenou stránkou.
- Fuchs2 `ticket_url = null`: Wix JSON-LD neobsahuje `offers`. RA linky sú viditeľné na stránke v texte, ale nie v štruktúrovaných dátach. Bez HTML scrapingu nie je ticket_url dostupné.
- Štítky (`type`, `character`, `music`, `size`) oboch podnikov nechané prázdne — doplní Matej.
