# Classification review — 2026-11-04

## Zhrnutie

### Počty podľa formátu (task 015, layer 1 only — AI layer skipped, ANTHROPIC_API_KEY not set)

| Formát | Počet |
|--------|-------|
| live | 47 |
| dj | 12 |
| music (nerozlíšené — pôjde na AI) | 142 |
| theatre | 56 |
| talk | 4 |
| dance | 9 |
| workshop | 4 |
| opening | 2 |
| other | 2 |
| quiz | 1 |
| *no format* (nerozlíšené — pôjde na AI) | 20 |
| **Spolu** | **299** |

### Porovnanie s task 013

| Metrika | Task 013 | Task 015 |
|---------|----------|----------|
| Celkovo udalostí | 299 | 298 |
| source | ~78 | 78 |
| keyword | ~59 | 58 |
| venue (odstraneé) | 159 | — |
| null/AI | ~3 | 162 |
| Nové formáty (dance/talk/comedy/workshop) | 0 | 17 |

> V task 013 bola venue rule (VENUE_DEFAULTS) zodpovedná za 159/299 (53 %) klasifikácií s nízkou presnosťou. V task 015 bola odstránená — 162 udalostí pôjde na AI layer 2.

### Udalosti so zmeneným formátom (task 013 → task 015)

Venue rule bola odstránená, takže všetky udalosti s `method=venue` v task 013 majú teraz `method=null` alebo `music fallback`. Konkrétne zmeny budú viditeľné po prvom AI behu (keď `ANTHROPIC_API_KEY` bude nastavený v GitHub Actions).

---

## Všetky udalosti (zoradené podľa podniku)

