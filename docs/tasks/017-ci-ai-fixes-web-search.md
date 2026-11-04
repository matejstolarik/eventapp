# 017: AI v CI, vyhľadávanie na webe, Fuchs2, presunuté akcie, čas behu

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-04. Podklad: prvý plánovaný beh 41827290413 (2026-11-04).

### 1. AI v GitHub Actions zlyhala
V behu 41827290413 všetkých 8 dávok: `API call 1 failed: Connection error. — batch skipped` → 0 akcií zatriedených, zverejnený súbor je len s vrstvou 1. Lokálne to fungovalo.
- Zisti príčinu: loguj typ výnimky a príčinu (`exc.__cause__`), nie len text. Over, či secret v CI naozaj prichádza (len True/False a dĺžka), či nie je nastavená iná premenná (napr. base URL), či ide o výpadok API (status stránka Anthropicu pre daný čas).
- Pridaj opakovanie s rastúcim čakaním pri sieťových chybách a 429/5xx (napr. 3 pokusy). Oprav počítadlo v logu („API call 1“ pri každej dávke).
- Ak AI v behu zlyhá, akcie bez výsledku sa majú skúsiť znova v ďalšom behu (nesmú sa uložiť do cache ako hotové).
- Over ručným behom workflow (`workflow_dispatch`), že AI v CI prebehne. Uveď odkaz na beh a počty zo súhrnu.

### 2. Vyhľadávanie na webe pre neisté akcie (vrstva 3, odsúhlasené Matejom 2026-11-04)
- Len pre akcie, kde vrstva 2 vrátila istotu pod prahom (konfigurácia, začni 0,6) alebo len `music`.
- Použi nástroj na vyhľadávanie na webe v Anthropic API (over v oficiálnej dokumentácii názov nástroja, cenu za vyhľadávanie a limity; uveď odkazy). Obmedz počet vyhľadávaní na akciu (napr. 2) a na beh (konfigurácia).
- **Cache podľa interpreta** (normalizované meno): výsledok (je to kapela / DJ / iné, žánre, zdrojová URL) sa uloží a pri ďalšej akcii toho istého interpreta sa nehľadá. Kde uložiť cache medzi behmi (repo nie, beh nič necommituje), navrhni a zdôvodni; napr. ako súčasť zverejnených dát na Pages.
- K výsledku ulož URL, z ktorej AI vychádzala, a zobraz ju v súbore na kontrolu.
- Výsledky len z pevných zoznamov formátov a žánrov.
- Matej: „hlavne nech sú dáta kvalitné“ – kvalita má prednosť pred cenou, ale s limitmi, aby chyba nemohla minúť veľa peňazí. Uveď skutočnú cenu.

### 3. Fuchs2 stráca akcie
Beh 41827290413: `source timeout 120s exceeded — stopping at 14 events` (lokálne 23). Sitemap s oknom 365 dní je ~180 požiadaviek. Zvýš `timeout_secs` pre Fuchs2 tak, aby stačil s rezervou (z GitHubu sú požiadavky pomalšie), alebo zníž počet požiadaviek bez straty budúcich akcií. Zdôvodni.

### 4. Presunuté a odložené akcie
Fuchs2 má akcie „POSTPONED: deBasement“ a „PŘESUNUTO DO MEETFACTORY / …“.
- Akcia presunutá do iného podniku: v pôvodnom podniku ju vyraď a zaloguj (v novom podniku je pod vlastným zdrojom).
- Odložená akcia bez nového dátumu: nový stav `postponed` (zmena dátového modelu, navrhnutá hlavným chatom; zapíš do `data-model.md` a `decisions.md`). Z názvu odstráň prefix („POSTPONED:“).
- Rozpoznávanie (EN/CZ/SK: postponed, odloženo, přesunuto, moved to…) v spoločnej normalizácii, nie len pre Fuchs2.

### 5. Ranný beh príde neskoro
Plánovaný beh na 04:17 UTC sa spustil o **12:12 UTC** (oneskorenie 8 h). Pridaj druhý plánovaný čas (napr. popoludní, mimo celej hodiny), aby boli dáta čerstvé aj pri oneskorení. Vďaka cache AI to nezvyšuje cenu. Do súhrnu behu zapíš oneskorenie oproti plánovanému času.

### 6. Report
Commit práce (finálny hash), odkaz na ručný beh v CI, počty formátov po vrstve 2 a 3, počet vyhľadávaní a cena, zoznam akcií, ktorým vyhľadávanie zmenilo formát (pred → po, zdrojová URL). Nový `docs/review/classification-RRRR-MM-DD.md`.

## Report
