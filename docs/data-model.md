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
- `commercial_club`: nepovinné, `true` = komerčný klub; **každá** hudobná akcia (`concert`/`dj`/`music`) v ňom je `party` s `primary_format = "party"` (pravidlo pipeline `apply_commercial_clubs`, bez AI; task 053). Chýba = `false`. Nastavuje Matej ručne.
- `lat`, `lng`: súradnice pre zobrazenie na mape. **Povinné** — podnik bez súradníc sa na mape nezobrazí. Zdroj: OSM Nominatim alebo mapa na webe podniku; vždy overiť adresou. Nový podnik bez súradníc sa do `venues.json` nepridá.
- `description`: krátky popis podniku (2–4 vety, čistý text, bez prekladu, z webu podniku). `null` ak podnik nemá stránku „O nás" / „About" alebo tam popis nie je.
- `description_url`: URL stránky, z ktorej popis pochádza. `null` ak `description` je `null`.
- `image_url`: URL fotky podniku (`og:image` domovskej stránky alebo stránky „O nás"), len URL, nekopírovať. `null` ak sa vhodný obrázok nenašiel. Nastavuje Matej ručne alebo podľa reportu.
- `image_source`: URL stránky, z ktorej `image_url` pochádza. `null` ak `image_url` je `null`.
- `image_thumb`: relatívna cesta k náhľadu (`img/venues/<id>.jpg`, 160×160 JPEG) generovaného pipeline z `image_url`. `null` ak `image_url` je `null` alebo stiahnutie zlyhalo. Generuje pipeline automaticky; Matej ho nenastavuje ručne.
- `closing`: nepovinné. Čas zatvorenia podľa dňa v týždni: `{"fri": "05:00", "sat": "07:00", "mon": "02:00"}`. Deň = deň, keď akcia **začala**. Chýbajúci deň alebo celé pole `null` = neznáme (použije sa 3:00). Ak je `closing` ≥ `start_time` akcie, zatvára sa v ten istý deň; inak nasledujúci deň ráno (`"00:00"` = polnoc po dni začiatku). Akcia bez `start_time`: `closing` < 12:00 → nasledujúci deň, inak ten istý deň. Hodnoty nastavuje Matej ručne. (Matej 2026-11-16)
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
  "primary_format": "dj",
  "genres": ["drum-and-bass", "techno"],
  "character": ["underground"],
  "artists": ["Zombie Cats", "Tanukichi"],
  "price_text": "200 Kč",
  "free": false,
  "ticket_url": "https://ra.co/events/...",
  "image_url": null,
  "image_thumb": null,
  "image_detail": null,
  "image_detail_size": null,
  "description": "Popisný text akcie z webu podniku, čistý text, max 1 000 znakov.",
  "description_source": "source",
  "descriptions": { "cs": "Český popis od AI …", "sk": "Slovenský preklad …", "en": "English translation …" },
  "artist_links": [{ "name": "Zombie Cats", "spotify_url": "https://open.spotify.com/artist/..." }],
  "enrichment": {
    "run":         { "checked_at": "2026-11-17", "model": "claude-haiku-5-5", "searches": 2 },
    "formats":     { "by": "ai_web", "model": "claude-haiku-5-5", "checked_at": "2026-11-17", "source_url": "https://...", "confidence": 0.9 },
    "genres":      { "by": "ai_web", "model": "claude-haiku-5-5", "checked_at": "2026-11-17", "source_url": "https://...", "confidence": 0.9 },
    "price_text":  { "by": "ai_web", "model": "claude-haiku-5-5", "checked_at": "2026-11-17", "source_url": "https://..." },
    "description": { "by": "ai_web", "model": "claude-haiku-5-5", "checked_at": "2026-11-17", "source_urls": ["https://..."] },
    "genre_candidates": [{ "raw": "neurofunk", "kind": "music", "maps_to": "drum-and-bass" }]
  },
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
- `formats` (viac naraz): `concert` (živí hudobníci na pódiu — kapela, sólo umelec, orchester, živý elektronický set), `dj`, `party` (veľká komerčná/mainstreamová párty, kam ľudia idú kvôli atmosfére, nie kvôli konkrétnej hudbe či interpretovi: komerčné kluby, Erasmus/študentské, hity 80./90., open bar, mainstreamové tematické večery; klubová noc zameraná na hudbu/DJ-ov je `dj`, nie `party`; mimo komerčných klubov len pri jasnom signáli, AI uvedie dôvod v `classification.reason`; v podniku s `commercial_club: true` je každá hudobná akcia `party`; task 053), `music` (hudobná akcia, pri ktorej sa nedá rozlíšiť concert vs. dj), `dance` (tanečné predstavenie), `talk` (čítanie, debata, prednáška, krst knihy, diskusia, večer piesní + poézie + prózy; v appke štítok „čítanie a diskusia“ / „čtení a diskuse“ / „talk & reading“, task 058), `stand-up` (stand-up comedy; do task 065 `comedy`, starý kód sa pri čítaní predchádzajúceho behu, odpovede AI aj `manual.json` premení na `stand-up`; filmový žáner `comedy` v `genres` je iná vec), `workshop` (aj hudobný / DJ workshop), `theatre`, `opening` (vernisáž), `film`, `quiz` (hospodské kvízy), `performance` (performance, performatívne umenie, živé pásmo na pomedzí divadla a výtvarného umenia; typ kultúra, ikona masky; task 058), `other`. Pravidlá AI pre typ: `docs/ai-rules.md` časť B. V podniku s `commercial_club: true` sa `party` pridá vždy; `primary_format` je `party`, okrem prípadu, keď AI určila `dj` (známy menovaný DJ ako headliner, task 058).
  - **`concert` vs. `dj` rozhoduje hlavný interpret** (task 053): koncert s DJ afterparty = `concert` (afterparty môže ostať ako druhý formát `dj`); klubová noc s kapelami aj DJ-mi bez jasného hlavného interpreta = `dj`; rap/hip-hop naživo = `concert`; DJ set hudobníka = `dj`; jam session a open mic = `concert` (dočasne). Elektronický live set: zatiaľ bez pevného pravidla (rozhodne kolo označovania, task 053 časť 3).
- `primary_format`: jeden formát hlavnej časti akcie (z `formats`), rozhoduje typ akcie pre farbu a ikonu (task 053). Určí ho AI vrstva 2 (hlavný interpret: koncert s DJ afterparty → `concert`) alebo pravidlo komerčného klubu (`party`). `null` ak ho pipeline neurčila (vrstva 1 zo sekcie/kľúčových slov, ručná oprava) – appka potom použije poradie `party` → `dj` → `concert`.
- `genres`: z pevného zoznamu (zoznam treba dohodnúť).
- `character`: zdedí sa od podniku, AI ho môže pre konkrétnu akciu prepísať (napr. retro noc v inak alternatívnom klube).
- `price` (task 058, schválené Matejom 2026-11-17): štruktúrovaná cena `{ min, max, currency, kind }`, `kind` ∈ `paid` | `free` | `voluntary` (dobrovoľné vstupné) | `free_reservation` (zdarma s rezerváciou); `currency` `CZK` / `EUR` / `null` (zdroj menu neuvádza). Viac cien (zľavnená, predpredaj / na mieste, BASIC / VIP, vlny) → rozpätie `min`–`max`; jedna cena → `min == max`; len „od X“ → `min`, `max: null`. Počíta ju pipeline z `price_text` (`pipeline/price.py`, rovnako pre web podniku aj AI); text bez rozpoznateľnej sumy alebo slova zdarma/dobrovolné → `null`. Appka zobrazuje len `price` podľa jazyka (`350 Kč`, `250–350 Kč`, `od 950 Kč` / `from 950 CZK`, `20 €`, Zdarma / Free, Dobrovoľné vstupné / Dobrovolné vstupné / Pay what you want, Zdarma, rezervácia / Zdarma, rezervace / Free, booking required). Pôvod: `enrichment.price_text`.
- `price_text`: text tak, ako ho dáva zdroj (v appke sa od task 058 nezobrazuje, je podklad pre `price`). `free` je odvodené (vstup zdarma áno/nie). Zdroje (task 054): stránka akcie podniku (riadok „Vstupné:“, „Vstupenky:“, „Admission:“ – Cross Club, EPIC, Roxy, MeetFactory, Kasárna, Čitárna; `detail_enrich`, kontrola chýbajúcej ceny najviac raz za 7 dní), štítok „vstup zdarma“ (Archa+), „VSTUP VOLNÝ“ (Akropolis); inak AI s overením (pozri `enrichment`).
- `sold_out`: `true` len ak zdroj výslovne uvádza vypredané; `false` len ak zdroj výslovne ponúka lístky; inak `null`. Nie je to `status`.
- `room`: nepovinné, sála alebo priestor v rámci podniku tak, ako ho uvádza zdroj (napr. Akropolis: Velký sál, Malá scéna, Jazz Bar); `null` ak zdroj ho neuvádza.
- `ticket_url`: odkaz priamo na predaj lístkov (napr. GoOut, RA, Ticketmaster). Stránka akcie na webe podniku patrí len do `sources[].url`, nie sem. Ak zdroj neposkytuje predajný odkaz, pole je `null`.
- `image_url`: URL obrázka akcie z webu podniku. Náhrada z GoOut sa nepoužíva (rozhodnutie 2026-11-17 po úlohe 060). `null` ak obrázok nie je.
- `image_thumb`: relatívna cesta k náhľadu (`img/events/<id>.jpg`, 640×480 JPEG (4 : 3, task 068): zdroj na výšku (šírka / výška < 0,8) celý v strede na rozmazanej a stmavenej výplni z neho samého, ostatné stredový výrez 4 : 3; pred 068 štvorec 480×480, do 2026-11-18 240×240) generovaného pipeline z `image_url`. `null` ak `image_url` je `null`, stiahnutie zlyhalo, alebo bolo odložené (limit 150 za beh). Generuje pipeline automaticky; Matej ho nenastavuje ručne.
- `image_detail`: relatívna cesta k zmenšenej kópii obrázka bez orezu (`img/events/detail/<id>.jpg`, JPEG, dlhšia strana najviac 1200 px, menší obrázok sa nezväčšuje) generovanej pipeline z `image_url` spolu s náhľadom (jedno stiahnutie, rovnaký limit a cache). `null` v tých istých prípadoch ako `image_thumb`. Používa ho stránka akcie (celý obrázok, task 068; predtým appka nepoužívala, task 066).
- `image_detail_size`: rozmery súboru `image_detail` v px ako `[šírka, výška]` (čítané z JPEG súboru po jeho zápise), alebo `null`, keď `image_detail` je `null`. Stránka akcie podľa neho vopred vyhradí miesto pre obrázok (bez posunu rozloženia po načítaní). Pridané v task 069.
- `description`: popis akcie z webu podniku. Čistý text bez HTML, max 1 000 znakov, skrátený na koniec vety (`. `, `! `, `? `), ak je dlhší — `null` ak zdroj popis neposkytuje alebo je prázdny. Adaptéry ho extrahujú priamo (RSS, JSON-LD, API). Detail enrichment (`pipeline/detail_enrich.py`) ho dograbí z detailnej stránky akcie po normalizácii (raz na akciu, cache, limit 40 fetchov na podnik a beh). Venue-špecifický CSS selektor `detail_desc_selector` v source config (venues.json) určuje, z ktorého elementu brať popis. Popis rovnajúci sa názvu akcie sa zahodí.
- `description_source`: `"source"` ak popis pochádza zo zdrojových dát (adaptér alebo detail enrichment), `"manual"` ak je z `data/manual.json` (task 060), `"ai"` ak zdroj popis nemá a `description` je český text z `descriptions.cs` (task 054), `null` ak `description` je `null`. Pôvodný popis zo zdroja ostáva v `description` (v appke sa nezobrazuje, je podklad pre AI).
- `descriptions` (task 054, schválené Matejom 2026-11-17): popis od AI v troch jazykoch `{ "cs", "sk", "en" }`, jedno volanie; `cs` je hlavný, `sk` a `en` sú preklady. 3–5 viet, vecne, z faktov zdroja a hľadania vlastnými slovami (nie vety z pôvodného popisu), bez reklamných fráz, výkričníkov, emoji, ceny, času a miesta; názvy žánrov sa neskloňujú. Text s výkričníkom, emoji alebo reklamnou frázou pipeline zahodí. Appka zobrazí `descriptions[jazyk]` → `descriptions.cs` → `description`; pôvod sa v appke neoznačuje. Nepovinné, chýba ak AI nemala fakty.
- `artist_links` (task 054; od task 060 len z `data/manual.json`): `[{ "name", "spotify_url" }]`, odkaz na profil interpreta na Spotify (`https://open.spotify.com/artist/<22 znakov>`). Bez ručného záznamu pole chýba. Tlačidlo Spotify v appke otvorí prvý. `artists` ostáva zoznam textov. Nepovinné.
- `enrichment` (task 054, návrh z 052 časť 3 schválený Matejom 2026-11-17): pôvod údajov, ktoré nedodal zdroj podniku. Kľúč = pole (`formats`, `genres`, `price_text`, `start_time`, `artists`, `artist_links`, `description` – platí pre `descriptions` a pri `description_source: "ai"` aj pre `description`), hodnota `{ by, model, checked_at, source_url | source_urls, confidence?, reason? }`:
  - `by`: `ai_text` (len z textu akcie, bez webového zdroja = odhad; len pri `formats`/`genres`), `ai_web` (overené hľadaním, so zdrojom) alebo `manual` (`data/manual.json`, task 060; bez `model` a `source_url`).
  - `run`: `{ checked_at, model, searches }` – kedy AI akciu spracovala (cache, pozri nižšie). Je aj vtedy, keď AI nedoplnila nič.
  - `genre_candidates`: žánre od AI mimo našich zoznamov `[{ raw, kind: music|film|stage, maps_to }]` (task 054 časť 4a); `maps_to` = náš žáner, pod ktorý patrí, alebo `null`. Z nich sa robia návrhy nových žánrov, v appke sa nezobrazujú.
  - Pravidlá: (1) údaj zo zdroja podniku má vždy prednosť; AI vyplní len prázdne pole, a keď ho neskôr dodá zdroj, AI hodnota aj jej záznam v `enrichment` sa zahodia. Formát AI nemení len pri `classification.method` `manual`; typ od AI má prednosť pred kategóriou podniku (`source`) aj kľúčovými slovami (`keyword`), tie ostávajú ako záloha, keď AI typ nevráti (task 063, `ai-rules.md` B7). Žánre AI nemení pri `manual` a `source` (žánre doplní, ak zdroj nedal žiadne). (2) `ai_web` hodnota bez `source_url` sa neuloží. (3) `ra.co` nikdy nie je zdroj. (4) Cena od AI sa uloží len po overení jedným GET na jej `source_url`: text stránky musí obsahovať sumu (pri „zdarma“ slovo zdarma/free/volný) **a** názov akcie alebo hlavného interpreta. Task 060: stránka sa načítala a suma na nej nie je → cena sa zahodí. Stránka sa nedá prečítať (chyba GET / 403, prázdna, alebo bez jedinej sumy = cenu kreslí JavaScript, napr. GoOut) **a** `source_url` je predpredaj (`goout.net`, `smsticket.cz`, `oazis.app`, `ticketportal.cz`, `ticketstream.cz`) → cena sa ponechá s `enrichment.price_text.verified: false`; nečitateľná stránka podniku → zahodiť. `verified` chýba = overená.
  - Cache: AI ide len na akcie v najbližších 60 dňoch, ktoré sú nové alebo majú zmenený názov (porovnáva sa s predchádzajúcim `events.json`, akcia s `enrichment.run.checked_at` a rovnakým názvom sa neposiela znova).
- `classification`: ako sa určili formát a žánre (`source`, `keyword`, `manual`, `llm`, `llm+web` – `llm+web` = AI s hľadaním a webovým zdrojom, task 054) a s akou istotou. Nepovinné `reason`: krátky text od AI, prečo je akcia `party` (task 053; len pri `method = "llm"` a formáte `party`). `null` ak pipeline formát ani žánre neurčila (napr. čistý RSS bez kategorizácie).
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
afro, afrobeats, alt-pop, alternative-rock, ambient, bass-music, bassline, blues,
breakbeat, chanson, classic-rock, classical, country, dance-pop, dance-punk, dancehall,
darkwave, death-metal, disco, doom-metal, dream-pop, drill, drum-and-bass, dub, dubstep,
ebm, edm, electro, electro-swing, electronic, emo, experimental, folk, funk, garage-
rock, goregrind, gothic-rock, grime, grindcore, grunge, hard-techno, hardcore,
hardstyle, hip-hop, house, hyperpop, indie, industrial, jazz, jungle, latin, metal,
metalcore, neo-soul, noise, noise-punk, noise-rock, oldies, orchestral, pop, pop-punk,
post-hardcore, post-punk, post-rock, psytrance, punk, rave, reggae, reggaeton, rnb,
rock, shoegaze, ska, slowcore, sludge-metal, soul, soundtrack, stoner-metal, synthwave,
tech-house, techno, trance, trap, uk-bass, uk-garage, world
```

(86 položiek — pôvodných 27 schválených Matejom 2026-11-04; pridané 2026-11-08: disco, hardstyle, latin, r-n-b, ska, trance; task 058 (Matej 2026-11-17): blues, industrial, hardcore, bass-music, rave, dream-pop, darkwave, slowcore, oldies, edm, metalcore, death-metal, grindcore, goregrind; `r-n-b` premenované na `rnb`; **task 065 (Matej 2026-11-17)**: hard-techno, breakbeat, jungle, synthwave, grime, trap, drill, afro, afrobeats, dub, dancehall, alternative-rock, noise-rock, post-rock, grunge, gothic-rock, classic-rock, garage-rock, emo, post-hardcore, noise, pop-punk, dance-punk, noise-punk, doom-metal, sludge-metal, stoner-metal, hyperpop, dance-pop, alt-pop, soul, neo-soul, classical, orchestral, soundtrack, country, chanson, psytrance, reggaeton. Zoznam v kóde: `pipeline/genres.py`.)

**Hierarchia (task 065, `docs/ai-rules.md` C7):** `data/genre_hierarchy.json` `{ "podžáner": ["rodič", …] }` (aj viac rodičov). Rodič je žáner zo zoznamov alebo zastrešenie, ktoré nie je štítok: `alternative` (len filter, ai-rules C8) a podtypy kultúry `film`, `theatre`, `dance` (C9). Slúži filtru a Pre teba; rodič sa k štítku **nepridáva**. V `genres` akcie sa rodič odstráni, keď je prítomný jeho podžáner a názov rodiča je obsiahnutý v názve podžánru (`doom-metal` + `metal` → `doom-metal`); inak ostáva (`trap` + `hip-hop`). `alternative` sa ako štítok zahodí. Test konzistencie: každý rodič existuje, žiadne cykly (`tests/test_genres_065.py`).

**Zahodení kandidáti (task 065):** `data/genre_ignored.json` `{ "ignored": [surové názvy], "ignored_music": [len ako hudobný žáner] }`; nenavrhujú sa znova (`genres-review`, `site/genre_proposals.json`).

**Poradie a mapovanie (task 058, `docs/ai-rules.md` C):** `genres` je zoradené od hlavného žánru (zložené názvy: „ambient techno“ → `techno, ambient`; „mainstage“ → `edm, electronic`). Mapujú sa len synonymá a pravopisné varianty (`rap → hip-hop`, „drum and bass“ → `drum-and-bass`); podžánre zo zoznamu ostávajú samostatné a nadradený žáner sa automaticky nepridáva (`metalcore` ≠ `metal`). `bass music` je `bass-music`, nie `uk-bass` ani `bassline`. Schválené mapovania: `data/genre_aliases.json` (`{ "surový": "náš" | ["hlavný", "ďalší"] }`).

### Žánre kultúry (task 054 časť 4a, Matej 2026-11-17)
- `film_genres` (film) a `stage_genres` (divadlo, tanec, performance): plnia sa len schválenými návrhmi (pridáva hlavný chat podľa Matejovho rozhodnutia; v kóde `FILM_GENRES` / `STAGE_GENRES` v `pipeline/genres.py`). `film_genres` (task 065, rodič `film`): action, adventure, animation, arthouse, biography, comedy, crime, cult-classic, documentary, drama, experimental, family, fantasy, history, horror, music, musical, mystery, queer, romance, sci-fi, short, thriller, war, western. `stage_genres`: `physical-theatre` (task 058); task 065: pod `theatre` drama, musical, opera, puppet-theatre, improv, cabaret, new-circus; pod `dance` contemporary-dance, ballet, dance-theatre; experimental. Rovnaký názov vo filme aj na scéne (drama, musical, experimental) = jeden žáner s viacerými rodičmi. Scénické žánre comedy, stand-up a performance sa nezavádzajú (C9). `genres` akcie s formátom `film` / `theatre` / `dance` berie len z týchto zoznamov.
- AI vracia aj žánre mimo zoznamov (`enrichment.genre_candidates`). Namapuje sa len pravopisný variant alebo schválené mapovanie z `data/genre_aliases.json` (ručne; `maps_to` navrhnuté AI sa od task 058 samo nepoužije), všetky použité mapovania (schválené + od AI) pipeline zapíše do `site/genre_aliases.json` na kontrolu.
- Nenamapované žánre sú **návrhy**: `site/genre_proposals.json` `[{ name, kind: music|film|stage, count, event_ids }]`, len pri **≥ 3 akciách**; v appke sa nezobrazujú. Na kontrolu Matejovi (`python -m pipeline.genres_review`) od **2 akcií** (task 065); zahodené (`data/genre_ignored.json`) sa nevypisujú. Akcia bez hudobného/filmového/scénického typu (talk, other): žáner zo zoznamu sa berie ako hudobný, nenamapovaný názov nie je kandidát (task 065).

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

## Ručné doplnky (`data/manual.json`, task 060, schválené Matejom 2026-11-17)

Zapisuje hlavný chat podľa Mateja. Ručné hodnoty majú prednosť pred AI aj pred zdrojom podniku; `status` (zrušené) a `sold_out` (vypredané) zo zdroja sa nikdy neprepíšu (v súbore sa nedajú zadať). Pipeline ich použije dvakrát: po pravidlovej klasifikácii (pred AI zaradením a AI doplnením – AI potom nemení typ ani žánre a pri známej sérii ich nehľadá, len účinkujúcich a popis večera) a po AI doplnení (ručné hodnoty prepíšu AI).

```json
{
  "artist_links": {
    "Bad Karma Boy": "https://open.spotify.com/artist/0123456789abcdefghijkl"
  },
  "events": {
    "kasarna-karlin-2026-12-02-bad-karma-boy-album-launch-island-mint": {
      "formats": ["concert"], "primary_format": "concert", "genres": ["indie"],
      "price_text": "350 Kč", "start_time": "19:30",
      "descriptions": { "cs": "…", "sk": "…", "en": "…" }
    }
  },
  "series": [
    { "venue_id": "fuchs2", "title_contains": "LATIN CORE THURSDAYS",
      "formats": ["party"], "genres": ["latin", "reggaeton"],
      "descriptions": { "cs": "Krátky popis série …" } }
  ]
}
```

- `artist_links`: meno interpreta → `https://open.spotify.com/artist/<22 znakov>` (ID z kworb.net, overené na stránke Spotify). Odkaz sa pripojí ku každej akcii, kde je to meno v `artists` alebo ako celá časť názvu (delenie podľa `+`, `,`, `:`, `☆`, ` - `, `b2b`, `w/` …; bez diakritiky a veľkosti písmen, nie časť slova). **Iné odkazy na Spotify sa neukladajú** (odkazy od AI sa zahodia, task 060 časť 6).
- `events`: oprava polí akcie podľa `event_id`; povolené `formats`, `primary_format`, `genres`, `price_text`, `start_time` (`HH:MM`), `descriptions` (`{cs, sk?, en?}`, `cs` povinné).
- `series`: opakujúca sa séria – `venue_id` + `title_contains` (podreťazec názvu bez diakritiky a veľkosti) → `formats`, `primary_format`, `genres`, `descriptions` (krátky popis série). Platí prvý zhodný záznam; záznam v `events` má prednosť pred sériou.
- Neplatné záznamy pipeline zaloguje a vynechá. Kľúč `note` (poznámka) sa ignoruje.
- Pôvod: `enrichment.<pole> = { "by": "manual", "checked_at" }` (`description` pre `descriptions`); pri zmene typu alebo žánrov `classification.method = "manual"`. Ak akcia nemá popis zo zdroja, `description` = `descriptions.cs` a `description_source = "manual"`. Ručné hodnoty sa z predchádzajúceho behu nepreberajú ako cache – po odstránení záznamu zo súboru zmiznú.

## Kategorizácia (formát, žánre, charakter)

Dve vrstvy:
1. **Deterministická (layer 1):** Priorita: manual override → sekcia zdroja → kľúčové slová v názve → fallback `music`. Bez hádania podľa podniku — ak rule nepomôže, formát ostáva `music` alebo prázdny.
2. **AI (layer 2, Claude Haiku):** Klasifikuje zostatok (prázdne formáty alebo `music`). Vstup: názov, interpreti, sekcia, čas začiatku, podnik a jeho štítky. Výsledok sa cachuje v `events.json` a znova sa volá AI len pri zmene názvu.

`classification = {"method": "source" | "keyword" | "llm" | "manual", "confidence": float, "reason"?: string}`

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

## Stav pipeline medzi behmi (`pipeline_state.json`, task 054)

Zverejnený na GitHub Pages vedľa `events.json` (pipeline ho načíta z `PREVIOUS_EVENTS_URL` → `pipeline_state.json`, lokálne zo `site/`). Nie je pre appku.
```json
{ "detail_checked": { "<event id>": "2026-11-17" },
  "ai_searches": { "month": "2026-11", "count": 312 },
  "ai_cost": { "month": "2026-11", "usd": 1.42, "runs": 9 },
  "updated_at": "2026-11-17T05:20:00+01:00" }
```
- `detail_checked`: kedy sa stránka akcie naposledy kontrolovala kvôli chýbajúcej cene/času (opakuje sa najskôr po 7 dňoch).
- `ai_searches`: počet webových hľadaní AI v kalendárnom mesiaci (limit 400 pri Claude; pri DeepSeek 3 000, skutočný limit je rozpočet v $). Ak sa stav nedá načítať (iná chyba ako 404), AI doplnenie sa v tom behu nespustí.
- `ai_cost` (task 062, DeepSeek): súčet ceny AI (zaradenie + doplnenie) za kalendárny mesiac v $ a počet behov. Rozpočet behu = min(0,30 $, 3 $ − `usd`); po prekročení sa AI zastaví, beh pokračuje. Nový mesiac začína od 0.

## Zhrnutie denného behu (`data/cache/run_summaries/<YYYY-MM-DD>.json`, task 057)

Jeden súbor na deň (pražský dátum; ďalší beh v ten istý deň ho prepíše), posledných 60 dní. Nie je v repe ani na Pages: drží ho cache GitHub Actions (`daily.yml`, kľúč `run-summaries-*`). Číta ho `pipeline.alerts` (upozornenia) a `pipeline.weekly_report` (týždenný report). Nie je pre appku.
```json
{ "date": "2026-11-19", "generated_at": "2026-11-19T05:31:00+01:00",
  "success": true, "has_previous": true, "events": 377, "new": 12, "gone": 2,
  "venues": { "roxy": { "events": 45, "new": 3, "gone": 0, "music_events": 40,
      "missing": { "image": 0, "time": 2, "price": 10, "genre": 1, "description": 0 },
      "sources": [{ "label": "rss", "events": 45, "warning": null }] } },
  "ai": { "provider": "deepseek", "searches": 120, "month_searches": 991, "search_limit": 3000,
          "cost_usd": 0.12, "month": "2026-11", "month_cost_usd": 1.37, "month_budget_usd": 3.0,
          "type_changed": 4, "nothing_found": 1, "prices_dropped": 2, "low_confidence": 8,
          "search_limit_reached": false, "http_402": false },
  "review": [{ "id": "…", "venue_id": "…", "title": "…", "date": "…", "source_url": "…",
               "kind": "price_dropped", "detail": "price '300 Kč': not on page" }],
  "no_spotify": [{ "id": "…", "…": "…", "artists": ["Band X"] }],
  "unverified_prices": [{ "id": "…", "…": "…", "price_text": "300 Kč", "price_source": "…" }],
  "genre_proposals": [{ "name": "shoegaze", "kind": "music", "count": 3, "examples": [{ "id": "…" }] }],
  "warnings": ["…"] }
```
- `success`: výsledok celého jobu (zapíše krok upozornení na konci `daily.yml`); pri zlyhaní pred zápisom zhrnutia vznikne len `{ date, generated_at, success: false }`.
- `sources[].warning`: `null` / `zero_events` / `error` (ako v job summary). `new` = id nebolo v predošlom behu; `gone` = akcia z predošlého behu s dátumom od dnes, ktorá zmizla.
- `missing`: počet akcií bez poľa – `image` (`image_url`), `time` (`start_time`), `price` (bez `price_text`/`price` a nie `free: true`), `genre` (len hudobné akcie `concert`/`dj`/`party`/`music`; základ `music_events`), `description`.
- `review[].kind`: `ai_nothing` (AI hľadala, nedoplnila nič), `low_confidence` (typ od AI s `confidence` < 0,6), `price_dropped`, `genres_dropped` (zahodené ochranami AI v tomto behu), `type_changed` (`old` → `new` formáty v tomto behu).
- `no_spotify`: nové akcie s typom `concert`/`dj`, prví dvaja interpreti bez `artist_links`. `unverified_prices`: cena od AI s `verified: false` v najbližších 14 dňoch.
- Testovací prepínač `ALERT_SIMULATE_ZERO=<venue_id>` (vstup `simulate_zero_source` v `daily.yml`): zdroje podniku sa v zhrnutí zapíšu s 0 akciami; `events.json` sa nemení.

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
