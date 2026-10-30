# Dátový model v1

Hodnoty v JSON príkladoch sú ilustračné (čas, cena a odkazy nie sú overené údaje).
Stav: návrh, väčšina rozhodnutí odsúhlasená 2026-10-29. Zdroj pravdy pre dátové štruktúry. Zmeny najprv navrhnúť, potom upraviť tento súbor.
Posledná aktualizácia: 2026-10-29

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
  "sources": [
    { "type": "ra", "club_id": 13354 },
    { "type": "rss", "url": "https://www.crossclub.cz/cs/rss/program/" }
  ],
  "active": true,
  "notes": null
}
```

- `id`: slug, stabilný, nikdy sa nemení (odkazujú naň obľúbené v PWA).
- `sources`: môže byť prázdne. Podnik bez zdroja akcií (napr. Magneto, Popocafepetl) ostáva v databáze, appka ukáže jeho profil a odkazy, len bez akcií.
- `capacity`: nepovinné, len overené číslo.
- `lat`, `lng`: súradnice pre budúcu mapu akcií. Doplniť už teraz pri zakladaní podniku, neskôr by sa dopĺňali spätne.
- Typy zdrojov v1: `ra`, `rss`, `jsonld`, `html`. V2 pribudne `instagram`.

### Štítky podniku (nastavuje Matej ručne)

**type** (viac naraz): `concert-club`, `dance-club`, `dj-bar`, `bar`, `cafe`, `culture-center`, `jazz-club`, `concert-hall`, `cinema`

**character** (viac naraz): `underground`, `alternative`, `experimental`, `commercial`, `retro`, `queer`, `student`

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
  "end_time": null,
  "formats": ["dj"],
  "genres": ["drum-and-bass", "techno"],
  "character": ["underground"],
  "artists": ["Zombie Cats", "Tanukichi"],
  "price_text": "200 Kč",
  "free": false,
  "ticket_url": "https://ra.co/events/...",
  "image_url": null,
  "sources": [
    { "type": "ra", "url": "https://ra.co/events/...", "external_id": "..." },
    { "type": "rss", "url": "https://www.crossclub.cz/cs/program/8697-neurocells-hard-rave/", "external_id": "8697" }
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
- `end_time`: nepovinné, ak akcia ide cez polnoc, `end_time` je menší ako `start_time`.
- `formats` (viac naraz): `live` (živí hudobníci na pódiu), `dj`, `theatre`, `opening` (vernisáž), `film`, `quiz` (hospodské kvízy), `other`.
- `genres`: z pevného zoznamu (zoznam treba dohodnúť).
- `character`: zdedí sa od podniku, AI ho môže pre konkrétnu akciu prepísať (napr. retro noc v inak alternatívnom klube).
- `price_text`: text tak, ako ho dáva zdroj. Ceny neparsujeme. `free` je odvodené (vstup zdarma áno/nie).
- `ticket_url`: odkaz priamo na predaj lístkov (napr. GoOut, RA, Ticketmaster). Stránka akcie na webe podniku patrí len do `sources[].url`, nie sem. Ak zdroj neposkytuje predajný odkaz, pole je `null`.
- `classification`: ako sa určili formát a žánre (`source`, `llm`, `llm+web`) a s akou istotou. `null` ak pipeline formát ani žánre neurčila (napr. čistý RSS bez kategorizácie).
- `status`: `scheduled` | `cancelled` (zdroj výslovne uvádza zrušenie) | `gone` (akcia zmizla zo všetkých zdrojov pred dátumom konania).
- `flags`: problémy, ktoré pipeline zachytila, napr. `date_conflict`, `time_conflict`, `date_suspicious`.

### Výstavy
Ako akcia sa berie len vernisáž (`opening`), jeden večer. Prebiehajúce výstavy sa nezobrazujú v zozname akcií, len v detaile podniku (neskôr).

### Predvolený pohľad v appke
Akcie s formátom `live` alebo `dj`. Ostatné formáty (divadlo, vernisáže, film, kvízy, iné) sa zapínajú filtrom.

## Kategorizácia (formát, žánre, charakter)

Tri vrstvy, od najlacnejšej:
1. **Zdroj**, ak kategóriu dáva (sekcia na webe, žánre na RA), prevedená na naše pevné hodnoty.
2. **LLM bez internetu** z názvu, popisu, interpretov, podniku a sekcie zdroja. Vráti hodnoty aj istotu.
3. **LLM s vyhľadaním interpreta na webe** len pri nízkej istote, hlavne na doplnenie žánru. Výsledok sa ukladá k menu interpreta (cache), aby sa ten istý interpret nehľadal znova.

## Rozhranie adaptéra

Každý adaptér robí jedno: z konfigurácie zdroja vráti zoznam akcií v jednotnom tvare, ešte bez deduplikácie.

```
fetch(venue, source_config) -> list[RawEvent]
```

`RawEvent` má rovnaké polia ako Akcia, okrem `id`, `first_seen`, `last_seen`, `status`, `flags`, `classification`, a namiesto zoznamu `sources` má jeden zdroj. Adaptér zodpovedá za prevod dátumov na miestny čas Prahy.

Nový zdroj (vrátane Instagramu vo v2) = nový adaptér. Zvyšok pipeline sa nemení.

## Deduplikácia

Dve akcie z rôznych zdrojov sú tá istá akcia, ak:
1. majú rovnaký `venue_id` a rovnaký `date`, a
2. podobný názov (normalizovaný: malé písmená, bez diakritiky, bez interpunkcie; zhoda nad prahom), alebo zdieľajú interpreta.

Ak si nie sme istí, akcie nezlučujeme. Duplicita v appke je menšia chyba než zlúčenie dvoch rôznych akcií.

Pri porovnaní s predchádzajúcim `events.json` sa akcia páruje rovnako, aby si zachovala `id` a `first_seen`.

## Zlučovanie polí

Keď viac zdrojov dáva to isté pole, vyhráva zdroj s vyššou prioritou:

`ra` > `jsonld` > `rss` > `html`

Výnimka: prázdna hodnota nikdy neprepíše vyplnenú.

## Kontroly kvality

- Dva zdroje sa nezhodnú v dátume alebo čase: hodnota podľa priority, akcia dostane príznak `date_conflict` / `time_conflict`.
- Dátum v minulosti pri **novej** akcii (taká sa predtým nevidela): príznak `date_suspicious`. Akcie za hranicou +180 dní sa do výstupu vôbec nedostanú (nie sú to chyby, len mimo okno).
- Podozrenie na prehodený deň a mesiac (prípad Kasárna: výpis „12. 2.“ vs. detail 2. 12.): ak sa dátum z výpisu a z detailu líšia práve prehodením, platí detail a akcia dostane príznak.
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
