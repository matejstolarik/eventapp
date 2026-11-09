# Dátový model v1

Hodnoty v JSON príkladoch sú ilustračné (čas, cena a odkazy nie sú overené údaje).
Stav: návrh, väčšina rozhodnutí odsúhlasená 2026-10-29. Zdroj pravdy pre dátové štruktúry. Zmeny najprv navrhnúť, potom upraviť tento súbor.
Posledná aktualizácia: 2026-11-09

## Prehľad

```
venues.json (ručne, v repe)  ->  adaptéry zdrojov  ->  normalizácia  ->  kategorizácia (AI)  ->  deduplikácia + kontroly  ->  events.json (GitHub Pages)  ->  PWA
```

- `venues.json`: zoznam podnikov, ich štítky a zdroje. Píše ho Matej ručne.
- `events.json`: výstup pipeline, jediný súbor, ktorý číta PWA.
- Predchádzajúci `events.json` slúži ako stav (kedy sme akciu prvýkrát videli, či zmizla).
- Všetky štítky sú v angličtine (malé písmená, slová spojené pomlčkou), aj keď UI bude v CZ/SK/EN.

## Podnik (`venues.json`)

```json
{
  "id": "cross-club",
  "name": "Cross Club",
  "city": "Praha",
  "address": "Plynární 1096/23, Praha 7",
  "lat": 50.1082,
  "lng": 14.4432,
  "web": "https://www.crossclub.cz",
  "instagram": "crossclubofficial",
  "facebook": "crossclubprague",
  "type": ["concert-club", "dance-club"],
  "character": ["alternative", "underground"],
  "music": ["drum-and-bass", "dubstep", "techno", "reggae"],
  "size": "small",
  "capacity": 250,
  "features": ["open-air"],
  "ra_url": "https://ra.co/clubs/13354",
  "sources": [
    { "type": "rss", "url": "https://www.crossclub.cz/cs/rss/program/" }
  ],
  "description": "Kultový underground klub a komunitné centrum v industriálnom komplexe. Multifunkčný priestor s barom, záhradou a štúdiami.",
  "description_url": "https://www.crossclub.cz/cs/o-nas/",
  "active": true,
  "notes": null
}
```

- `id`: slug, stabilný, nikdy sa nemení (odkazujú naň obľúbené v PWA).
- `sources`: nesmie byť prázdne. Podnik bez zdroja akcií sa do `venues.json` nepridá.
- `capacity`: nepovinné, len overené číslo.
- `lat`, `lng`: súradnice pre zobrazenie na mape. **Povinné** — podnik bez súradníc sa na mape nezobrazí. Zdroj: OSM Nominatim alebo mapa na webe podniku; vždy overiť adresou. Nový podnik bez súradníc sa do `venues.json` nepridá.
- `description`: krátky popis podniku (2–4 vety, čistý text, bez prekladu, z webu podniku). `null` ak podnik nemá stránku „O nás" / „About" alebo tam popis nie je.
- `description_url`: URL stránky, z ktorej popis pochádza. `null` ak `description` je `null`.
- `ra_url`: nepovinné. Odkaz na profil podniku na Resident Advisor (napr. `https://ra.co/clubs/13354`). Len na zobrazenie v appke, nie na fetchovanie dát.
- Typy zdrojov v1: `rss`, `jsonld`, `html`. Nový typ zdroja = nový samostatný adaptér. (RA sa nepoužíva; `instagram` nie je zdroj dát — pozri `docs/decisions.md`.)
- `sources[].section`: nepovinné. Sekcia webu, z ktorej akcia pochádza (napr. `hudba`, `divadlo` pre MeetFactory). Pomáha pri kategorizácii.
- `html`: venue-specific HTML scraping. Konfigurácia obsahuje `strategy` (napr. `akropolis` pre Palác Akropolis).
- `api`: JSON API rozhranie webu podniku. Len verejne dostupné bez prihlásenia a bez kľúča. Konfigurácia obsahuje `strategy` (napr. `strapi` pre Strapi v5 API). Príklad: `bikejesus.com/api/events`.

### Štítky podniku (nastavuje Matej ručne)

**type** (viac naraz): `concert-club`, `dance-club`, `dj-bar`, `bar`, `cafe`, `culture-center`, `jazz-club`, `concert-hall`, `cinema`

**character** (viac naraz): `underground`, `alternative`, `experimental`, `commercial`, `retro`, `queer`, `student`, `tourist`, `queer-friendly`, `late-night`, `community`, `diy`, `art-space`, `english-friendly`, `cozy`, `hangout`, `family-friendly`

