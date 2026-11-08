# Klasifikačná review — 2026-11-08

Zdroj: `https://matejstolarik.github.io/eventapp/events.json`  
Vygenerované: `2026-11-08T21:13:41+01:00` (CI beh #9, workflow_dispatch, commit a9f6291)

## Súhrn

| Metrika | Hodnota |
|---|---|
| Celkom akcií | 377 |
| Metóda `llm` | 196 |
| Metóda `keyword` | 58 |
| Metóda `source` | 123 |

## Počty podľa podniku

| Podnik | Akcií |
|---|---|
| palac-akropolis | 87 |
| meetfactory | 42 |
| roxy | 42 |
| archa-plus | 62 |
| bike-jesus | 32 |
| citarna-unijazz | 12 |
| cross-club | 15 |
| epic | 23 |
| forum-karlin | 28 |
| fuchs2 | 23 |
| kasarna-karlin | 11 |

## Formáty (po AI klasifikácii)

| Formát | Počet |
|---|---|
| concert | 191 |
| dj | 88 |
| party | 58 |
| theatre | 62 |
| dance | 9 |
| film | 7 |
| talk | 6 |
| music | 4 |
| other | 5 |
| workshop | 4 |
| opening | 2 |
| quiz | 2 |
| comedy | 1 |

## `party` akcie (58 celkom)

AI pridelila `party` 58 akciám — prvý beh po pridaní formátu (cache bypass triggeroval prehodnotenie všetkých llm akcií s dj/concert/music bez party).

Vzorka pre manuálnu kontrolu (vybrané zaujímavé prípady):

| Podnik | Dátum | Názov | Formáty | Správne? |
|---|---|---|---|---|
| cross-club | 2026-11-08 | SUNDEJ SE SUNDAY | dj, party | ✅ |
| cross-club | 2026-11-11 | TECHNO  HOUSE | dj, party | ✅ |
| meetfactory | 2026-11-28 | Gutafest 2026 | concert, party | ✅ festival |
| meetfactory | 2027-02-27 | Winter Prague Gothic Treffen | party | ✅ |
| citarna-unijazz | 2026-11-20 | PSYTRANCE UNITED | dj, party | ✅ |
| fuchs2 | 2026-11-27 | Chinchilla ☆ Jolina Louise | dj, party | ✅ |
| fuchs2 | 2026-12-01 | High on Fire ☆ Cancer Void | concert, dj, party | ✅ metal festival s aftery |
| bike-jesus | 2026-11-11 | Dudlíkfest 2026 | concert, party | ✅ festival |
| archa-plus | 2026-11-20 | Amphibian Quadrophonic Soundsystem | dj, party | ✅ |
| epic | 2026-11-08 | SUNDAY RITUALS - REGGAETON & LATINO | dj, party | ✅ všetky EPIC = party |

Všetkých 23 akcií EPIC správne `dj + party` — sú to klubové noci.  
Cross Club má 11 `dj + party` — zodpovedá charakteru (techno/house klub).

## Zostatok `music` (4 akcie)

AI nevedela určiť live vs. dj pre 4 akcie — `music` je fallback.  
Príklady: Čitárna Unijazz (kultúrne akcie, žáner nejasný z názvu).

## Záver

AI klasifikácia funguje správne. `party` formát pridelený konzistentne pre klubové noci a festivaly s párty charakterom. EPIC Prague 23/23 = `dj + party` je správne. Falošne pozitívne: 0 viditeľných. Falošne negatívne: Roxy — Roxy prideľuje `party` cez `data-hashtags`, nie AI, takže táto review sa týka len AI-klasifikovaných akcií.
