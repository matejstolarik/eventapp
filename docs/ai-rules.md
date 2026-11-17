# Pravidlá AI pre akcie (zdroj pravdy pre prompt)

Schválené Matejom 2026-11-17 (z rozhodnutí po úlohách 052–054 a z označení 50 akcií v `docs/tasks/056/labels-matej.csv`). Prompt AI (zaradenie aj doplnenie) sa riadi týmto súborom. Zmeny len so súhlasom Mateja; nové pravidlo = nový bod s dátumom.

## A. Postup hľadania
1. Urči všetkých účinkujúcich akcie.
2. O **každom hlavnom** účinkujúcom zisti: kto to je, odkiaľ, **ako sa prezentuje** (kapela / DJ / producent / divadelný súbor…), aký žáner robí, čo vydal.
3. Nájdi stránku akcie (web podniku, **verejná Facebook udalosť**, predpredaj) kvôli cene a času. **Instagram nie. Resident Advisor (`ra.co`) nikdy.**
4. Typ, žánre aj popis urči **z tých istých zistení** (jeden prieskum, nie oddelene).

## B. Typ (jeden hlavný `primary_format`, ďalšie len doplnkové)
1. Rozhoduje **hlavný interpret**, nie názov akcie ani označenie podniku („Party – Hlavní stage“ v Cross Clube je názov sály).
2. Kapela, spevák, raper naživo, **elektronika hraná naživo** (live set, „LIVE“/„(live)“ pri hlavnom interpretovi, živá kapela, spev, nástroje; napr. Bonobo, Tinlicker, Modeselektor LIVE, Amphibian Quadrophonic Soundsystem, CREDIT 00 (live)) → `concert`.
3. DJ-i (prezentujú sa ako DJ), veľa mien oddelených ☆/+ a noc do rána, **žánrová noc bez headlinera** (DRUMSTATION), **sound system** (Bashment) → `dj`.
4. Spevák/kapela a po nich DJ → `concert`, `dj` doplnkový. Časový harmonogram kapiel („20:00 X, 21:00 Y“) → `concert`.
5. `party` = len veľká komerčná/mainstreamová párty kvôli atmosfére (komerčné kluby, Erasmus/študentské, hity 80./90., open bar). V komerčnom klube (`commercial_club`): generická noc → `party`; **DJ je hlavné lákadlo a párty je postavená okolo neho** (SLVL) → `primary_format: dj`, `party` doplnkový; **lákadlom je párty samotná** (téma, formát, napr. Video Oldies Rudy Tučeka, Student Wednesday), aj keď je DJ menovaný → `party`. Pozná sa to hlavne z názvu a popisu (Matej 2026-11-17). Mimo komerčných klubov len pri jasnom signáli s dôvodom.
6. Kultúra podľa podtypu: `film`, `theatre`, `dance`, `comedy` (stand-up), `talk` (čítanie a diskusia: krst knihy, poézia, piesne + texty, prednáška), `performance` (performatívne pásmo), `workshop` (aj hudobný/DJ), `opening` (výstava), `quiz`; inak `other`.

## C. Žánre
1. **Zoradené od hlavného.** Zložené názvy → hlavný prvý: „ambient techno“ → `techno, ambient`; „mainstage“ → `edm, electronic`; „oldies“ → `oldies` (+ `pop` len ak sedí).
2. Mapovať **len synonymá a pravopisné varianty** (`rap → hip-hop`). Podžánre zo zoznamu ostávajú samostatné; nadradený žáner sa **nepridáva automaticky** (`metalcore` ≠ `metal`).
3. **Každý žáner musí mať oporu v nájdenom fakte** o interpretovi. Bez opory žiadny.
4. Žáner mimo zoznamu → návrh (`genre_candidates`), Matej schvaľuje.
5. Žánre aj pri filme a divadle (zoznamy `film_genres`, `stage_genres`).
6. Nemapovať: `bass music` ≠ `uk-bass` (len interpreti z UK) ≠ `bassline` (štýl zo Sheffieldu). `hardcore` je samostatný (nie automaticky punk ani techno).

## D. Cena
1. Len cena **výslovne uvedená pri tejto akcii a dátume**, so zdrojom; AI cenu pipeline overí otvorením zdrojovej stránky. Cena zo stránky podniku má prednosť.
2. Štruktúra `price {min, max, currency, kind}`; zobrazenie podľa jazyka appky bez ďalšieho textu: `350 Kč` · rozpätie `250–350 Kč` (zľavnená, predpredaj/na mieste, BASIC/VIP) · `od 950 Kč` · `20 €` · Zdarma · Dobrovoľné vstupné · Zdarma, rezervácia.

## E. Čas
Len výslovne uvedený pri akcii; inak prázdny. Nikdy neodhadovať.

## F. Popis
3–5 viet, vecne a do hĺbky (kto, odkiaľ, čím je známy, čo vydal, čo je na večeri zvláštne), **bez reklamných fráz a pátosu**, bez výkričníkov a emoji, bez ceny/času/miesta. Žánre ako názvy („techno“, nie „technové“). Len fakty zo zdrojov; z pôvodného textu fakty, nie vety. CZ hlavný, SK a EN preklad. Vzor: popis Allt v úlohe 054 časť 4b.

## G. Interpreti a Spotify
Mená všetkých účinkujúcich. Pri každom hlavnom interpretovi hľadanie „<meno> spotify“; odkaz `open.spotify.com/artist/…` len ak je vo výsledkoch a zhoda je istá (meno + žáner alebo krajina). Inak appka vyhľadá podľa mena.

## H. Neistota
Keď AI nič nenájde (napr. REVO: Z Gumy Do Gumy), nechaj prázdne a označ „na kontrolu“. Nič nehádať.
