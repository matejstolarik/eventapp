# Pravidlá AI pre akcie (zdroj pravdy pre prompt)

Schválené Matejom 2026-11-17 (z rozhodnutí po úlohách 052–054 a z označení 50 akcií v `docs/tasks/056/labels-matej.csv`). Prompt AI (zaradenie aj doplnenie) sa riadi týmto súborom. Zmeny len so súhlasom Mateja; nové pravidlo = nový bod s dátumom.

## A. Postup hľadania
1. Urči všetkých účinkujúcich akcie.
2. O **každom hlavnom** účinkujúcom zisti: kto to je, odkiaľ, **ako sa prezentuje** (kapela / DJ / producent / divadelný súbor…), aký žáner robí, čo vydal.
3. Nájdi stránku akcie (web podniku, **verejná Facebook udalosť**, predpredaj) kvôli cene a času. **Instagram nie. Resident Advisor (`ra.co`) nikdy.**
4. Typ, žánre aj popis urči **z tých istých zistení** (jeden prieskum, nie oddelene).
5. **(2026-11-18, úloha 067, vykonanie C5)** Pri filme zisti aj samotný film (réžia, rok, krajina) a jeho žánre podľa zdrojov (animovaný, dokumentárny, dráma…); pri divadle, tanci a performance žáner diela (činohra, súčasný tanec, bábkové divadlo, nový cirkus…). Fakt pre žáner je fakt o filme / diele (C3).

## B. Typ (jeden hlavný `primary_format`, ďalšie len doplnkové)
1. Rozhoduje **hlavný interpret**, nie názov akcie ani označenie podniku („Party – Hlavní stage“ v Cross Clube je názov sály).
2. Kapela, spevák, raper naživo, **elektronika hraná naživo** (live set, „LIVE“/„(live)“ pri hlavnom interpretovi, živá kapela, spev, nástroje; napr. Bonobo, Tinlicker, Modeselektor LIVE, Amphibian Quadrophonic Soundsystem, CREDIT 00 (live)) → `concert`.
3. DJ-i (prezentujú sa ako DJ), veľa mien oddelených ☆/+ a noc do rána, **žánrová noc bez headlinera** (DRUMSTATION), **sound system** (Bashment) → `dj`.
4. Spevák/kapela a po nich DJ → `concert`, `dj` doplnkový. Časový harmonogram kapiel („20:00 X, 21:00 Y“) → `concert`.
5. `party` = len veľká komerčná/mainstreamová párty kvôli atmosfére (komerčné kluby, Erasmus/študentské, hity 80./90., open bar). V komerčnom klube (`commercial_club`): generická noc → `party`; **DJ je hlavné lákadlo a párty je postavená okolo neho** (SLVL) → `primary_format: dj`, `party` doplnkový; **lákadlom je párty samotná** (téma, formát, napr. Video Oldies Rudy Tučeka, Student Wednesday), aj keď je DJ menovaný → `party`. Pozná sa to hlavne z názvu a popisu (Matej 2026-11-17). Mimo komerčných klubov len pri jasnom signáli s dôvodom.
6. Kultúra podľa podtypu: `film`, `theatre`, `dance`, `stand-up` (do 2026-11-17 `comedy`; ikona mikrofónu ostáva), `talk` (čítanie a diskusia: krst knihy, poézia, piesne + texty, prednáška), `performance` (performatívne pásmo), `workshop` (aj hudobný/DJ), `opening` (výstava), `quiz`; inak `other`.
7. **(2026-11-17, Matej)** Interpret, ktorý sa primárne prezentuje ako živý act alebo kapela (live electronic act, nástroje, spev; napr. Tinlicker), je `concert` aj vtedy, keď podnik píše „DJ set“; `dj` doplnkový. Rozhoduje, čím interpret je, nie nadpis podniku. **Typ od AI má prednosť pred kategóriou podniku zo zdroja** (2026-11-17, Matej); ručná oprava (`manual.json`) má prednosť pred oboma.
8. **(2026-11-22, Matej, task 090)** Barové hry a súťaže: **turnaj** (stolný futbal, šípky, beer pong, „darts battle“) a **beer pong** → `party`; **kvíz** (pub quiz, „Z-Quiz“) → `quiz` (kultúra), aj keď je po ňom afterparty. Platí pre všetky miesta, nielen El Magico. Ostatné akcie podľa pravidiel vyššie.

## C. Žánre
1. **Zoradené od hlavného.** Zložené názvy → hlavný prvý: „ambient techno“ → `techno, ambient`; „mainstage“ → `edm, electronic`; „oldies“ → `oldies` (+ `pop` len ak sedí).
2. Mapovať **len synonymá a pravopisné varianty** (`rap → hip-hop`). Podžánre zo zoznamu ostávajú samostatné; nadradený žáner sa **nepridáva automaticky** (`metalcore` ≠ `metal`).
3. **Každý žáner musí mať oporu v nájdenom fakte** o interpretovi. Bez opory žiadny.
4. Žáner mimo zoznamu → návrh (`genre_candidates`), Matej schvaľuje.
5. Žánre aj pri filme a divadle (zoznamy `film_genres`, `stage_genres`).
6. Nemapovať: `bass music` ≠ `uk-bass` (len interpreti z UK) ≠ `bassline` (štýl zo Sheffieldu). `hardcore` je samostatný (nie automaticky punk ani techno).