Definície nových štítkov:
- `tourist`: program a prevádzka zamerané najmä na turistov (hity, akcie pre cudzincov, prepredaj vstupeniek turistickými agentúrami).
- `queer-friendly`: doložený queer program alebo spolupráca (queer kolektívy, Prague Pride, queer debaty). Len s doloženým zdrojom (do `notes` podniku), nikdy jediný štítok charakteru; nezistené neznamená „nie je". (`queer` ostáva pre podniky, ktoré sú queer ako také.)
- `late-night`: program bežne do rána.
- `community`: komunitne vedené.
- `diy`: svojpomocné, nezávislé.
- `art-space`: galéria/rezidencie popri hudbe.
- `english-friendly`: program výslovne prístupný v angličtine.
- `cozy`: komorný priestor.
- `hangout`: hlavne posedenie, akcie doplnok.
- `family-friendly`: aj pre deti.

**music**: predvolené žánre podniku, z rovnakého zoznamu ako `genres` akcie.

**size** (jedna hodnota), v UI s rozsahom a príkladmi:
- `small`: do ~300 (Twist, Jazz Republic, Cross Club)
- `medium`: ~300 až 1 000 (Bike Jesus)
- `large`: ~1 000 až 4 000 (Forum Karlín)
- `arena`: 4 000+ (O2 arena)

**features** (viac naraz): `open-air`, `rooftop`, `seasonal`

## Akcia (`events.json`)

```json
{
  "id": "cross-club-2026-10-30-neurocells-hard-rave",
  "venue_id": "cross-club",
  "title": "NEUROCELLS & HARD RAVE",
  "date": "2026-10-30",
  "start_time": "22:00",
  "doors_time": null,
  "end_time": null,
  "formats": ["dj"],
  "genres": ["drum-and-bass", "techno"],
  "character": ["underground"],
  "artists": ["Zombie Cats", "Tanukichi"],
  "price_text": "200 Kč",
  "free": false,
  "ticket_url": "https://ra.co/events/...",
  "image_url": null,
  "description": "Popisný text akcie z webu podniku, čistý text, max 1 000 znakov.",
  "description_source": "source",
  "sources": [
    { "type": "jsonld", "url": "https://meetfactory.cz/cs/program/detail/event", "external_id": null, "section": "hudba" },
    { "type": "rss", "url": "https://www.crossclub.cz/cs/program/8697-neurocells-hard-rave/", "external_id": "8697", "section": null }
  ],
  "classification": { "method": "llm", "confidence": 0.9 },
  "first_seen": "2026-10-20",
  "last_seen": "2026-10-29",
  "status": "scheduled",
  "flags": []
}
```

