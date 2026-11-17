# 065: Žánre podľa schválenia, hierarchia ako dáta, stand-up, popis pri needs_review

## Zadanie

**Schválené Matejom 2026-11-17** (vedľajší chat „žánre“ + hlavný chat). **ZMENA 2026-11-17 (Matej, pred spustením): 065 ide pred 064.** `psytrance` a `reggaeton` ako samostatné žánre (pôvodne 064 časť 4) robí táto úloha: zrušiť mapovanie `psytrance → trance` a `reggaeton → latin`, pridať oba do zoznamu, varianty `psy trance`, `psychedelic trance` → `psytrance`. Zobrazenie hierarchie vo filtri, zlúčené čipy a podtypy ako čipy **nie sú súčasťou** – prídu s návrhom Filtra.

**Čítaj:** `docs/ai-rules.md` B6, C (nové C7–C9), F, H; `docs/tasks/062/genres-review.md`; `data/genre_aliases.json`; zoznamy žánrov v `docs/data-model.md` (`genres`, `film_genres`, `stage_genres`); `pipeline/ai_guards.py` (poistka žánrov, aliasy, české tvary); `pipeline/genres_review.py`; v appke preklady žánrov a podtypov (`web/src/i18n/*`), mapovanie ikon typov.

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`. Zmena dátového modelu je schválená týmto zadaním (nové žánre, `stand-up`, `genre_hierarchy.json`) – zapíš ju do `data-model.md`.

### 1. Zoznam žánrov a mapovania
**Nové žánre – hudba** (rodič v zátvorke; rodič musí byť tiež v zozname):
- `hard-techno` (techno); `breakbeat`; `jungle`; `synthwave`; `grime`
- `trap`, `drill` (hip-hop); `afro` (zastrešujúci); `afrobeats` (afro); `dub`; `dancehall`
- `alternative-rock`, `noise-rock`, `post-rock`, `grunge`, `gothic-rock` (rock aj alternative); `classic-rock`, `garage-rock` (rock)
- `emo`, `post-hardcore`, `noise` (alternative); existujúce `indie`, `post-punk`, `shoegaze`, `slowcore`, `dream-pop`, `darkwave` dostanú rodiča alternative
- `pop-punk`, `dance-punk`, `noise-punk` (punk); `doom-metal`, `sludge-metal`, `stoner-metal` (metal)
- `hyperpop`, `dance-pop`, `alt-pop` (pop); `soul`, `neo-soul` (soul)
- `classical`, `orchestral`, `soundtrack`, `country`, `chanson`
- `psytrance` (trance), `reggaeton` (latin)
- `alternative` = len zastrešenie vo filtri (v hierarchii, nie ako štítok; poistka ho ako štítok zahodí)

**Nové žánre – film** (rodič `film`): action, adventure, animation, biography, comedy, crime, documentary, drama, family, fantasy, history, horror, music, musical, mystery, romance, sci-fi, short, thriller, war, western, experimental, queer, cult-classic (kultové a legendárne filmy), arthouse (nezávislé, nízkorozpočtové, umelecké).

**Nové žánre – scéna:** pod `theatre`: drama, musical, opera, puppet-theatre, improv, cabaret, new-circus (physical-theatre existuje); pod `dance`: contemporary-dance, ballet, dance-theatre. Rovnaký názov vo filme aj na scéne (drama, musical, experimental) = jeden žáner s viacerými rodičmi.

**Mapovania (`genre_aliases.json`):** hard techno, hardtechno → hard-techno; breaks → breakbeat; raggajungle → jungle; ragga → dancehall; acid house, booty house → house; **afro house → house + afro**; afro-fusion → afro; hardcore rave → rave; alt. rock → alternative-rock; noise rock → noise-rock; folk-rock → folk + rock; **doom metal → doom-metal (samotné „doom“ sa nemapuje**, Matej 2026-11-17 – string band Freshwater Dogs); sludge, sludge metal → sludge-metal; stoner metal → stoner-metal; emo-rap → hip-hop; indie pop → indie + pop; electropop → pop + electronic; glitch pop → pop; šanson → chanson; současný tanec → contemporary-dance.

**Zahodení kandidáti** (ignorovať, nenavrhovať znova; `data/genre_ignored.json` alebo podobne): alternative (ako štítok), tekno, uptempo, acid, ghetto-tech, deconstructed club, idm, witch house, jump-up, neurofunk, jersey club, miami bass, booty bass, ballroom, bounce, rub-a-dub, flamenco, digicore, dixieland, swing, twist, rock'n'roll, trampská píseň, ploužák, valčík, old-time, drone, sound art, bigbeat, educational narrative adventure game, road movie, parodie na horory a sitcomy, postpunkový dokument; cabaret ako hudobný žáner (scénický ostáva).

**Hierarchia:** `data/genre_hierarchy.json` (`{žáner: [rodičia]}`), test konzistencie (každý rodič existuje, žiadne cykly).

**Pravidlo C7 v kóde:** podžáner + rodič, ktorého názov je obsiahnutý v názve podžánru → rodič sa zo štítkov odstráni (`doom-metal` + `metal` → `doom-metal`); inak ostáva. Test.

**Poistka (`ai_guards`):** české a anglické tvary pre nové žánre (napr. „kultovní“, „artový“, „činohra“, „loutkové“, „současný tanec“, „balet“, „dokumentární“, „animovaný“, „horor“, „černobílý“ → nič, nie je žáner). Testy na niekoľkých.

**Kontroly (do reportu):**
- `jazz` je v zozname, a predsa v `genres-review.md` medzi kandidátmi s `maps_to: null` – nájdi príčinu a oprav.
- Kandidát sa v `genres-review.md` ukáže až od 2 akcií (návrh Matej).
- „educational narrative adventure game“ mal zlý druh (`music`) – príčina.
- VLTAVA – STO LET S VÁMI vytvorila 8 kandidátov – prečo (C3?).
- Po zmene: zoznam akcií, ktoré ostali bez žánru, hoci predtým žáner mali.

### 2. Podtyp `comedy` → `stand-up`
- Premenovať formát kultúry `comedy` na `stand-up` všade: `data-model.md`, klasifikácia (kľúčové slová), prompt (B6 je už zmenené), `manual.json`, cache/uložené výsledky pri aplikácii (starý `comedy` sa pri čítaní premení), appka (preklady CZ/SK/EN „Stand-up“, farba a **ikona mikrofónu ostávajú**), `docs/design.md` (len názov). Filmový žáner `comedy` je iná vec (pole `genres`).
- Test: akcia s `formats: [comedy]` z cache → `stand-up`; TANTEHORSE ►IRIS (2026-12-01) má po behu `stand-up`.

### 3. Popis pri `needs_review` od modelu (ai-rules F, H)
- Keď model akciu sám označí `needs_review`, AI popis sa neukladá (CZ, SK, EN). Platí pre nové aj existujúce akcie (REVO: Z Gumy Do Gumy). Test.
- Cena a čas v popise ostávajú povolené (bez poistky) – nemeniť.

### 4. Test proti poškodenému kódovaniu v appke
- Chyba „Â·“ v `EventPanel.tsx` (z `61aa01c`, opravené v `5d2e21d`). Pridaj test (vitest alebo skript v `npm test`), ktorý v `web/src` nájde typické poškodené sekvencie (`Â`, `Ã`, `â€`) a zlyhá. Ak vieš z histórie zistiť, prečo vznikla (nástroj/kódovanie pri zápise), napíš to.

### Aplikácia na existujúce dáta
- Najprv bez API: znova aplikovať mapovania a hierarchiu na uložené surové žánre/kandidátov. Rozhodnutie z uloženého prieskumu len kde to inak nejde. **Rozpočet najviac 0,10 $** (kredit ~0,41 $), bez nového hľadania.

## Overenie a report
- `pytest -q`, `npm test`, `npm run build`; číslo behu a nasadenia.
- Čísla z `events.json` posledného behu (príkaz): akcie so žánrom, počet použitých žánrov, top 20 žánrov, akcie bez žánru (pred/po), `stand-up` akcie, popisy odstránené kvôli `needs_review`, nový `genres-review.md` (len kandidáti ≥ 2 akcie), cena, zostatok kreditu.
- Ručne over 3 akcie so zmeneným žánrom na webe (Omah Lay → `afrobeats`/`afro`? – ak bola zrušená, iná akcia).
- Otvorené body.

## Report

**Dátum:** 2026-11-18. **Commity:** `94f997d` (časť 1), `6f54fc5` (časť 2), `01cd989` (časť 3), `58eb222` (časť 4), report v nasledujúcom commite. **Beh:** Daily pipeline [44198194551](https://github.com/matejstolarik/eventapp/actions/runs/44198194551) (workflow_dispatch, `ai_budget_usd=0.10`), testy, build aj nasadenie na Pages úspešné; `events.json` generated_at `2026-11-18T00:25:40+01:00`. Lokálne: `pytest -q` 491 passed, `npm test` (kontrola kódovania + 199 vitest) ok, `npm run build` ok.

**Stav: časti 2, 3, 4 sú hotové a overené v nasadení. Časť 1 je v kóde hotová, ale na existujúce dáta sa v behu NEaplikovala.** Beh nenačítal uložený prieskum (`research store: 0 records loaded`) a publikovaný `research/2026-11.json` sa tým zmenšil z 243 záznamov na 1 (podrobne nižšie, otvorený bod 1). Čakám na rozhodnutie Mateja.

### Čo je hotové
1. **Žánre** (`94f997d`): nové hudobné, filmové a scénické žánre (`pipeline/genres.py`, `data-model.md`), `psytrance` a `reggaeton` samostatné, mapovania v `data/genre_aliases.json` („doom“ sa nemapuje), `data/genre_hierarchy.json` + test konzistencie (každý rodič existuje, žiadne cykly), `data/genre_ignored.json` (zahodení kandidáti; `cabaret` len ako hudobný žáner), pravidlo C7 a zahodenie štítku `alternative` (`finalize_genres`, pri validácii aj na konci behu pre všetky zdroje), C7–C9 v prompte, české a anglické tvary v poistke (kmene `*`: kultovn*, artov*, cinohr*, loutkov*, „současný tanec“, balet*, dokumentarn*, animovan*, horor; „černobílý“ nie je žáner – test). `genres_review`: kandidáti len od 2 akcií, bez zahodených a už schválených. Nové: `remap_stored_genres` – pri každom behu znova namapuje uložené surové názvy akcií z cache podľa aktuálnych zoznamov, bez API (potrebuje záznam prieskumu).
2. **`comedy` → `stand-up`** (`6f54fc5`): kľúčové slová, prompt, platné formáty, odpovede AI, `primary_format` z prieskumu, `manual.json`, načítanie predchádzajúceho behu (`_migrate_event`), výstup; appka (kód `stand-up`, ikona mikrofónu aj farba ostávajú, štítok „stand-up“), `design.md` (len názov). Test `tests/test_standup_065.py`.
3. **Popis pri `needs_review` od modelu** (`01cd989`): pri novom výsledku sa popis neuloží a preklad sa nevolá; akcie z cache s `run.needs_review` popis stratia. Cena a čas sa nemenia. Test `tests/test_review_desc_065.py`.
4. **Kódovanie** (`58eb222`): `web/scripts/check-encoding.mjs` beží v `npm test` pred vitestom. Je to skript, nie vitest test, lebo test s `node:fs` neprejde cez `tsc -b` (web nemá `@types/node`). Overené, že zlyhá na súbore s „ Â· “. Našiel ešte 3 poškodené `aria-label` v `EventPanel.tsx` (`VybranÃ¡ akcia`, `OtvoriÅ¥ akciu`, `Å tÃ­tky akcie`), opravené. Príčina: `61aa01c` uložil celý `EventPanel.tsx` prečítaný ako Windows-1252 (zdvojené sú všetky ne-ASCII znaky toho súboru, ostatné súbory commitu sú v poriadku). Zodpovedá to skriptovanej úprave cez Windows PowerShell 5.1 (`Get-Content` bez `-Encoding`); s istotou sa to z histórie určiť nedá.

### Kontroly zo zadania
- **`jazz` s `maps_to: null`:** Jazzmánie je `talk`, takže `own_kind = None`, `map_genre` sa nevolal a každý surový žáner skončil ako kandidát `kind: music, maps_to: null`. Opravené: pri akcii bez hudobného, filmového či scénického typu sa žáner zo zoznamu berie ako hudobný a nenamapovaný názov nie je kandidát. Rovnaká príčina je pri **„educational narrative adventure game“** (akcia `talk, other`, zlý druh `music`).
- **VLTAVA – STO LET S VÁMI (8 kandidátov):** nejde o porušenie C3. Prieskum (krok 1) našiel zdroj s výpisom štýlov kapely („genres: rock, cabaret, swing, trampská píseň, blues, reggae, dixieland, twist, rock'n'roll [11][13][15]“; v druhom termíne „jazz, folk, chanson, cabaret … swing, trampská písnička, twist“). Žánre zo zoznamu prešli poistkou (rock, blues, reggae / rock, jazz, folk), všetko ostatné išlo do kandidátov, ktoré nemajú poistku ani limit. Teraz sú zahodené alebo schválené (chanson).
- **Kandidát v `genres-review.md` až od 2 akcií:** hotové. Nový súbor `docs/tasks/065/genres-review.md` má **0 kandidátov a 0 navrhnutých mapovaní s ≥ 2 akciami**. S 1 akciou ostalo 8: slam poetry (stage), brass-house, klezmer, balkan brass, doom, crossover, nu-metal, campy konverzační komedie (stage).
- **Akcie, ktoré ostali bez žánru:** v nasadenom behu žiadna (žánre sa nezmenili, viď otvorený bod 1). V suchom behu na zálohe prieskumu tiež žiadna.

### Čísla (beh 44198194551)
Príkaz: `python numbers065.py docs/tasks/065/events-run44172530495.json site/events.json` (skript v scratchpade, porovná `genres`, `formats`, `descriptions`). „Pred“ je beh 44172530495, „po“ je `site/events.json` z artefaktu behu 44198194551.
- Akcie: 374 → 372; so žánrom 266 → 265; bez žánru 108 → 107; použitých žánrov 44 → 44; akcií so zmenenými žánrami: **0** (remap bez prieskumu nebežal).
- Top 20: rock 53, pop 41, electronic 40, indie 39, techno 37, hip-hop 35, house 35, folk 24, drum-and-bass 23, edm 20, metal 18, experimental 17, jazz 16, punk 12, post-punk 9, rnb 9, hardcore 7, world 7, trance 6, blues 6.
- `stand-up`: 1 akcia, TANTEHORSE ►IRIS (2026-12-01) `[stand-up, theatre, music]`, primary `stand-up`. `comedy` vo formátoch: 0.
- Popisy odstránené kvôli `needs_review`: **40** (log „cached AI description dropped“); akcií s `needs_review` a AI popisom: 0. Z tých 40 má **13 v popise názov podniku** (cross club, roxy, bike jesus, unijazz, epic prague). Ich `needs_review` mohlo nastaviť ešte pravidlo z 062 (podnik v popise, zrušené v 063), nie model; rozlíšiť sa to nedá (otvorený bod 2).
- Cena behu: AI doplnenie $0.0059 (1 nová akcia, 3 hľadania); rozpočet behu $0.10; mesiac pred behom $1.2880. Zostatok kreditu DeepSeek je odhad ~0,40 $ (0,41 $ − 0,006 $), cez API neoverený.

### Overenie na webe (`https://matejstolarik.github.io/eventapp/events.json`, generated_at 2026-11-18T00:25:40)
- TANTEHORSE ►IRIS: `formats [stand-up, theatre, music]`, `primary_format stand-up`.
- REVO: Z Gumy Do Gumy (bike-jesus-2026-11-20): bez popisu.
- Jazzmánie Vladimíra Kouřila #274: `genres [jazz]` (žáner podniku; z AI už nebude kandidátom).
- Omah Lay: `genres [rnb]`, nezmenené, lebo remap nebežal. Na zálohe prieskumu vychádza `[rnb, afrobeats]` (afro-fusion → `afro`, C7 ho pri `afrobeats` odstráni).
- Zmenené žánre na webe overiť nejde, žiadne sa nezmenili.

