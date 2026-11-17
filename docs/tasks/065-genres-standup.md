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
