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

Dátum: 2026-11-02. Commit: `4bc0034` (Task 003: work order, Akropolis external rooms, vstupne codes, report rules).

### Čo je hotové

**1. Poradie práce** — `docs/project.md` sekcia „Poradie práce" aktualizovaná: krok 3 označený ako hotový, pridané kroky 6 (ďalšie podniky pred PWA) a 7 (zatriedenie akcií), PWA presunutá na krok 8. Nový riadok v `decisions.md` (2026-11-02) nahrádza riadok 2026-10-31.

**2. Akropolis: akcie mimo vlastných priestorov** — Zoznam vlastných priestorov pridaný do `data/venues.json` → `sources[0].own_rooms: ["Velký sál", "Malá scéna", "Jazz bar"]`. Adaptér (`pipeline/adapters/html_akropolis.py`) filtruje akcie s inou sálou a loguje ich. Po pushi pipeline vyradila 8 externých akcií (ARCHA+, Roxy, Planetárium Praha×2, Jazz Dock, Kostel sv. Šimona a Judy, Bike Jesus, DIVADLO HYBERNIA×2). Rozhodnutie v `decisions.md` 2026-11-02. Vlastné priestory overené cez navigačnú lištu stránky (Velký sál, Malá scéna, Jazz Bar).

**3. Akropolis: kódy vstupne_6** — Pridané podrobné komentáre s mapovaním kódov a ich zdrojom. Zdroj: `data` atribút `.kas_box6` HTML elementov (čiarkovaný reťazec, index = kód): 0=nyní neprodáváme, 1=KUP TEĎ! (Akropolis), 2=VYPRODÁNO!, 3=VSTUP VOLNÝ!, 4=JIŽ BRZY…!, 5=ZRUŠENO!, 6=PŘELOŽENO! ►, 7=s rezervací VSTUP VOLNÝ!, 9=prodej ukončen, 10=prodej na místě, 11=KUP TEĎ! (externý URL). Overenie: kód 2 = „VYPRODÁNO!" (SPITFIRE DVACETJEDNA 2026-11-02), kód 5 = „ZRUŠENO!" (data atribút). Kód 11 opravený: `ticket_url` teraz používa externý URL z `vstupne_6` (napr. goout.net, narodni-divadlo.cz). Kódy 3, 4, 6 explicitne ošetrené (log, sold_out=null). Kód 3 (voľný vstup): `free=True, sold_out=False`. Rozhodnutie v `decisions.md` 2026-11-02.

**2 akcie so sold_out=null pred úpravou:** KIIŌTŌ/UK+MONIKA NAČEVA (2027-03-12, ext_id=41514) a SPITFIRE COMPANY ►KONEC ČLOVĚKA?! (2027-02-22, ext_id=41323). Oba mali vstupne kód **4** = „JIŽ BRZY…!" (lístky ešte nie sú v predaji). Overené na webe: https://palacakropolis.cz/work/33298?event_id=41514&...&page_id=33824 a event_id=41323 zobrazovali text „JIŽ BRZY...". Po novom: KIIŌTŌ vyradená (Jazz Dock = externá sála); SPITFIRE KONEC zostáva (Velký sál, kód 4 → `sold_out=null` správne).

**ticket_url (kód 1):** tlačidlo „KUP TEĎ!" na webe vedie na `/work/33298?event_id=...&page_id=42027` = interný formulár na kúpu vstupenky na palacakropolis.cz. Adaptér generuje rovnaký cieľ → v poriadku.

**4. Reporty README** — Pridané do `docs/tasks/README.md`: pravidlo pre commit hash (finálny po pushi, nie pred pushom) a pravidlo pre sekciu „Otvorené" (nesmie byť „nič" ak sú obmedzenia). Rozhodnutie v `decisions.md` 2026-11-02.

### Čísla (z `site/events.json` po pipeline run 2026-11-02)

Príkaz: `python "C:\...\check4.py"` (pozri scratchpad) a pipeline log.

| Metrika | Hodnota |
|---|---|
| Akropolis eventov pred (posledný run) | 91 |
| Akropolis eventov po (tento run) | 83 |
| Vyradené externé akcie | 8 |
| Celkovo eventov (všetky podniky) | 159 |
| Akropolis sold_out=True | 7 |
| Akropolis sold_out=False | 75 |
| Akropolis sold_out=null | 1 |
| Akropolis cancelled | 0 |
| Akropolis vlastné sály | Velký sál (75), Malá scéna (4), Jazz bar (4) |

### Verifikácia z webu

- Filtrované externé akcie: pipeline log 2026-11-02 ukazuje 8 skip správ (ARCHA+, Roxy, Planetárium×2, Jazz Dock, Kostel, Bike Jesus, DIVADLO HYBERNIA×2)
- Kód 4 (JIŽ BRZY…!): overené na https://palacakropolis.cz/work/33298?event_id=41514&genre=1&no=62&page_id=33824 (KIIŌTŌ) a event_id=41323 (SPITFIRE KONEC)
- Kód 2 (VYPRODÁNO!): overené na SPITFIRE DVACETJEDNA 2026-11-02 (per zadanie)
- Kód 5 (ZRUŠENO!): overené cez `.kas_box6[data]` atribút (index 5 v reťazci)
- Kód 11 externý URL: FLAMENGO → goout.net, LATERNA MAGIKA → vstupenky.narodni-divadlo.cz
- ticket_url (kód 1): https://palacakropolis.cz/work/33298?event_id=40205&genre=1&no=62&page_id=42027 zobrazuje formulár „KOUPIT VSTUPENKU"
- Vlastné priestory Akropolisu: Velký sál, Malá scéna, Jazz Bar (navigácia na palacakropolis.cz)

### Otvorené

- Kód 6 (PŘELOŽENO! ►): event_id=41773 v `vstupne_6`. Adaptér loguje warning a ponecháva `status=scheduled`. Aktuálny stav na webe neoverený (event neidentifikovaný v events.json — možno mimo časového okna).
- Kód 3 (VSTUP VOLNÝ!): žiadny živý príklad v aktuálnom `vstupne_6`, logika pridaná ale neotestovaná na reálnych dátach.
- Kód 9, 10: v `vstupne_6` sa nevyskytujú — nie sú ošetrené (padnú do „unknown code" warning).
- Testy Akropolis neoverujú novú logiku filtrovania `own_rooms` (fixtures nemajú nastavený `own_rooms` v source config — to je správne správanie, filtruje len ak je `own_rooms` nastavený).