### Suchý beh remapu na zálohe (nie výsledok behu, len podklad na rozhodnutie)
Na `events.json` + `research/2026-11.json` behu 44172530495 by sa zmenili žánre 33 akcií a žiadna by neostala bez žánru. Napríklad: PSYTRANCE / PSYTRANCE UNITED `trance` → `psytrance`; TITI `techno` → `hard-techno`; High on Fire `metal, death-metal` → `death-metal, sludge-metal, stoner-metal`; SUNDAY RITUALS – AFRO HOUSE `house` → `house, afro`; ADÉLA `pop` → `dance-pop, electronic, hyperpop`; Chelsea Wolfe + `doom-metal, gothic-rock`; REEAL TIME 3 (film) + `animation`; SPITFIRE COMPANY & PAST (theatre) + `musical`; THE MUSIC DIGEST (talk) `[]` → `folk, jazz, rock, funk`.

### Rozhodnutia urobené samostatne (v `docs/decisions.md`)
`experimental` nemá rodiča a je aj v `stage_genres`; existujúce podžánre (`tech-house`, `death-metal`, `metalcore`, …) nedostali rodiča; podžáner v poistke maskuje rodiča („hard techno“ nie je opora pre `techno`, „alt. rock“ nie pre `rock`); `slug()` bez diakritiky; remap uložených žánrov pri každom behu (keď kandidát nemá vlastný citát, berú sa citáty celej akcie; skôr overené a nezmenené žánre sa znova nekontrolujú); štítok „stand-up“ malými písmenami; české a slovenské názvy filmových a scénických žánrov v appke (hudobné ostávajú kódom); kontrola kódovania ako skript.

