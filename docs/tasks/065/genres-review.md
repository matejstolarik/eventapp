# Žánre na kontrolu

Zdroj: `site/events.json` (generated_at 2026-11-18T00:25:40.356663+01:00), príkaz: `python -m pipeline.genres_review site/events.json <výstup>`.
Kandidáti a navrhnuté mapovania len od 2 akcií; zahodení kandidáti (`data/genre_ignored.json`) a už schválené názvy sa nevypisujú.
Akcie s AI doplnením: 241 z 372.

Matej: pri každom riadku napíš áno / nie (alebo iný cieľ). Schválené mapovania pôjdu do `data/genre_aliases.json`, schválené nové žánre do zoznamu v `pipeline/genres.py`.

## 1. Schválené mapovania (`data/genre_aliases.json`)

| surový názov | náš žáner |
|---|---|
| acid house | house |
| afro house | house, afro |
| afro-fusion | afro |
| alt. rock | alternative-rock |
| ambient techno | techno, ambient |
| booty house | house |
| breaks | breakbeat |
| d&b | drum-and-bass |
| dnb | drum-and-bass |
| doom metal | doom-metal |
| drum n bass | drum-and-bass |
| drum'n'bass | drum-and-bass |
| drumandbass | drum-and-bass |
| dub step | dubstep |
| electronic dance music | edm |
| electropop | pop, electronic |
| emo-rap | hip-hop |
| folk-rock | folk, rock |
| glitch pop | pop |
| hard techno | hard-techno |
| hardcore rave | rave |
| hardtechno | hard-techno |
| hiphop | hip-hop |
| indie pop | indie, pop |
| latino | latin |
| mainstage | edm, electronic |
| noise rock | noise-rock |
| psy trance | psytrance |
| psychedelic trance | psytrance |
| queer rave | rave |
| r&b | rnb |
| r'n'b | rnb |
| ragga | dancehall |
| raggajungle | jungle |
| rap | hip-hop |
| sludge | sludge-metal |
| sludge metal | sludge-metal |
| současný tanec | contemporary-dance |
| stoner metal | stoner-metal |
| ukg | uk-garage |
| šanson | chanson |

## 2. Mapovania navrhnuté AI (ešte neschválené)

Surový názov sa mapoval na žáner zo zoznamu (pravopisný variant alebo synonymum).

| surový názov | druh | → náš žáner | akcií | príklady | schváliť? |
|---|---|---|---|---|---|
| – | | | | | |

## 3. Kandidáti bez žánru zo zoznamu (`maps_to: null`)

Nový žáner do zoznamu, mapovanie na existujúci, alebo nič.

| surový názov | druh | akcií | príklady | rozhodnutie |
|---|---|---|---|---|
| – | | | | |

## 4. Použité žánre (počet akcií v `events.json`)

| žáner | akcií |
|---|---|
| rock | 53 |
| pop | 41 |
| electronic | 40 |
| indie | 39 |
| techno | 37 |
| hip-hop | 35 |
| house | 35 |
| folk | 24 |
| drum-and-bass | 23 |
| edm | 20 |
| metal | 18 |
| experimental | 17 |
| jazz | 16 |
| punk | 12 |
| post-punk | 9 |
| rnb | 9 |
| hardcore | 7 |
| world | 7 |
| trance | 6 |
| blues | 6 |
| bass-music | 5 |
| metalcore | 5 |
| shoegaze | 4 |
| tech-house | 4 |
| electro | 4 |
| latin | 4 |
| slowcore | 4 |
| disco | 4 |
| dubstep | 3 |
| ambient | 3 |
| funk | 3 |
| death-metal | 3 |
| industrial | 3 |
| electro-swing | 2 |
| reggae | 2 |
| darkwave | 2 |
| uk-bass | 2 |
| dream-pop | 2 |
| uk-garage | 2 |
| physical-theatre | 2 |
| hardstyle | 2 |
| ebm | 1 |
| oldies | 1 |
| rave | 1 |