| Venue | Dátum | Názov | Formáty | Žánre | Metóda | Istota |
|-------|-------|-------|---------|-------|--------|--------|
| archa-plus | 2026-11-04 | Adina Šulcová: 50 démonů čtverečních | theatre | — | source | 1.00 |
| archa-plus | 2026-11-06 | KARAOKE+ | — | — | — | — |
| archa-plus | 2026-11-07 | Hatebreed + Life of Agony + Hopes + Status Praesent | music | — | — | — |
| archa-plus | 2026-11-08 | Spectaculare_14 - Floex Ensemble (křest) + Juha Mäki-Patola | live | — | keyword | 0.90 |
| archa-plus | 2026-11-09 | Debata pro loutky: JSTE TEPLÍ? | talk | — | source | 1.00 |
| archa-plus | 2026-11-10 | A+U: GarageBand w/ Josef K. | dj | — | keyword | 0.90 |
| archa-plus | 2026-11-10 | Debata pro loutky: JSTE QUEER? | talk | — | source | 1.00 |
| archa-plus | 2026-11-11 | LEAP | music | — | — | — |
| archa-plus | 2026-11-12 | God Save the Drama Queen: Král*ovna | theatre | — | source | 1.00 |
| archa-plus | 2026-11-12 | Jak se sebou nenechat zamést v nájmu | talk | — | source | 1.00 |
| archa-plus | 2026-11-13 | Festival Alternativa: Den 1. | music | — | — | — |
| archa-plus | 2026-11-13 | God Save the Drama Queen: Král*ovna | theatre | — | source | 1.00 |
| archa-plus | 2026-11-14 | Festival Alternativa: Den 2. | music | — | — | — |
| archa-plus | 2026-11-15 | Health + VOWWS | music | — | — | — |
| archa-plus | 2026-11-16 | České znění: Sex ve městě | — | — | — | — |
| archa-plus | 2026-11-18 | Burkicom: Slunce | dance | — | source | 1.00 |
| archa-plus | 2026-11-18 | Uvedení hry – Andre miri cipa / V mojí kůži | — | — | — | — |
| archa-plus | 2026-11-19 | José González | music | — | — | — |
| archa-plus | 2026-11-20 | Amphibian Quadrophonic Soundsystem | music | — | — | — |
| archa-plus | 2026-11-21 | Arlo Parks | music | — | — | — |
| archa-plus | 2026-11-23 | Činoherní studio Ústí nad Labem: Svatá Johana z jatek | theatre | — | source | 1.00 |
| archa-plus | 2026-11-24 | Adina Šulcová: 50 démonů čtverečních | theatre | — | source | 1.00 |
| archa-plus | 2026-11-25 | Adina Šulcová: 50 démonů čtverečních | theatre | — | source | 1.00 |
| archa-plus | 2026-11-26 | Střed zájmu: Síla kolektivu | talk | — | source | 1.00 |
| archa-plus | 2026-11-27 | Billy Barman & Dievčatá zo SĽUK-u - Vianočný koncert | music | — | — | — |
| archa-plus | 2026-11-27 | Mat213 – křest desky a medley největších hitů | live | — | keyword | 0.90 |
| archa-plus | 2026-11-29 | A+U: Základy živého zvučení (Mr. Wombat) | workshop | — | source | 1.00 |
| archa-plus | 2026-11-29 | Popkulturní kvíz #2 | quiz | — | source | 1.00 |
| archa-plus | 2026-11-30 | Going Nowhere | opening | — | source | 1.00 |
| archa-plus | 2026-11-30 | ROAST slaví narozky | — | — | — | — |
| archa-plus | 2026-12-01 | ARCHA+ / Divadlo NIE: JEDEN A JEDEN A JEDEN | theatre | — | source | 1.00 |
| archa-plus | 2026-12-01 | Divadlo NIE / ARCHA+: JEDEN A JEDEN A JEDEN | theatre | — | source | 1.00 |
| archa-plus | 2026-12-01 | Ibra Ibrahimovič: Střepy severních Čech | opening | — | source | 1.00 |
| archa-plus | 2026-12-03 | Baby Lasagna | music | — | — | — |
| archa-plus | 2026-12-04 | Ventolin + FVLCRVM - Ventofu tour | live | — | keyword | 0.90 |
| archa-plus | 2026-12-05 | Chelsea Wolfe - THE DARK World Tour | live | — | keyword | 0.90 |
| archa-plus | 2026-12-06 | A+U: Adam Dragun – Montáž jako lifestyle | workshop | — | source | 1.00 |
| archa-plus | 2026-12-09 | Pocta Radimu Hladíkovi - MÁ HRA | music | — | — | — |
| archa-plus | 2026-12-12 | DEKKADANCERS: STUDIO 54 | dance | — | source | 1.00 |
| archa-plus | 2026-12-13 | DEKKADANCERS: STUDIO 54 | dance | — | source | 1.00 |
| archa-plus | 2026-12-14 | DEKKADANCERS: STUDIO 54 | dance | — | source | 1.00 |
| archa-plus | 2026-12-15 | DEKKADANCERS: STUDIO 54 | dance | — | source | 1.00 |
| archa-plus | 2026-12-16 | DEKKADANCERS: STUDIO 54 | dance | — | source | 1.00 |
| archa-plus | 2026-12-17 | Orin Rodriguez, Kirikou Gueye: Titty Killer | theatre | — | source | 1.00 |
| archa-plus | 2026-12-18 | DEKKADANCERS: STUDIO 54 | dance | — | source | 1.00 |
| archa-plus | 2026-12-19 | DEKKADANCERS: STUDIO 54 | dance | — | source | 1.00 |
| archa-plus | 2026-12-20 | DEKKADANCERS: STUDIO 54 | dance | — | source | 1.00 |
| archa-plus | 2027-01-19 | Jana Kirschner - Večer Trojkráľový | music | — | — | — |
| archa-plus | 2027-01-26 | Jordi Casanovas: Smečka | theatre | — | source | 1.00 |
| archa-plus | 2027-01-27 | A+U: Set and Play w/ Ursula Sereghy | dj | — | keyword | 0.90 |
| archa-plus | 2027-02-08 | Night Lovell | dj | — | keyword | 0.90 |
| archa-plus | 2027-02-09 | A+U: Základy DJingu s litterbinem | workshop | — | source | 1.00 |
| archa-plus | 2027-02-16 | Adina Šulcová: 50 démonů čtverečních | theatre | — | source | 1.00 |
| archa-plus | 2027-02-18 | Cameron Whitcomb | music | — | — | — |
| archa-plus | 2027-02-19 | Giant Rooks | music | — | — | — |
| archa-plus | 2027-02-25 | Orin Rodriguez, Kirikou Gueye: Titty Killer | theatre | — | source | 1.00 |
| archa-plus | 2027-02-26 | God Save the Drama Queen: Král*ovna | theatre | — | source | 1.00 |
| archa-plus | 2027-02-28 | Adam Dragun: ALEX | theatre | — | source | 1.00 |
| archa-plus | 2027-03-05 | oskar med k | music | — | — | — |
| archa-plus | 2027-03-11 | Saxon | music | — | — | — |
| archa-plus | 2027-03-13 | Cult of Luna + BRUIT ≤ + Youth Code | — | — | — | — |
| archa-plus | 2027-03-17 | Warhaus | music | — | — | — |
| archa-plus | 2027-04-21 | A+U: Základy DJingu s litterbinem (EN) | workshop | — | source | 1.00 |
| bike-jesus | 2026-11-06 | LYRA with FUNK D'VOID [ Cocoon / Bedrock ] | music | — | — | — |
| bike-jesus | 2026-11-07 | EARLY SHOW: Westside Cowboy (UK) /live | live | — | keyword | 0.90 |
| bike-jesus | 2026-11-07 | Rave Generation | dj | — | keyword | 0.90 |
| bike-jesus | 2026-11-10 | deary | music | — | — | — |
| bike-jesus | 2026-11-11 | Dudlíkfest 2026 | music | — | — | — |
| bike-jesus | 2026-11-12 | REVO: August Ocean & Idea: Medzi mnou a zajtrajškom album release party /live | live | — | keyword | 0.90 |
| bike-jesus | 2026-11-13 | Lick w/ Bobok & Teoman, Gökdeniz, Fembot, Keo Jesse & Dash | dj | — | keyword | 0.90 |
| bike-jesus | 2026-11-14 | REVO: Takto: Alejandro Molinari, Tatomed, Gatita Tribalera,     AVDH, Djames, Venera | music | — | — | — |
| bike-jesus | 2026-11-15 | Desire & Johnny Jewel + support: Mothermary | live | — | keyword | 0.90 |
| bike-jesus | 2026-11-16 | Bashment Bass Foundation Anniversary Dance featuring NOMADIX (UK) | music | — | — | — |
| bike-jesus | 2026-11-18 | ATHENA CHLEBOVÁ - KŘEST PRAHA + GAMBRZ REPRZ + VENTOLIN DJ SET /live | live, dj | — | keyword | 0.80 |
| bike-jesus | 2026-11-19 | .THEMAYREVOLUTION - PRAHA KŘEST 1 /live | live | — | keyword | 0.90 |
| bike-jesus | 2026-11-20 | CREDIT 00 (live), MIDIRAMA & RAPHAEL KOSMOS | live | — | keyword | 0.90 |
| bike-jesus | 2026-11-20 | EARLY SHOW: Ley Lofaj /live | live | — | keyword | 0.90 |
| bike-jesus | 2026-11-20 | REVO: Z Gumy Do Gumy | music | — | — | — |
| bike-jesus | 2026-11-21 | ACT OF THE BOUNCE | music | — | — | — |
| bike-jesus | 2026-11-21 | Gurriers (IE) + Support: Enola Gay | live | — | keyword | 0.90 |
| bike-jesus | 2026-11-21 | REVO: Spirála | music | — | — | — |
| bike-jesus | 2026-11-26 | FEVERDREAM | music | — | — | — |
| bike-jesus | 2026-11-27 | REVO: SOUR ROOM | music | — | — | — |
| bike-jesus | 2026-11-27 | WELLWET Residents + Secret Guest (DE) | dj | — | keyword | 0.90 |
| bike-jesus | 2026-11-28 | REVO: Just InCase: Blackloud, KAWA, Topal | music | — | — | — |
| bike-jesus | 2026-11-28 | The Scratch (+ DUG) /live | live | — | keyword | 0.90 |
| bike-jesus | 2026-11-29 | Rikas | music | — | — | — |
| bike-jesus | 2026-12-01 | Novulent + Softcult | music | — | — | — |
| bike-jesus | 2026-12-03 | SEBE + Pokoj25 | music | — | — | — |
| bike-jesus | 2026-12-04 | Tonic Walter | music | — | — | — |
| bike-jesus | 2027-01-30 | Giles Corey /live | live | — | keyword | 0.90 |
| bike-jesus | 2027-02-04 | Petrofski + support: Lowmoe | live | — | keyword | 0.90 |
| bike-jesus | 2027-02-18 | Mothermary /live | live | — | keyword | 0.90 |
| bike-jesus | 2027-03-13 | Iluka | music | — | — | — |
| bike-jesus | 2027-04-08 | Festival Spectaculare: Janus Rasmussen live | live | — | keyword | 0.90 |
| bike-jesus | 2027-04-11 | GHØSTKID (DE) : Follow The White Rabbit tour + Dropout Kings, Stain the Canvas | live | — | keyword | 0.90 |
| citarna-unijazz | 2026-11-04 | Unijazz Open | — | — | — | — |
| citarna-unijazz | 2026-11-05 | BBP – podzemní orchestr + Polanský&Langman | — | — | — | — |
| citarna-unijazz | 2026-11-06 | Drážďanská cena za poezii 2026 - Pražský večer | — | — | — | — |
| citarna-unijazz | 2026-11-09 | Svítit cestou - Motivační stand-up Světlany Nálepkové | — | — | — | — |
| citarna-unijazz | 2026-11-10 | Argo: Michal Vrba – Hlušický čtverec | — | — | — | — |
| citarna-unijazz | 2026-11-11 | Vidět hutnou hudbu | — | — | — | — |
| citarna-unijazz | 2026-11-12 | HLAVEC: Nohaband + Původní Bureš | — | — | — | — |
| citarna-unijazz | 2026-11-13 | Unijazz Cup 2026 #11 | — | — | — | — |
| citarna-unijazz | 2026-11-16 | Moře dní: křest vinylu, support: Dvořák | live | — | keyword | 0.90 |
| citarna-unijazz | 2026-11-18 | Text-appeal vol. 28 | — | — | — | — |
| citarna-unijazz | 2026-11-19 | JAKUB EDEN - KŘEST DEBUTOVÉHO ALBA | live | — | keyword | 0.90 |
| citarna-unijazz | 2026-11-20 | PSYTRANCE UNITED | — | — | — | — |
| citarna-unijazz | 2026-11-24 | Freshwater Dogs + Table Mountain String Band | — | — | — | — |
| citarna-unijazz | 2026-11-26 | Syrový tóny + Katka Šarközi | — | — | — | — |
| citarna-unijazz | 2026-11-30 | František Drábek - Je tohle divadlo? | — | — | — | — |
| cross-club | 2026-11-04 | BIOCROSS | music | — | — | — |
| cross-club | 2026-11-05 | UP TONE 19:00 w/ STURLE DAGSLAND & TECHNO AFTERPARTY | dj | — | keyword | 0.90 |
| cross-club | 2026-11-06 | DOUBLE TROUBLE w/ MAGNETUDE (UK) | dj | — | keyword | 0.90 |
| cross-club | 2026-11-07 | TŘI HLASY | music | — | — | — |
| cross-club | 2026-11-08 | SUNDEJ SE SUNDAY | music | — | — | — |
| cross-club | 2026-11-09 | LOS TEKKENOS | music | — | — | — |
| cross-club | 2026-11-10 | TECHNO NIGHT | dj | — | keyword | 0.90 |
| cross-club | 2026-11-11 | TECHNO  HOUSE | music | — | — | — |
| cross-club | 2026-11-12 | POHŘEBNÍ KAPELA & METAL NIGHT | dj | — | keyword | 0.90 |
| cross-club | 2026-11-13 | ARRAKIS FESTIVAL | music | — | — | — |
| cross-club | 2026-11-14 | ARRAKIS FESTIVAL | music | — | — | — |
| cross-club | 2026-11-15 | SUNDEJ SE SUNDAY | music | — | — | — |
| cross-club | 2026-11-16 | FESTIVAL NADPRAHOU PULMESIC & TECHNO STAGE & PSEUDO 4 | music | — | — | — |
| cross-club | 2026-11-17 | TECHNO STAGE | music | — | — | — |
| cross-club | 2026-11-18 | KŘIŽOVATKA & KAVÁRNA KŘEST BOLDRIKOVO KNIHY | live | — | keyword | 0.90 |
| forum-karlin | 2026-11-06 | Shinedown | music | — | — | — |
| forum-karlin | 2026-11-08 | RAMMSTEIN SYMPHONIC EXPERIENCE | music | — | — | — |
| forum-karlin | 2026-11-13 | Michal Horák | music | — | — | — |
| forum-karlin | 2026-11-14 | SOČR & Monkey Business | music | — | — | — |
| forum-karlin | 2026-11-15 | EsDeeKid | music | — | — | — |
| forum-karlin | 2026-11-16 | The Pretty Reckless | music | — | — | — |
| forum-karlin | 2026-11-18 | Omah Lay | music | — | — | — |
| forum-karlin | 2026-11-21 | STAHLZEIT | music | — | — | — |
| forum-karlin | 2026-11-29 | SLAVA VAKARCHUK IN PRAGUE | music | — | — | — |
| forum-karlin | 2026-12-01 | Resident Evil – Symphony of Legacy | music | — | — | — |
| forum-karlin | 2026-12-04 | MIKOLAS – FORUM KARLÍN | music | — | — | — |
| forum-karlin | 2026-12-05 | Kodaline | music | — | — | — |
| forum-karlin | 2026-12-06 | SANDRA | music | — | — | — |
| forum-karlin | 2026-12-09 | Olympic | music | — | — | — |
| forum-karlin | 2026-12-10 | Stronger Together | music | — | — | — |
| forum-karlin | 2026-12-16 | Fantastic Future Summit 2026 | music | — | — | — |
| forum-karlin | 2026-12-17 | Dalibor Janda | music | — | — | — |
| forum-karlin | 2026-12-21 | Vánoční koncert Michala Prokopa & Framus Five | music | — | — | — |
| forum-karlin | 2027-01-11 | ADÉLA | music | — | — | — |
| forum-karlin | 2027-01-30 | Original ENIGMA Voices Symphonic | music | — | — | — |
| forum-karlin | 2027-02-08 | Skryptonite | music | — | — | — |
| forum-karlin | 2027-02-21 | THE UNOFFICIAL ERAS TOUR (PRAGUE'S VERSION) TAYLOR SWIFT TRIBUTE BY KATY ELLIS AND TAYLORMANIA (UK) | live | — | keyword | 0.90 |
| forum-karlin | 2027-02-27 | Tata Bojs | music | — | — | — |
| forum-karlin | 2027-03-05 | SUZI QUATRO | music | — | — | — |
| forum-karlin | 2027-03-11 | Palaye Royale 2027 | music | — | — | — |
| forum-karlin | 2027-03-17 | BONOBO | music | — | — | — |
| forum-karlin | 2027-03-20 | KALEO | music | — | — | — |
| forum-karlin | 2027-04-17 | 2hollis | music | — | — | — |
| forum-karlin | 2027-04-21 | MINISTRY, DIE KRUPPS | music | — | — | — |
| fuchs2 | 2026-11-06 | TECHNO ALLIANCE: Fjaak ☆ Nina Farrina ☆ Midirama | music | — | — | — |
| fuchs2 | 2026-11-12 | SALO: Lovačka Srca Takeover | music | — | — | — |
| fuchs2 | 2026-11-13 | TECHNO ALLIANCE:  Kike Pravda ☆ Marie Pravda ☆ DDK ☆ Miss Univers ☆ TerminusTechnikus | music | — | — | — |
| fuchs2 | 2026-11-14 | LIVE NATION presents STVW | live | — | keyword | 0.90 |
| fuchs2 | 2026-11-14 | X-RAY MEETS SWITCH: Mez & Grandmixxer | music | — | — | — |
| fuchs2 | 2026-11-16 | ALL NIGHT LONG: SJ Yellow | dj | — | keyword | 0.90 |
| fuchs2 | 2026-11-27 | RFP CONCERTS present Chinchilla ☆ Jolina Louise | music | — | — | — |
| fuchs2 | 2026-11-27 | WRONG 10 YEARS presents Prison Religion ☆ Wick ☆ Zaffer 9 | music | — | — | — |
| fuchs2 | 2026-12-01 | PUSHTEEK presents High on Fire ☆ Cancer Void ☆ Thulsa | music | — | — | — |
| fuchs2 | 2026-12-03 | F2 LIVE: Dušan Vlk / Asthmaboy Again | live | — | keyword | 0.90 |
| fuchs2 | 2026-12-05 | ZLOMENÁ SCÉNA x OVERVIEW MUSIC present Calyx Skantia Kyrist Wingz & Energy | music | — | — | — |
| fuchs2 | 2026-12-16 | BUMBUM SATORI present Dukla ☆ Pebble Seven | music | — | — | — |
| fuchs2 | 2026-12-31 | POSTPONED: deBasement | music | — | — | — |
| fuchs2 | 2027-02-17 | F2 LIVE: Beaks | live | — | keyword | 0.90 |
| fuchs2 | 2027-03-10 | PŘESUNUTO DO MEETFACTORY / RFP CONCERTS present South Arcade | music | — | — | — |
| kasarna-karlin | 2026-12-02 | Bad Karma Boy (album launch) + Island Mint | — | — | — | — |
| kasarna-karlin | 2027-04-12 | Keo (UK) | — | — | — | — |
| meetfactory | 2026-11-05 | Live Nation: Altın Gün + Anatolian Grooves | live | — | keyword | 0.90 |
| meetfactory | 2026-11-07 | Anna Vaverková + Elias O. Graversen | music | — | — | — |
| meetfactory | 2026-11-08 | Sacred Chants: Laboratorium Pieśni | music | — | — | — |
| meetfactory | 2026-11-09 | Samanta Schweblin: Mimo dosah | theatre | — | source | 1.00 |
| meetfactory | 2026-11-12 | Obscure: Archspire + Crown Magnetar + The Zenith Passage + Analepsy | music | — | — | — |
| meetfactory | 2026-11-13 | Selection: Skeler + LXST CXNTURY + Æstral + MRJay | music | — | — | — |
| meetfactory | 2026-11-15 | Obscure: Suffocation + Despised Icon + Carnifex + Gutrectomy | music | — | — | — |
| meetfactory | 2026-11-16 | Oliver Lovrenski: Když nám bylo míň | theatre | — | source | 1.00 |
| meetfactory | 2026-11-17 | Masakr Elsinor: Your Silence Will Not Protect You | theatre | — | source | 1.00 |
| meetfactory | 2026-11-19 | Pragokoncert: Allt + Avralize + Bite Down | music | — | — | — |
| meetfactory | 2026-11-21 | Good Times Only: křest desky + Blue Uandi | live | — | keyword | 0.90 |
| meetfactory | 2026-11-22 | Music Press Production: Arab Strap | music | — | — | — |
| meetfactory | 2026-11-24 | Elfriede Jelinek: Popel | theatre | — | source | 1.00 |
| meetfactory | 2026-11-25 | Cancer House + Kailas | music | — | — | — |
| meetfactory | 2026-11-27 | Live Nation: Tiffany Day | live | — | keyword | 0.90 |
| meetfactory | 2026-11-28 | Gutafest 2026 | music | — | — | — |
| meetfactory | 2026-11-29 | Esther Bol: Infračervené | theatre | — | source | 1.00 |
| meetfactory | 2026-11-30 | Live Nation: Strangelove | live | — | keyword | 0.90 |
| meetfactory | 2026-12-01 | Shaking Hand + Wreckberries | music | — | — | — |
| meetfactory | 2026-12-04 | RFP Concerts: VOILÀ | music | — | — | — |
| meetfactory | 2026-12-06 | Satoshi: Viva Moldova Europe Tour | live | — | keyword | 0.90 |
| meetfactory | 2026-12-09 | Esther Bol: Infračervené | theatre | — | source | 1.00 |
| meetfactory | 2026-12-11 | Selection: Mighty Oaks + June Carousel | music | — | — | — |
| meetfactory | 2026-12-12 | Michel Houellebecq: Serotonin | theatre | — | source | 1.00 |
| meetfactory | 2026-12-14 | Annie Ernaux: Obyčejná žena | theatre | — | source | 1.00 |
| meetfactory | 2026-12-17 | Samanta Schweblin: Mimo dosah | theatre | — | source | 1.00 |
| meetfactory | 2026-12-19 | Oliver Lovrenski: Když nám bylo míň | theatre | — | source | 1.00 |
| meetfactory | 2027-01-13 | Oliver Lovrenski: Když nám bylo míň | theatre | — | source | 1.00 |
| meetfactory | 2027-01-27 | RFP Concerts: Comeback Kid | music | — | — | — |
| meetfactory | 2027-02-07 | Live Nation: Iceage | live | — | keyword | 0.90 |
| meetfactory | 2027-02-12 | Live Nation: almost monday | live | — | keyword | 0.90 |
| meetfactory | 2027-02-16 | Live Nation: Look Mum No Computer | live | — | keyword | 0.90 |
| meetfactory | 2027-02-17 | Live Nation: Amble | live | — | keyword | 0.90 |
| meetfactory | 2027-02-21 | RFP Concerts: Dead Poet Society | music | — | — | — |
| meetfactory | 2027-02-24 | Live Nation: Jacob Banks | live | — | keyword | 0.90 |
| meetfactory | 2027-02-27 | Winter Prague Gothic Treffen | music | — | — | — |
| meetfactory | 2027-02-28 | Protomartyr | music | — | — | — |
| meetfactory | 2027-03-06 | RFP Concerts: H-Blockx | music | — | — | — |
| meetfactory | 2027-03-10 | RFP Concerts: South Arcade | music | — | — | — |
| meetfactory | 2027-03-11 | Live Nation: Haiden Henderson | live | — | keyword | 0.90 |
| meetfactory | 2027-04-02 | Fource: Nieve Ella | music | — | — | — |
| meetfactory | 2027-04-17 | 16 Horsepower | music | — | — | — |
| meetfactory | 2027-05-02 | Obscure: Nevermore + Rivers of Nihil + Urne | music | — | — | — |
| palac-akropolis | 2026-11-04 | KAFKA BAND HRAJE KAFKU | music | — | — | — |
| palac-akropolis | 2026-11-05 | BLACK SEA DAHU/CH+SUPPORT ►SOLONG/CH | live | — | keyword | 0.90 |
| palac-akropolis | 2026-11-06 | FLAMENGO REUNION SESSION - 60 LET | music | — | — | — |
| palac-akropolis | 2026-11-06 | SPITFIRE COMPANY ►ANTIWORDS | theatre | — | source | 1.00 |
| palac-akropolis | 2026-11-07 | FOURCE PRESENTS ► ZIMMER90/DE+SUPPORT ►CECI/DE | live | — | keyword | 0.90 |
| palac-akropolis | 2026-11-08 | NEBOJSY ►KUCHYŇSKÉ PORNO | theatre | — | source | 1.00 |
| palac-akropolis | 2026-11-09 | MAALEM HOUSSAM GUINIA/MA | music | — | — | — |
| palac-akropolis | 2026-11-10 | ZRNÍ (KŘEST) | live | — | keyword | 0.90 |
| palac-akropolis | 2026-11-11 | DELORAINE+UTTERN/IT | music | — | — | — |
| palac-akropolis | 2026-11-12 | MARC RIBOT, CHES SMITH & FARIDA AMADOU/US/BE | music | — | — | — |
| palac-akropolis | 2026-11-13 | REST+AUGUST OCEAN & IDEA+SPECIAL GUESTS | music | — | — | — |
| palac-akropolis | 2026-11-14 | REST+SPECIAL GUESTS | music | — | — | — |
| palac-akropolis | 2026-11-15 | SMAG PA DIG SELVE/DK | music | — | — | — |
| palac-akropolis | 2026-11-18 | SPITFIRE COMPANY & PAST ►CANCEL | theatre | — | source | 1.00 |
| palac-akropolis | 2026-11-19 | SPITFIRE COMPANY & PAST ►CANCEL | theatre | — | source | 1.00 |
| palac-akropolis | 2026-11-19 | VIVERE (KŘEST EP METROPOLE)+JAY AUSTIN | live | — | keyword | 0.90 |
| palac-akropolis | 2026-11-20 | VLTAVA - STO LET S VÁMI | music | — | — | — |
| palac-akropolis | 2026-11-21 | CLAPTRAP/FR | music | — | — | — |
| palac-akropolis | 2026-11-21 | VLTAVA - STO LET S VÁMI | music | — | — | — |
| palac-akropolis | 2026-11-23 | THE MUSIC DIGEST (38) ►THE DEVIL'S TRADE+SKOTAČNÍ KULOMET | other | — | source | 1.00 |
| palac-akropolis | 2026-11-24 | DIVADLO NIE ►WE WILL STILL BE HERE | theatre | — | source | 1.00 |
| palac-akropolis | 2026-11-25 | TERROR/US+BANE/US+START TODAY+PEACE OF MIND/DE | music | — | — | — |
| palac-akropolis | 2026-11-26 | DIVO INSTITUTE+THE WILDERNESS/SK+DALŠÍ | music | — | — | — |
| palac-akropolis | 2026-11-27 | FVCK_KVLT/SK+SMALL TOWN LIFE/SK+DALŠÍ | music | — | — | — |
| palac-akropolis | 2026-11-28 | TROS SKETOS | music | — | — | — |
| palac-akropolis | 2026-11-29 | LẨU–VYPRÁVĚNÍ U JÍDLA | theatre | — | source | 1.00 |
| palac-akropolis | 2026-11-30 | CHRISTIAN MARIEN QUARTET/DE | music | — | — | — |
| palac-akropolis | 2026-11-30 | LẨU–VYPRÁVĚNÍ U JÍDLA | theatre | — | source | 1.00 |
| palac-akropolis | 2026-12-01 | TANTEHORSE ►IRIS | theatre | — | source | 1.00 |
| palac-akropolis | 2026-12-03 | HRDZA/SK– VÁNOČNÍ TURNÉ | music | — | — | — |
| palac-akropolis | 2026-12-04 | FRANTIŠEK SKÁLA & TŘASKAVÁ SMĚS ►KŘEST NOVÉHO ALBA ZKLAMAL | live | — | keyword | 0.90 |
| palac-akropolis | 2026-12-05 | PALLADIAN/ES+CARMICHAEL/UK | music | — | — | — |
| palac-akropolis | 2026-12-06 | OLIN "45 LET V TOM" | music | — | — | — |
| palac-akropolis | 2026-12-07 | SPITFIRE COMPANY & PAST ►CANCEL | theatre | — | source | 1.00 |
| palac-akropolis | 2026-12-08 | AHMEDOVÁ, GEISLEROVÁ, DITTRICHOVÁ ►A BEZ POVÍDÁNÍ | theatre | — | source | 1.00 |
| palac-akropolis | 2026-12-09 | MÁRIO BIHÁRI ►DÍKY ZUZCE NAVAROVÉ | music | — | — | — |
| palac-akropolis | 2026-12-10 | DUNAJ - 40 LET NA SCÉNĚ (1986–2026) | music | — | — | — |
| palac-akropolis | 2026-12-11 | COCOTTE MINUTE+POST-IT+ANTEATER | music | — | — | — |
| palac-akropolis | 2026-12-12 | LETNÍ KAPELA | music | — | — | — |
| palac-akropolis | 2026-12-13 | DIVADLO NIE ►WE WILL STILL BE HERE | theatre | — | source | 1.00 |
| palac-akropolis | 2026-12-14 | DIVADLO NIE ►WE WILL STILL BE HERE | theatre | — | source | 1.00 |
| palac-akropolis | 2026-12-14 | SMUK ZVUK | music | — | — | — |
| palac-akropolis | 2026-12-15 | TANTEHORSE ►LIGHT IN THE DARKNESS (ČECHOVÁ+VIZVÁRY) | theatre | — | source | 1.00 |
| palac-akropolis | 2026-12-15 | THE MUSIC DIGEST (39) | other | — | source | 1.00 |
| palac-akropolis | 2026-12-16 | MIREK KEMEL S KAPELOU | music | — | — | — |
| palac-akropolis | 2026-12-17 | HM ►VÁNOČNÍ KONCERT | music | — | — | — |
| palac-akropolis | 2026-12-17 | HM.. ►KONCERT PRO DĚTI | music | — | — | — |
| palac-akropolis | 2026-12-18 | HENTAI CORPORATION - SHIRIMMING TOUR (KŘEST DESKY) | live | — | keyword | 0.90 |
| palac-akropolis | 2026-12-19 | PASTAVBACKU+SPECIAL GUESTS | music | — | — | — |
| palac-akropolis | 2026-12-20 | LATERNA MAGIKA ►PERPETUUM HAVEL | theatre | — | source | 1.00 |
| palac-akropolis | 2026-12-21 | LATERNA MAGIKA ►PERPETUUM HAVEL | theatre | — | source | 1.00 |
| palac-akropolis | 2026-12-22 | UŽ JSME DOMA – KŘEST REEDICE ALBA NEMILOVANÝ SVĚT | live | — | keyword | 0.90 |
| palac-akropolis | 2027-01-15 | ADONXS - DEATH OF A POP STAR TOUR | live | — | keyword | 0.90 |
| palac-akropolis | 2027-01-21 | DIVADLO NIE ► MŮRA ►TROCHU SVĚTLA JEŠTĚ ZBÝVÁ | theatre | — | source | 1.00 |
| palac-akropolis | 2027-01-22 | DIVADLO NIE ► MŮRA ►TROCHU SVĚTLA JEŠTĚ ZBÝVÁ | theatre | — | source | 1.00 |
| palac-akropolis | 2027-01-23 | SPITFIRE COMPANY & PAST ►CANCEL | theatre | — | source | 1.00 |
| palac-akropolis | 2027-01-25 | SPITFIRE COMPANY ►ANTIWORDS | theatre | — | source | 1.00 |
| palac-akropolis | 2027-01-26 | TANTEHORSE ►S(t)IGMA | theatre | — | source | 1.00 |
| palac-akropolis | 2027-01-30 | MIŘENKA ČECHOVÁ & SPITFIRE COMPANY ►BALETKY | theatre | — | source | 1.00 |
| palac-akropolis | 2027-01-31 | SPITFIRE COMPANY ►DVACETJEDNA | theatre | — | source | 1.00 |
| palac-akropolis | 2027-02-01 | NEBOJSY ►KUCHYŇSKÉ PORNO | theatre | — | source | 1.00 |
| palac-akropolis | 2027-02-04 | INSANIA ► KŘEST ALBA NEO–NOE+HOST ►ZPUTNIK | live | — | keyword | 0.90 |
| palac-akropolis | 2027-02-20 | LẨU–VYPRÁVĚNÍ U JÍDLA | theatre | — | source | 1.00 |
| palac-akropolis | 2027-02-22 | SPITFIRE COMPANY ►KONEC ČLOVĚKA?! | theatre | — | source | 1.00 |
| palac-akropolis | 2027-02-23 | СОЮЗ (SOYUZ)/BY/PL | music | — | — | — |
| palac-akropolis | 2027-02-27 | SPITFIRE COMPANY & PAST ►CANCEL | theatre | — | source | 1.00 |
| palac-akropolis | 2027-02-28 | LATERNA MAGIKA ►PERPETUUM HAVEL | theatre | — | source | 1.00 |
| palac-akropolis | 2027-03-01 | LATERNA MAGIKA ►PERPETUUM HAVEL | theatre | — | source | 1.00 |
| palac-akropolis | 2027-03-02 | NEBOJSY ►KUCHYŇSKÉ PORNO | theatre | — | source | 1.00 |
| palac-akropolis | 2027-03-09 | TANTEHORSE ►RUKOJMÍ (INVISIBLE IV.) | theatre | — | source | 1.00 |
| palac-akropolis | 2027-03-16 | BIGYUKI/JP | music | — | — | — |
| palac-akropolis | 2027-03-19 | THE DEAD DAISIES (FEAT. KELLY HANSEN), THE QUIREBOYS, THE GEMS | music | — | — | — |
| palac-akropolis | 2027-03-27 | EMMA RUTH RUNDLE/US+SUPPORT ►CINDER WELL/US | live | — | keyword | 0.90 |
| palac-akropolis | 2027-04-01 | ART SCHOOL GIRLFRIEND/UK+BLONE (DE) | music | — | — | — |
| palac-akropolis | 2027-04-03 | EDDIE 9V/US | music | — | — | — |
| palac-akropolis | 2027-04-07 | IGOR OROZOVIČ & CO/V ŽENSKÉM OBLEŽENÍ | music | — | — | — |
| palac-akropolis | 2027-04-08 | FIRE! – MATS GUSTAFSSON, JOHAN BERTHLING, MARIÁ PORTUGAL/BR/SE | music | — | — | — |
| palac-akropolis | 2027-04-15 | SOPHIE HUNGER/CH | music | — | — | — |
| palac-akropolis | 2027-04-18 | MATT DARRIAU´S PARADOX TRIO/US | music | — | — | — |
| palac-akropolis | 2027-04-23 | BOUNDARIES/US | music | — | — | — |
| palac-akropolis | 2027-04-24 | FOURCE PRESENTS ►RODRIGO Y GABRIELA/MX- OURHOME TOUR | live | — | keyword | 0.90 |
| palac-akropolis | 2027-04-29 | BOMBINO/NG | music | — | — | — |
| palac-akropolis | 2027-05-03 | DIVADLO NIE ►MUZEUM VZPOMÍNEK | theatre | — | source | 1.00 |