### Otvorené body (na rozhodnutie Mateja)
1. **Uložený prieskum sa stratil z Pages.** Beh načítal 0 záznamov bez varovania (Pages pre `research/2026-11.json` vrátil 404 alebo chybu; lokálne som 2026-11-17 večer dostával HTTP 503, kým `events.json` fungoval) a zapísal späť len 1 nový záznam. Posledná úplná kópia (243 záznamov) je v `docs/tasks/065/research-2026-11-run44172530495.json` (z artefaktu Pages behu 44172530495, ten čoskoro expiruje). Bez nej nefunguje remap žánrov, `ENRICH_FROM_RESEARCH` ani `fill_primary_from_research`. Návrh: (a) obnoviť z tejto zálohy (napr. jednorazovo načítať zo súboru v repozitári, keď Pages záznamy nemá) a (b) aby sa to neopakovalo, držať `site/research` aj v `actions/cache` (ako náhľady obrázkov) a logovať varovanie, keď chýba mesiac, ktorý predchádzajúci beh mal. Ide o zmenu uloženia dát, preto som ju bez súhlasu nespravil.
2. **13 popisov je možno odstránených neprávom** (`needs_review` mohlo pochádzať z pravidla 062 o podniku v popise). Popisy sú v `docs/tasks/065/events-run44172530495.json`. Dajú sa obnoviť (napr. cez `manual.json` alebo jednorazovo z cache), alebo nechať tak. Zoznam: cross-club-2026-11-22-sundej-se-sunday, cross-club-2026-11-30-los-tekkenos, citarna-unijazz-2026-12-15-vanocni-vecirek-giboni, bike-jesus-2026-11-20-revo-z-gumy-do-gumy (tu Matej popis výslovne nechce), bike-jesus-2026-11-26-feverdream, bike-jesus-2026-11-27-revo-sour-room, bike-jesus-2026-11-27-wellwet-residents-secret-guest-de, roxy-2026-11-20-drum-bass-pilates, roxy-2026-11-27-techno-pilates-s-dj-hound, roxy-2026-12-30-nye-warm-up, roxy-2026-12-31-new-years-eve-2026-gold-rush, roxy-2027-01-01-the-opening-party-2027, epic-2026-12-06-sunday-rituals-mainstream-music.
3. Po obnove prieskumu treba nový beh, čísla žánrov (pred/po, akcie bez žánru) a ručné overenie 3 zmenených akcií na webe. Táto časť reportu ešte chýba.
4. Rodičia pre existujúce podžánre (`tech-house` → house, `death-metal`/`metalcore` → metal, …): zadanie ich nemenovalo.