Polia:
- `id`: vzniká pri prvom zachytení akcie a potom sa nemení, ani keď sa zmení názov. Slug v id sa tvorí z názvu: malé písmená, diakritika sa odstraňuje cez NFKD (nie nahrádza pomlčkou), zostanú len `[a-z0-9]` + pomlčky. „TŘI HLASY" → `tri-hlasy`, „POHŘEBNÍ KAPELA" → `pohrebni-kapela`.
- `date`, `start_time`, `end_time`: **miestny čas Prahy**, uložený ako text (`YYYY-MM-DD`, `HH:MM`). Nie UTC. Dôvod: Cross RSS dáva polnoc ako `23:00 GMT` predchádzajúceho dňa, pri prepočte cez UTC by akcia skočila o deň.
- `start_time`: nepovinné, niektoré zdroje čas nedávajú (Cross RSS). Appka vtedy ukáže len dátum.
- `doors_time`: nepovinné, čas otvorenia dverí (napr. z `doorTime` v JSON-LD MeetFactory). Nikdy sa nepoužíva ako `start_time`.
- `end_time`: nepovinné, ak akcia ide cez polnoc, `end_time` je menší ako `start_time`.
- `formats` (viac naraz): `concert` (živí hudobníci na pódiu — kapela, sólo umelec, orchester, živý elektronický set), `dj`, `party` (klubová noc alebo tematická párty, kombinuje sa s `dj` alebo `concert`; rozhoduje AI vrstva 2 s vysvetlením v prompte), `music` (hudobná akcia, pri ktorej sa nedá rozlíšiť concert vs. dj), `dance` (tanečné predstavenie), `talk` (čítanie, debata, prednáška, krst knihy, diskusia), `comedy` (stand-up), `workshop`, `theatre`, `opening` (vernisáž), `film`, `quiz` (hospodské kvízy), `other`.
- `genres`: z pevného zoznamu (zoznam treba dohodnúť).
- `character`: zdedí sa od podniku, AI ho môže pre konkrétnu akciu prepísať (napr. retro noc v inak alternatívnom klube).
- `price_text`: text tak, ako ho dáva zdroj. Ceny neparsujeme. `free` je odvodené (vstup zdarma áno/nie).
- `sold_out`: `true` len ak zdroj výslovne uvádza vypredané; `false` len ak zdroj výslovne ponúka lístky; inak `null`. Nie je to `status`.
- `room`: nepovinné, sála alebo priestor v rámci podniku tak, ako ho uvádza zdroj (napr. Akropolis: Velký sál, Malá scéna, Jazz Bar); `null` ak zdroj ho neuvádza.
- `ticket_url`: odkaz priamo na predaj lístkov (napr. GoOut, RA, Ticketmaster). Stránka akcie na webe podniku patrí len do `sources[].url`, nie sem. Ak zdroj neposkytuje predajný odkaz, pole je `null`.
- `description`: popis akcie z webu podniku. Čistý text bez HTML, max 1 000 znakov, skrátený na koniec vety (`. `, `! `, `? `), ak je dlhší — `null` ak zdroj popis neposkytuje alebo je prázdny. Adaptéry ho extrahujú priamo (RSS, JSON-LD, API). Detail enrichment (`pipeline/detail_enrich.py`) ho dograbí z detailnej stránky akcie po normalizácii (raz na akciu, cache, limit 40 fetchov na podnik a beh). Venue-špecifický CSS selektor `detail_desc_selector` v source config (venues.json) určuje, z ktorého elementu brať popis. Popis rovnajúci sa názvu akcie sa zahodí.
- `description_source`: `"source"` ak popis pochádza zo zdrojových dát (adaptér alebo detail enrichment), `"ai"` ak ho vygeneruje AI vrstva 2 (neskôr), `null` ak `description` je `null`.
- `classification`: ako sa určili formát a žánre (`source`, `llm`, `llm+web`) a s akou istotou. `null` ak pipeline formát ani žánre neurčila (napr. čistý RSS bez kategorizácie).
- `status`: `scheduled` | `cancelled` (zdroj výslovne uvádza zrušenie) | `postponed` (akcia odložená bez nového dátumu; prefix odstránený z názvu) | `gone` (akcia zmizla zo všetkých zdrojov pred dátumom konania).
- `flags`: problémy, ktoré pipeline zachytila, napr. `date_conflict`, `time_conflict`, `date_suspicious`.

### Dátum bez roka

