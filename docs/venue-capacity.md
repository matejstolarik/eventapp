# Kapacity pražských podnikov (prieskum hlavného chatu 2026-11-19)

Podklad pre pole `capacity` vo `data/venues.json` (zoradenie „Veľkosť“, úloha 073) a pre budúce podniky. **Pravidlo:** do `venues.json` ide len číslo so zdrojom; kde zdroj nie je, `null`. Odhady (napr. Matejov rýchly zoznam z AI 2026-11-19) sa nezapisujú.

Spoľahlivosť: **oficiálny** = web podniku, prevádzkovateľa, provozní řád, technický rider, mesto (prague.eu, praha.eu); **sekundárny** = Wikipedia, predajcovia lístkov, adresáre; **slabý** = turistické weby, recenzie.

## Naše podniky (v appke)

| Podnik (`id`) | Dnes vo `venues.json` | Zistené v prieskume | Zdroj | Poznámka |
|---|---|---|---|---|
| Forum Karlín (`forum-karlin`) | 3800 | **až 3000** (oficiálny) | prague.eu/cs/objevujte/forum-karlin/; prazsky.denik.cz (Bestsport: „kapacitou asi 3000 osob“); forbes.cz (zmenšenie na 1500) | **Rozpor:** 3800 je z Cvent (`notes`: 3800 stánie, 1800 sedenie, sekundárny); prevádzkovateľ a mesto uvádzajú do 3000 → návrh **3000** |
| Palác Akropolis (`palac-akropolis`) | 700 | veľký sál 700, malý 80 (sekundárny) | liveurope.eu/node/22 | Sedí (zdroj z 013) |
| MeetFactory (`meetfactory`) | 750 | koncertná sála 750, zmenšená 350 (oficiálny) | meetfactory.cz/en/hudebni-dramaturgie, meetfactory.cz/en/informace-pro-kapely | Sedí |
| Archa+ (`archa-plus`) | 1200 | 2 sály spolu do 1200 (sekundárny) | goout.net/pl/archa+/vzljb/; 013: archatheatre.cz (200–350 sedenie, do 1200 stánie) | Sedí |
| ROXY (`roxy`) | 750 | 750 stánie, 330 sedenie (sekundárny); iné weby 1000 | ticketmaster.cz/venue/roxy-praha-1-tickets/roxy/105; cvent.com | Sedí |
| EPIC (`epic`) | 600 | „cez 1500“ (slabý) | top-10-in-prague.com (recenzia GetYourGuide) | 600 je od Mateja (019); 1500 len zo slabého zdroja – nemeniť bez oficiálneho |
| Fuchs2 (`fuchs2`) | 650 | nenájdené v tomto prieskume | 013: selection.cz/en/venues/fuchs2 | Ponechať |
| Cross Club (`cross-club`) | 250 | nenájdené (oficiálne číslo nie je) | – | 250 schválil Matej v 013, zdroj v `notes` nie je; ponechať, doplniť „podľa Mateja“ |
| Bike Jesus (`bike-jesus`) | 280 | do 280 (sekundárny) | kdykam.com/en/venue/bike-jesus-praha-165/ | Sedí |
| Kasárna Karlín (`kasarna-karlin`) | null | Garáže 150 sedenie / 300 stánie, Bazén 60–90 (oficiálny, projekt pre MHMP); dvor neznámy | [Podrobný popis projektu Kasárna Karlín](https://eud-vis.praha.eu/pub/deska/6000004/4/6000003%23MHMPAWO0A020%23MHMP0BTA07MH%230/6000003%23MHMPAWO0A020%23MHMP0BT9Q9G0/Podrobný_popis_projektu_Kasárna_Karlín_anonymizovany.pdf) (eud-vis.praha.eu) | Návrh **300** (najväčší vnútorný priestor so zdrojom); od 2025 max. 3 koncerty ročne na dvore |
| Čítárna Unijazz (`citarna-unijazz`) | null → 70 (073) | sál s barem cca 70, salonek 10–15 (oficiálny) | citarna.unijazz.cz/pronajem-prostor/ | Nájdené v úlohe 073 na oficiálnom webe |

## Navrhnuté a budúce podniky

| Podnik | Kapacita | Spoľahlivosť | Zdroj |
|---|---|---|---|
| O2 arena | do 20 000 (koncert) | oficiálny | o2arena.cz/?p=2376 |
| O2 universum, sál A | 4500 (celý komplex 10 000) | oficiálny | o2universum.cz brožúra; prague.eu/cs/objevujte/o2-universum/ |
| Sportovní hala Fortuna (bývalá Tipsport arena, premenovaná 2022) | koncerty 8000 | oficiálny (mesto) | prague.eu/cs/objevujte/sportovni-hala-fortuna/ |
| Palác Lucerna, Velký sál | do 2500 | oficiálny (mesto) | prague.eu/cs/objevujte/palac-lucerna-velky-sal/ |
| SaSaZu | 2500 | sekundárny | prague-trip.com/nightlife/best-clubs/; karlobag.eu |
| Lucerna Music Bar | 800 (iný web ~1000) | sekundárny | en.wikipedia.org/wiki/Lucerna_Music_Bar |
| Futurum Music Bar | do 500 | sekundárny | cz.mticket.eu/en/concert/futurum-music-bar-1993.html |
| Jatka78, hlavná sála | 342 sedenie | oficiálny (rider) | jatka78.cz (technický rider) |
| Kino Aero | 323 | oficiálny (provozní řád) | kinoaero.cz/attachments/Provozni-rad-kino-aero.pdf |
| Café v lese (klub v suteréne) | 150 | slabý | mapstr.com (citát) |
| Karlovy lázně | nenájdené (5 klubov na 5 poschodiach) | – | prague.eu |
| Jazz Dock, Rock Café, Mecca, Chapeau Rouge, Retro Music Hall, Duplex, Jazz Republic, El Magico, Twist Bar, Magneto, Popocafepetl, Kolektor, Acid Coffee, Střecha Radost | nenájdené / nehľadané | – | doplniť pri pridaní podniku |

## Pozor
- Kapacita je veľkosť budovy alebo sály, nie návštevnosť akcie. Podniky s viacerými sálami (Akropolis, MeetFactory, Archa+, Kasárna, O2 universum) majú pri akcii v menšej sále oveľa menej ľudí.
- Pri zmene sa číslo aj zdroj zapisujú do `notes` podniku.

## Doplnené Matejom 2026-11-20 (po prieskume 083)
| Podnik | Kapacita | Zdroj |
|---|---|---|
| Lucerna Music Bar | 1000 návštevníkov | Matej |
| O2 universum | Sál A (koncertný) cca 5 200; zvyšných cca 4 800 v 37 ďalších sáloch a priestoroch | Matej |
| Jazz Republic | ~150 (plán stolov: 130 miest; zaokrúhlené nahor) | Matej, plán rezervácie |
| El Magico | 300 | Matej |
| Karlovy Lázně | 1000 | Matej |
| O2 arena | až 20 000 | web (083) |
| SaSaZu | 2000 | web (083) |
| Sportovní hala Fortuna | 5 500 sedenie + 3 500 státie | web (083) |
| Duplex | „over 2000“ | web (083) |
| Kongresové centrum, Kongresový sál | 2 764 | web (083) |
