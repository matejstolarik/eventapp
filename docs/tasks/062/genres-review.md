# Žánre na kontrolu (úloha 062)

Zdroj: `site/events.json` (generated_at 2026-11-17T20:44:17.601749+01:00), príkaz: `python -m pipeline.genres_review site/events.json docs/tasks/062/genres-review.md`.
Akcie s AI doplnením: 243 z 374.

Matej: pri každom riadku napíš áno / nie (alebo iný cieľ). Schválené mapovania pôjdu do `data/genre_aliases.json`, schválené nové žánre do zoznamu v `pipeline/genres.py`.

## 1. Schválené mapovania (`data/genre_aliases.json`)

| surový názov | náš žáner |
|---|---|
| ambient techno | techno, ambient |
| d&b | drum-and-bass |
| dnb | drum-and-bass |
| drum n bass | drum-and-bass |
| drum'n'bass | drum-and-bass |
| drumandbass | drum-and-bass |
| dub step | dubstep |
| electronic dance music | edm |
| hiphop | hip-hop |
| latino | latin |
| mainstage | edm, electronic |
| psy trance | trance |
| psychedelic trance | trance |
| psytrance | trance |
| queer rave | rave |
| r&b | rnb |
| r'n'b | rnb |
| rap | hip-hop |
| reggaeton | latin |
| ukg | uk-garage |

## 2. Mapovania navrhnuté AI (ešte neschválené)

Surový názov sa mapoval na žáner zo zoznamu (pravopisný variant alebo synonymum).

| surový názov | druh | → náš žáner | akcií | príklady | schváliť? |
|---|---|---|---|---|---|
| – | | | | | |

## 3. Kandidáti bez žánru zo zoznamu (`maps_to: null`)

Nový žáner do zoznamu, mapovanie na existujúci, alebo nič.