Niektoré zdroje (napr. Akropolis) uvádzajú dátum bez roka (napr. „4. 11."). Pravidlo: dátum pred včerajškom patrí do budúceho roka. Pravidlo sa uplatňuje len v adaptéroch, ktoré dostávajú dátum bez roka, a je zdokumentované komentárom v adaptéri. Ak by vypočítaný dátum padol za +180 dní od dnes, akcia sa nezaradí (je mimo okno).

### Oznamy, ktoré nie sú akcie

Niektoré zdroje uverejňujú oznamy, ktoré nie sú akciami (napr. „ZAVŘENO" v Čitárni). Tieto záznamy sa vyraďujú priamo v adaptéri daného podniku a logujú na úrovni INFO (`log.info("skipped: %s", title)`). Dôvod filtrovania je zdokumentovaný komentárom v adaptéri.

### Výstavy
Ako akcia sa berie len vernisáž (`opening`), jeden večer. Prebiehajúce výstavy sa nezobrazujú v zozname akcií, len v detaile podniku (neskôr).

### Predvolený pohľad v appke
Akcie s formátom `concert`, `dj` alebo `music`. Ostatné formáty (divadlo, vernisáže, film, kvízy, iné) sa zapínajú filtrom.

## Pevný zoznam žánrov

Platí pre `music` podniku aj `genres` akcie. Malé písmená, pomlčky, anglicky. Zostavený z `music` polí všetkých podnikov v `venues.json` (2026-11-04). Čaká na schválenie Matejom.

```
ambient, bassline, disco, drum-and-bass, dubstep, ebm, electro, electro-swing,
electronic, experimental, folk, funk, hardstyle, hip-hop, house, indie, jazz,
latin, metal, pop, post-punk, punk, r-n-b, reggae, rock, ska, shoegaze,
tech-house, techno, trance, uk-bass, uk-garage, world
```

(33 položiek — pôvodných 27 schválených Matejom 2026-11-04; pridané 2026-11-08: disco, hardstyle, latin, r-n-b, ska, trance)

## Ručné opravy klasifikácie (`data/overrides.json`)

Súbor `data/overrides.json` obsahuje opravy, ktoré majú prednosť pred pravidlami pipeline:

```json
[
  { "id": "cross-club-2026-10-30-neurocells-hard-rave", "formats": ["dj"] },
  { "venue_id": "fuchs2", "title_contains": "F2 LIVE", "formats": ["live"] }
]
```

Typy záznamov:
- `id` + `formats`: oprava konkrétnej akcie podľa ID.
- `venue_id` + `title_contains` + `formats`: oprava všetkých akcií daného podniku, v ktorých sa v názve nachádza zadaný reťazec.

Ak sa oprava aplikuje, `classification.method = "manual"`.

## Kategorizácia (formát, žánre, charakter)

Dve vrstvy:
1. **Deterministická (layer 1):** Priorita: manual override → sekcia zdroja → kľúčové slová v názve → fallback `music`. Bez hádania podľa podniku — ak rule nepomôže, formát ostáva `music` alebo prázdny.
2. **AI (layer 2, Claude Haiku):** Klasifikuje zostatok (prázdne formáty alebo `music`). Vstup: názov, interpreti, sekcia, čas začiatku, podnik a jeho štítky. Výsledok sa cachuje v `events.json` a znova sa volá AI len pri zmene názvu.

`classification = {"method": "source" | "keyword" | "llm" | "manual", "confidence": float}`

## Rozhranie adaptéra

Každý adaptér robí jedno: z konfigurácie zdroja vráti zoznam akcií v jednotnom tvare, ešte bez deduplikácie.

```
fetch(venue, source_config) -> list[RawEvent]
```

`RawEvent` má rovnaké polia ako Akcia, okrem `id`, `first_seen`, `last_seen`, `status`, `flags`, `classification`, a namiesto zoznamu `sources` má jeden zdroj. Adaptér zodpovedá za prevod dátumov na miestny čas Prahy.

Nový typ zdroja = nový adaptér. Zvyšok pipeline sa nemení.

## Deduplikácia

Dve akcie z rôznych zdrojov sú tá istá akcia, ak:
1. majú rovnaký `venue_id` a rovnaký `date`, a
2. podobný názov (normalizovaný: malé písmená, bez diakritiky, bez interpunkcie; zhoda nad prahom), alebo zdieľajú interpreta.

Ak si nie sme istí, akcie nezlučujeme. Duplicita v appke je menšia chyba než zlúčenie dvoch rôznych akcií.

Pri porovnaní s predchádzajúcim `events.json` sa akcia páruje rovnako, aby si zachovala `id` a `first_seen`.

## Zlučovanie polí

Keď viac zdrojov dáva to isté pole, vyhráva zdroj s vyššou prioritou:

`jsonld` > `rss` > `html`

Výnimka: prázdna hodnota nikdy neprepíše vyplnenú.

## Kontroly kvality

- Dva zdroje sa nezhodnú v dátume alebo čase: hodnota podľa priority, akcia dostane príznak `date_conflict` / `time_conflict`.
- Dátum v minulosti pri **novej** akcii (taká sa predtým nevidela): príznak `date_suspicious`. Akcie za hranicou +180 dní sa do výstupu vôbec nedostanú (nie sú to chyby, len mimo okno).
- Podozrenie na prehodený deň a mesiac: ak sa dátum z URL a z JSON-LD líšia práve prehodením dňa a mesiaca → `date_conflict` + `date_suspicious`. Kasárna Karlín zobrazuje dátumy v HTML systematicky ako MM. DD. (nie DD. MM.) — toto sa **neflaguje**, keďže dátum z HTML textu sa na Kasárne vôbec nepoužíva; berieme ho len z URL a z JSON-LD.
- Čas z JSON-LD sa neberie naslepo: Kasárna má chybu v timezone na serveri (čas je posunutý o 5–6 h). Správny čas sa parsuje z textu stránky.
- Adaptér, ktorý vráti nula akcií pri podniku, ktorý zvyčajne nejaké má: varovanie v logu (pravdepodobne sa zmenil web).

## Formát výstupu

```json
{
  "schema_version": 1,
  "generated_at": "2026-10-29T06:00:00+01:00",
  "venues": [ ... ],
  "events": [ ... ]
}
```

- Obsahuje akcie od včera do +180 dní. Ostatné vypadávajú.
- Podniky sú vo výstupe celé, PWA si z nich berie názvy, odkazy, IG a štítky.

## Otvorené otázky

1. Pevný zoznam žánrov (spoločný pre `music` podniku a `genres` akcie).
2. Stand-up a podobné formáty: samostatne, alebo stačí `other`? (Kvízy rozhodnuté: samostatný formát `quiz`.)
3. Štítky pre zvyšné podniky doplní Matej (Acid Coffee, Magneto a ďalšie).