7. **(2026-11-17, Matej, schválenie žánrov – úloha 065)** Zastrešujúce žánre scény sú povolené (`latin`, `afro`) – výnimka z C2. **Hierarchia** podžáner → rodič (aj viac rodičov) je v `data/genre_hierarchy.json`; slúži filtru a Pre teba, rodič sa k štítku automaticky **nepridáva**. Ak má akcia podžáner aj rodiča a názov rodiča je obsiahnutý v názve podžánru (`doom-metal` + `metal`), rodič sa zo štítkov odstráni; inak ostane, ak ho AI našla (`trap` + `hip-hop`).
8. `alternative` AI ako štítok **nedáva** (len zastrešenie vo filtri). `rock` ako štítok len pri nejednoznačnom rocku; konkrétny podžáner má prednosť (`classic-rock` pre „dad rock“).
9. Pri kultúre sú zastrešením filmových a scénických žánrov podtypy (`film`, `theatre`, `dance`); scénické žánre comedy, stand-up a performance sa nezavádzajú (duplikovali by podtypy).
10. **(2026-11-19, Matej, úloha 078)** Pri podtype `talk` sú žánre `slam-poetry` (slam poetry, poetry slam), `reading` (autorské čítanie), `book-launch` (krst knihy), `lecture` (prednáška), `discussion` (diskusia, debata, panel); zastrešením je podtyp `talk` (ako pri filme a divadle, C9). Dáva ich len pipeline podľa schválených slovných spojení (`data/genre_aliases.json`, nie samotné slová; samotné „slam“ nie) v názve, popise akcie a uloženom prieskume, a len akciám s typom `talk`; iná akcia ich nemá.

## D. Cena
1. Len cena **výslovne uvedená pri tejto akcii a dátume**, so zdrojom; AI cenu pipeline overí otvorením zdrojovej stránky. Cena zo stránky podniku má prednosť.
2. Štruktúra `price {min, max, currency, kind}`; zobrazenie podľa jazyka appky bez ďalšieho textu: `350 Kč` · rozpätie `250–350 Kč` (zľavnená, predpredaj/na mieste, BASIC/VIP) · `od 950 Kč` · `20 €` · Zdarma · Dobrovoľné vstupné · Zdarma, rezervácia.

## E. Čas
Len výslovne uvedený pri akcii; inak prázdny. Nikdy neodhadovať. **(2026-11-22, Matej, task 090)** Happy hour, akcia na drinky alebo otváracie hodiny („happy hour od 17:00 do 22:00“) nie sú čas začiatku – spomenú sa v popise.

## F. Popis
Približne 5 viet; dĺžka podľa interpreta: pri veľkej hviezde môže byť dlhší, pri undergroundovom interpretovi s málom informácií kratší (2026-11-17, Matej). Vecne a do hĺbky (kto, odkiaľ, čím je známy, čo vydal, čo je na večeri zvláštne), **bez reklamných fráz a pátosu**, bez výkričníkov a emoji, cena, čas a miesto môžu byť spomenuté v kontexte, ak nie sú jedinou informáciou a popis sa okolo nich netočí (2026-11-17, Matej; bez poistky, nejde na kontrolu). Žánre ako názvy („techno“, nie „technové“). Len fakty zo zdrojov; z pôvodného textu fakty, nie vety. CZ hlavný, SK a EN preklad. Vzor: popis Allt v úlohe 054 časť 4b.
**(2026-11-17, Matej) Popis prezentuje informácie, nikdy ich nedostatok.** Žiadne vety o tom, čo sa nenašlo, nie je známe, nebolo zverejnené alebo ohlásené („o účinkujících se nedochovaly další podrobnosti“, „konkrétní účinkující nejsou zveřejněni“, „sedmé jméno zatím ohlášeno nebylo“), ani o tom, ako AI hľadala (rovnaké meno u iných interpretov). Málo informácií = kratší popis; nič = žiadny popis (pravidlo H). **Keď AI akciu sama označí na kontrolu (`needs_review`), popis sa neukladá** (2026-11-17, Matej: výplň a dohady nemajú hodnotu).

## G. Interpreti a Spotify
Mená všetkých účinkujúcich. **Spotify AI nehľadá** (zmena 2026-11-17, Matej): odkazy na Spotify dopĺňa len hlavný chat ručne do `data/manual.json` (ID z kworb.net, overené na `open.spotify.com/artist/<ID>`). Odkaz na Spotify z AI sa neukladá.

## H. Neistota
Keď AI nič nenájde (napr. REVO: Z Gumy Do Gumy), nechaj prázdne a označ „na kontrolu“. Nič nehádať.