| surový názov | druh | akcií | príklady | rozhodnutie |
|---|---|---|---|---|
| breakbeat | music | 3 | PRODIGY AFTERPARTY & RAVE (cross-club-2026-11-23-prodigy-afterparty-rave); GUTT3RCLUB x GLITTER.HIT: Ship Sket ☆ Ke (fuchs2-2026-12-11-gutt3rclub-x-glitter-hit-ship-sket-kewu-domizako); X CLUB. (roxy-2026-11-20-x-club) | |
| drama | film | 3 | Transgender Awareness Week: Lola (kasarna-karlin-2026-11-18-transgender-awareness-week-lola); Transgender Awareness Week: The Danish G (kasarna-karlin-2026-11-19-transgender-awareness-week-the-danish-girl); The Stranger (2025) (kasarna-karlin-2026-11-24-the-stranger-2025) | |
| hyperpop | music | 3 | Live Nation: Tiffany Day (meetfactory-2026-11-27-live-nation-tiffany-day); Mat213 – křest desky a medley největších (archa-plus-2026-11-27-mat213-krest-desky-a-medley-nejvetsich-hitu); ADÉLA (forum-karlin-2027-01-11-adela) | |
| alternative | music | 2 | Syrový tóny + Katka Šarközi (citarna-unijazz-2026-11-26-syrovy-tony-katka-sarkozi); VYPRODÁNO: COLORFACTORY (roxy-2026-11-18-vyprodano-colorfactory) | |
| animation | film | 2 | ANIMAGLAJZ – animations from Sutnarka (kasarna-karlin-2026-11-20-animaglajz-animations-from-sutnarka); REEAL TIME 3 (archa-plus-2026-12-14-reeal-time-3) | |
| cabaret | music | 2 | VLTAVA - STO LET S VÁMI (palac-akropolis-2026-11-20-vltava-sto-let-s-vami); VLTAVA - STO LET S VÁMI (palac-akropolis-2026-11-21-vltava-sto-let-s-vami) | |
| chanson | music | 2 | Anna Jozefína a Pruhovaný holub (citarna-unijazz-2026-12-08-anna-jozefina-a-pruhovany-holub); VLTAVA - STO LET S VÁMI (palac-akropolis-2026-11-21-vltava-sto-let-s-vami) | |
| country | music | 2 | Žižkovská benefice: C Pentane + Banana S (citarna-unijazz-2026-12-03-zizkovska-benefice-c-pentane-banana-split-srpr-deti-deste); FRANTIŠEK SKÁLA & TŘASKAVÁ SMĚS ►KŘEST N (palac-akropolis-2026-12-04-frantisek-skala-traskava-smes-krest-noveho-alba-zklamal) | |
| documentary | film | 2 | I'm Not Everything I Want to Be (kasarna-karlin-2026-11-17-i-m-not-everything-i-want-to-be); Citizen Havel (kasarna-karlin-2026-11-17-citizen-havel) | |
| electropop | music | 2 | F2 LIVE: Metastavy ☆ Tante Elze (fuchs2-2026-12-13-f2-live-metastavy-tante-elze); ADÉLA (forum-karlin-2027-01-11-adela) | |
| grime | music | 2 | FAMILY THERAPY present Asher ☆ Parashoot (fuchs2-2026-11-21-family-therapy-present-asher-parashoot-fahell-zecco-millo); GUTT3RCLUB x GLITTER.HIT: Ship Sket ☆ Ke (fuchs2-2026-12-11-gutt3rclub-x-glitter-hit-ship-sket-kewu-domizako) | |
| hard techno | music | 2 | HARD RAVE & PSYTRANCE (cross-club-2026-11-28-hard-rave-psytrance); MCR-T (roxy-2026-11-27-mcr-t) | |
| hardtechno | music | 2 | DIMITRI K x YOSHIKO (epic-2026-12-11-dimitri-k-x-yoshiko); TITI (epic-2027-01-15-titi) | |
| indie pop | music | 2 | F2 LIVE: Metastavy ☆ Tante Elze (fuchs2-2026-12-13-f2-live-metastavy-tante-elze); Mat213 – křest desky a medley největších (archa-plus-2026-11-27-mat213-krest-desky-a-medley-nejvetsich-hitu) | |
| jump-up | music | 2 | DRUMSTATION (cross-club-2026-11-27-drumstation); KANINE (roxy-2026-11-28-kanine) | |
| jungle | music | 2 | X CLUB. (roxy-2026-11-20-x-club); VENJENT (roxy-2026-11-23-venjent) | |
| noise | music | 2 | Cancer House + Kailas (meetfactory-2026-11-25-cancer-house-kailas); WRONG 10 YEARS presents Prison Religion  (fuchs2-2026-11-27-wrong-10-years-presents-prison-religion-wick-zaffer-9) | |
| noise-rock | music | 2 | Žižkovská benefice: C Pentane + Banana S (citarna-unijazz-2026-12-03-zizkovska-benefice-c-pentane-banana-split-srpr-deti-deste); Gurriers (IE) + Support: Enola Gay (bike-jesus-2026-11-21-gurriers-ie-support-enola-gay) | |
| trap | music | 2 | WRONG 10 YEARS presents Prison Religion  (fuchs2-2026-11-27-wrong-10-years-presents-prison-religion-wick-zaffer-9); MCR-T (roxy-2026-11-27-mcr-t) | |
| acid | music | 1 | DRUMSTATION (cross-club-2026-11-27-drumstation) | |
| acid house | music | 1 | GUTT3RCLUB x GLITTER.HIT: Ship Sket ☆ Ke (fuchs2-2026-12-11-gutt3rclub-x-glitter-hit-ship-sket-kewu-domizako) | |
| afro house | music | 1 | SUNDAY RITUALS - AFRO HOUSE (epic-2026-11-22-sunday-rituals-afro-house) | |
| afro-fusion | music | 1 | Omah Lay (forum-karlin-2026-11-18-omah-lay) | |
| afrobeats | music | 1 | Omah Lay (forum-karlin-2026-11-18-omah-lay) | |
| alt-pop | music | 1 | VENJENT (roxy-2026-11-23-venjent) | |
| alt. rock | music | 1 | Žižkovská benefice: C Pentane + Banana S (citarna-unijazz-2026-12-03-zizkovska-benefice-c-pentane-banana-split-srpr-deti-deste) | |
| alternative-rock | music | 1 | .THEMAYREVOLUTION - PRAHA KŘEST 1 /live (bike-jesus-2026-11-19-themayrevolution-praha-krest-1-live) | |
| ballroom | music | 1 | GUTT3RCLUB x GLITTER.HIT: Ship Sket ☆ Ke (fuchs2-2026-12-11-gutt3rclub-x-glitter-hit-ship-sket-kewu-domizako) | |
| bigbeat | music | 1 | Žižkovská benefice: C Pentane + Banana S (citarna-unijazz-2026-12-03-zizkovska-benefice-c-pentane-banana-split-srpr-deti-deste) | |
| booty bass | music | 1 | GUTT3RCLUB x GLITTER.HIT: Ship Sket ☆ Ke (fuchs2-2026-12-11-gutt3rclub-x-glitter-hit-ship-sket-kewu-domizako) | |
| booty house | music | 1 | MCR-T (roxy-2026-11-27-mcr-t) | |
| bounce | music | 1 | ACT OF THE BOUNCE (bike-jesus-2026-11-21-act-of-the-bounce) | |
| breaks | music | 1 | DRUMSTATION (cross-club-2026-11-27-drumstation) | |
| campy konverzační komedie | stage | 1 | Adina Šulcová: 50 démonů čtverečních (archa-plus-2026-11-24-adina-sulcova-50-demonu-ctverecnich) | |
| classical | music | 1 | Resident Evil – Symphony of Legacy (forum-karlin-2026-12-01-resident-evil-symphony-of-legacy) | |
| contemporary dance | stage | 1 | LẨU–VYPRÁVĚNÍ U JÍDLA (palac-akropolis-2026-11-30-lauvypraveni-u-jidla) | |
| dance theatre | stage | 1 | DEKKADANCERS: STUDIO 54 (archa-plus-2026-12-19-dekkadancers-studio-54) | |
| dance-pop | music | 1 | ADÉLA (forum-karlin-2027-01-11-adela) | |
| dance-punk | music | 1 | Gurriers (IE) + Support: Enola Gay (bike-jesus-2026-11-21-gurriers-ie-support-enola-gay) | |
| dancehall | music | 1 | DUB CLUB LIVE present Omega Nebula ☆ War (fuchs2-2026-12-11-dub-club-live-present-omega-nebula-warrior-queen-peeni-walli) | |
| deconstructed club | music | 1 | GUTT3RCLUB x GLITTER.HIT: Ship Sket ☆ Ke (fuchs2-2026-12-11-gutt3rclub-x-glitter-hit-ship-sket-kewu-domizako) | |
| digicore | music | 1 | Live Nation: Tiffany Day (meetfactory-2026-11-27-live-nation-tiffany-day) | |
| dixieland | music | 1 | VLTAVA - STO LET S VÁMI (palac-akropolis-2026-11-20-vltava-sto-let-s-vami) | |
| doom | music | 1 | Freshwater Dogs + Table Mountain String  (citarna-unijazz-2026-11-24-freshwater-dogs-table-mountain-string-band) | |
| doom metal | music | 1 | Chelsea Wolfe - THE DARK World Tour (archa-plus-2026-12-05-chelsea-wolfe-the-dark-world-tour) | |
| drill | music | 1 | GUTT3RCLUB x GLITTER.HIT: Ship Sket ☆ Ke (fuchs2-2026-12-11-gutt3rclub-x-glitter-hit-ship-sket-kewu-domizako) | |
| drone | music | 1 | Cancer House + Kailas (meetfactory-2026-11-25-cancer-house-kailas) | |
| dub | music | 1 | DUB CLUB LIVE present Omega Nebula ☆ War (fuchs2-2026-12-11-dub-club-live-present-omega-nebula-warrior-queen-peeni-walli) | |
| educational narrative adventure game | music | 1 | Uvedení hry – Andre miri cipa / V mojí k (archa-plus-2026-11-18-uvedeni-hry-andre-miri-cipa-v-moji-kuzi) | |
| emo | music | 1 | F2 LIVE: Dušan Vlk / Asthmaboy Again (fuchs2-2026-12-03-f2-live-dusan-vlk-asthmaboy-again) | |
| emo-rap | music | 1 | F2 LIVE: Dušan Vlk / Asthmaboy Again (fuchs2-2026-12-03-f2-live-dusan-vlk-asthmaboy-again) | |
| flamenco | music | 1 | Good Times Only: křest desky + Blue Uand (meetfactory-2026-11-21-good-times-only-krest-desky-blue-uandi) | |
| folk-rock | music | 1 | MIREK KEMEL S KAPELOU (palac-akropolis-2026-12-16-mirek-kemel-s-kapelou) | |
| garage-rock | music | 1 | .THEMAYREVOLUTION - PRAHA KŘEST 1 /live (bike-jesus-2026-11-19-themayrevolution-praha-krest-1-live) | |
| ghetto-tech | music | 1 | MCR-T (roxy-2026-11-27-mcr-t) | |
| glitch pop | music | 1 | Live Nation: Tiffany Day (meetfactory-2026-11-27-live-nation-tiffany-day) | |
| gothic rock | music | 1 | Chelsea Wolfe - THE DARK World Tour (archa-plus-2026-12-05-chelsea-wolfe-the-dark-world-tour) | |
| grunge | music | 1 | Gurriers (IE) + Support: Enola Gay (bike-jesus-2026-11-21-gurriers-ie-support-enola-gay) | |
| hardcore rave | music | 1 | GUTT3RCLUB x GLITTER.HIT: Ship Sket ☆ Ke (fuchs2-2026-12-11-gutt3rclub-x-glitter-hit-ship-sket-kewu-domizako) | |
| idm | music | 1 | Amphibian Quadrophonic Soundsystem (archa-plus-2026-11-20-amphibian-quadrophonic-soundsystem) | |
| jazz | music | 1 | Jazzmánie Vladimíra Kouřila #274 (citarna-unijazz-2026-12-01-jazzmanie-vladimira-kourila-274) | |
| jersey club | music | 1 | GUTT3RCLUB x GLITTER.HIT: Ship Sket ☆ Ke (fuchs2-2026-12-11-gutt3rclub-x-glitter-hit-ship-sket-kewu-domizako) | |
| miami bass | music | 1 | MCR-T (roxy-2026-11-27-mcr-t) | |
| musical | stage | 1 | SPITFIRE COMPANY & PAST ►CANCEL (palac-akropolis-2026-11-17-spitfire-company-past-cancel) | |
| neo-soul | music | 1 | F2 LIVE: Metastavy ☆ Tante Elze (fuchs2-2026-12-13-f2-live-metastavy-tante-elze) | |
| neurofunk | music | 1 | VENJENT (roxy-2026-11-23-venjent) | |
| noise rock | music | 1 | Žižkovská benefice: C Pentane + Banana S (citarna-unijazz-2026-12-03-zizkovska-benefice-c-pentane-banana-split-srpr-deti-deste) | |
| noise-punk | music | 1 | Gurriers (IE) + Support: Enola Gay (bike-jesus-2026-11-21-gurriers-ie-support-enola-gay) | |
| old-time | music | 1 | Freshwater Dogs + Table Mountain String  (citarna-unijazz-2026-11-24-freshwater-dogs-table-mountain-string-band) | |
| orchestral | music | 1 | Resident Evil – Symphony of Legacy (forum-karlin-2026-12-01-resident-evil-symphony-of-legacy) | |
| parodie na horory a sitcomy | stage | 1 | Adina Šulcová: 50 démonů čtverečních (archa-plus-2026-11-24-adina-sulcova-50-demonu-ctverecnich) | |
| ploužák | music | 1 | FRANTIŠEK SKÁLA & TŘASKAVÁ SMĚS ►KŘEST N (palac-akropolis-2026-12-04-frantisek-skala-traskava-smes-krest-noveho-alba-zklamal) | |
| pop-punk | music | 1 | NERVY (roxy-2026-11-29-nervy) | |
| post-hardcore | music | 1 | Cancer House + Kailas (meetfactory-2026-11-25-cancer-house-kailas) | |
| post-rock | music | 1 | Cancer House + Kailas (meetfactory-2026-11-25-cancer-house-kailas) | |
| postpunkový dokument | stage | 1 | TANTEHORSE ►S(t)IGMA (palac-akropolis-2026-12-10-tantehorse-s-t-igma) | |
| ragga | music | 1 | DUB CLUB LIVE present Omega Nebula ☆ War (fuchs2-2026-12-11-dub-club-live-present-omega-nebula-warrior-queen-peeni-walli) | |
| raggajungle | music | 1 | DUB CLUB LIVE present Omega Nebula ☆ War (fuchs2-2026-12-11-dub-club-live-present-omega-nebula-warrior-queen-peeni-walli) | |
| road movie | film | 1 | Transgender Awareness Week: Lola (kasarna-karlin-2026-11-18-transgender-awareness-week-lola) | |
| rock'n'roll | music | 1 | VLTAVA - STO LET S VÁMI (palac-akropolis-2026-11-20-vltava-sto-let-s-vami) | |
| rub-a-dub | music | 1 | DUB CLUB LIVE present Omega Nebula ☆ War (fuchs2-2026-12-11-dub-club-live-present-omega-nebula-warrior-queen-peeni-walli) | |
| sludge | music | 1 | Cancer House + Kailas (meetfactory-2026-11-25-cancer-house-kailas) | |
| sludge metal | music | 1 | PUSHTEEK presents High on Fire ☆ Cancer  (fuchs2-2026-12-01-pushteek-presents-high-on-fire-cancer-void-thulsa) | |
| sound art | music | 1 | LẨU–VYPRÁVĚNÍ U JÍDLA (palac-akropolis-2026-11-30-lauvypraveni-u-jidla) | |
| soundtrack | music | 1 | Resident Evil – Symphony of Legacy (forum-karlin-2026-12-01-resident-evil-symphony-of-legacy) | |
| současný tanec | stage | 1 | DEKKADANCERS: STUDIO 54 (archa-plus-2026-12-19-dekkadancers-studio-54) | |
| stoner metal | music | 1 | PUSHTEEK presents High on Fire ☆ Cancer  (fuchs2-2026-12-01-pushteek-presents-high-on-fire-cancer-void-thulsa) | |
| swing | music | 1 | VLTAVA - STO LET S VÁMI (palac-akropolis-2026-11-20-vltava-sto-let-s-vami) | |
| synthwave | music | 1 | F2 LIVE: Metastavy ☆ Tante Elze (fuchs2-2026-12-13-f2-live-metastavy-tante-elze) | |
| tekno | music | 1 | HARD RAVE & PSYTRANCE (cross-club-2026-11-28-hard-rave-psytrance) | |
| trampská píseň | music | 1 | VLTAVA - STO LET S VÁMI (palac-akropolis-2026-11-20-vltava-sto-let-s-vami) | |
| twist | music | 1 | VLTAVA - STO LET S VÁMI (palac-akropolis-2026-11-20-vltava-sto-let-s-vami) | |
| uptempo | music | 1 | DIMITRI K x YOSHIKO (epic-2026-12-11-dimitri-k-x-yoshiko) | |
| valčík | music | 1 | FRANTIŠEK SKÁLA & TŘASKAVÁ SMĚS ►KŘEST N (palac-akropolis-2026-12-04-frantisek-skala-traskava-smes-krest-noveho-alba-zklamal) | |
| witch house | music | 1 | WRONG 10 YEARS presents Prison Religion  (fuchs2-2026-11-27-wrong-10-years-presents-prison-religion-wick-zaffer-9) | |
| šanson | music | 1 | FRANTIŠEK SKÁLA & TŘASKAVÁ SMĚS ►KŘEST N (palac-akropolis-2026-12-04-frantisek-skala-traskava-smes-krest-noveho-alba-zklamal) | |

## 4. Použité žánre (počet akcií v `events.json`)

| žáner | akcií |
|---|---|
| rock | 51 |
| hip-hop | 35 |
| house | 35 |
| pop | 35 |
| techno | 34 |
| indie | 32 |
| electronic | 30 |
| folk | 21 |
| drum-and-bass | 20 |
| edm | 18 |
| metal | 16 |
| jazz | 16 |
| experimental | 13 |
| punk | 9 |
| post-punk | 8 |
| rnb | 8 |
| trance | 6 |
| blues | 6 |
| bass-music | 5 |
| hardcore | 5 |
| world | 5 |
| disco | 4 |
| shoegaze | 3 |
| dubstep | 3 |
| tech-house | 3 |
| electro | 3 |
| metalcore | 3 |
| latin | 3 |
| funk | 3 |
| industrial | 3 |
| electro-swing | 2 |
| ambient | 2 |
| reggae | 2 |
| darkwave | 2 |
| uk-bass | 2 |
| dream-pop | 2 |
| uk-garage | 2 |
| hardstyle | 2 |
| slowcore | 1 |
| ebm | 1 |
| death-metal | 1 |
| physical-theatre | 1 |
| oldies | 1 |
| rave | 1 |
