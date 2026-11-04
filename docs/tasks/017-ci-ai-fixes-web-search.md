# 017: AI v CI, Fuchs2, presunuté akcie, oneskorenie behu

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-04 (pred odovzdaním: vyhľadávanie na webe presunuté do 018). Podklad: prvý plánovaný beh 41827290413 (2026-11-04).

### 1. AI v GitHub Actions zlyhala
V behu 41827290413 všetkých 8 dávok: `API call 1 failed: Connection error. — batch skipped` → 0 akcií zatriedených, zverejnený súbor je len s vrstvou 1. Lokálne to fungovalo.
- Zisti príčinu: loguj typ výnimky a príčinu (`exc.__cause__`), nie len text. Over, či secret v CI naozaj prichádza (len True/False a dĺžka), či nie je nastavená iná premenná (napr. base URL), či ide o výpadok API (status stránka Anthropicu pre daný čas).
- Pridaj opakovanie s rastúcim čakaním pri sieťových chybách a 429/5xx (napr. 3 pokusy). Oprav počítadlo v logu („API call 1“ pri každej dávke).
- Ak AI v behu zlyhá, akcie bez výsledku sa majú skúsiť znova v ďalšom behu (nesmú sa uložiť do cache ako hotové).
- Over ručným behom workflow (`workflow_dispatch`), že AI v CI prebehne. Uveď odkaz na beh a počty zo súhrnu.

### 2. Vyhľadávanie na webe
Presunuté do samostatnej úlohy 018 (Matej 2026-11-04, šetrenie kreditov). V tejto úlohe nerob.

### 3. Fuchs2 stráca akcie
Beh 41827290413: `source timeout 120s exceeded — stopping at 14 events` (lokálne 23). Sitemap s oknom 365 dní je ~180 požiadaviek. Zvýš `timeout_secs` pre Fuchs2 tak, aby stačil s rezervou (z GitHubu sú požiadavky pomalšie), alebo zníž počet požiadaviek bez straty budúcich akcií. Zdôvodni.

### 4. Presunuté a odložené akcie
Fuchs2 má akcie „POSTPONED: deBasement“ a „PŘESUNUTO DO MEETFACTORY / …“.
- Akcia presunutá do iného podniku: v pôvodnom podniku ju vyraď a zaloguj (v novom podniku je pod vlastným zdrojom).
- Odložená akcia bez nového dátumu: nový stav `postponed` (zmena dátového modelu, navrhnutá hlavným chatom; zapíš do `data-model.md` a `decisions.md`). Z názvu odstráň prefix („POSTPONED:“).
- Rozpoznávanie (EN/CZ/SK: postponed, odloženo, přesunuto, moved to…) v spoločnej normalizácii, nie len pre Fuchs2.

### 5. Ranný beh príde neskoro
Plánovaný beh na 04:17 UTC sa spustil o 12:12 UTC (oneskorenie 8 h). **Matej: jeden beh denne stačí, oneskorenie je v poriadku** (upravené pred odovzdaním, druhý beh sa nepridáva). Len do súhrnu behu zapíš oneskorenie oproti plánovanému času, aby bolo vidno, keby sa beh vynechal alebo chodil až večer.

### 6. Report
Commit práce (finálny hash), odkaz na ručný beh v CI, počty formátov po vrstve 2, cena AI v CI. Nový `docs/review/classification-RRRR-MM-DD.md`.

## Report
