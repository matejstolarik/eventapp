# 003: Poradie práce, Akropolis mimo vlastných sál, stav lístkov

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02. Pôvodné zadanie 003 (rozsah v1, fázy vydania) bolo zapracované už v úlohe 001, preto je toto zadanie prepísané pred odovzdaním. Začni až po prečítaní tohto súboru, potom úloha 004.

### 1. Poradie práce (rozhodnutie Mateja 2026-11-02)
V `docs/project.md` (Poradie práce) a ako nový riadok v `docs/decisions.md`:
1–2 hotové; 3 adaptéry pre súčasné podniky (hotové: Cross, MeetFactory, Kasárna, Čitárna, Akropolis); 4 denný beh + GitHub Pages; 5 test LLM extrakcie nad HTML (Twist, Akropolis ako kontrola) → rozhodnutie vlastné parsery vs. LLM; 6 ďalšie podniky pred PWA, ale len tie, ktoré pôjdu rýchlo (zložité parsery na mieru až po PWA); 7 zatriedenie akcií aspoň podľa sekcie zdroja (bez neho je predvolený pohľad `live` + `dj` prázdny); 8 minimálna PWA.
Dôvod: Matej chce mať v appke od začiatku čo najviac podnikov, ak sa dajú pridať rýchlo.

### 2. Akropolis: akcie mimo vlastných priestorov
Akropolis vo výpise uvádza aj akcie, ktoré organizuje inde (v events.json: ARCHA+, Roxy, Planetárium Praha, Jazz Dock, Kostel sv. Šimona a Judy, Bike Jesus, DIVADLO HYBERNIA). Teraz majú `venue_id` = `palac-akropolis`, takže appka by ukázala napr. Modeselektor „v Akropolise“, hoci je v Roxy. V reporte 002 sú chybne označené ako „externé sály z MeetFactory/Kasárna“.
- Zoznam vlastných priestorov Akropolisu daj do konfigurácie zdroja v `venues.json` (zatiaľ Velký sál, Malá scéna, Jazz bar; over na webe, či nemá ďalšie vlastné priestory).
- Akcie s inou sálou vyraď a zaloguj (nie sú to akcie tohto podniku; Archa+ a Bike Jesus budú mať vlastné zdroje). Rozhodnutie zapíš do `decisions.md`.
- Ak by akcia nemala sálu vôbec, nechaj ju (ide pravdepodobne o Akropolis) a zaloguj.

### 3. Akropolis: význam kódov stavu lístkov (`/pub/vstupne_6`)
Kódy `no` (1, 11 = predaj; 2 = vypredané; 5 = zrušené) sú odvodené z neverejného endpointu.
- Do komentára adaptéra a do reportu napíš, odkiaľ je význam každého kódu (napr. z JS webu, ktorý kód mapuje na text tlačidla), a ktoré kódy si overil na konkrétnej akcii. Vypredané je overené na SPITFIRE COMPANY ►DVACETJEDNA 2026-11-02 (web: „Vyprodáno!“).
- `status = cancelled` nastav len pre kód, ktorého význam je overený z webu. Ak nie je, kód 5 ber ako neznámy (`sold_out = null`, `status = scheduled`) a zaloguj.
- Uveď, aké kódy majú 2 akcie so `sold_out = null` (KIIŌTŌ 2027-03-12, SPITFIRE ►KONEC ČLOVĚKA?! 2027-02-22) a čo je pri nich na webe.
- Over, kam vedie tlačidlo „Kup teď!“ na webe. `ticket_url` má byť ten istý cieľ. Ak je to stránka na webe Akropolisu s predajom (nie detail akcie), je to v poriadku; napíš, čo tam je.

### 4. Reporty
- Hash commitu v reporte musí byť finálny hash na `origin/main` (reporty 001 a 002 uvádzajú `966b4da`, na GitHube je `af8cb04`). Do `docs/tasks/README.md` dopíš: hash zapisuj po pushi; ak sa pri rebase zmení, oprav ho v ďalšom commite.
- Časť „Otvorené“ nesmie byť „nič“, ak sú známe obmedzenia (napr. 2 akcie bez stavu lístkov). Dopíš to do README ako pravidlo.

## Report
