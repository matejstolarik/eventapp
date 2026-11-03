# 012: Archa+ a Forum Karlín (+ otázky z 011)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-03. Podklady z prieskumu (úloha 008, `tests/fixtures/survey/`). Oba sú Matejove prioritné podniky, typ `html` s vlastným parserom.

### Archa+
- Program: https://archa-plus.cz/cz/program/ (bloky `program-item`, `performance-date`, `performance-title`, `tags-tickets`; ISO dátum a čas).
- Štítky na webe (napr. „tanec“, „EN friendly“) ulož do `sources[].section` len ak zodpovedajú sekcii programu; inak ich len zaloguj do reportu (poslúžia pri zatriedení v úlohe 013). Nič neprekladaj na naše formáty, to je úloha 013.
- `ticket_url` len ak odkaz „Vstupenky“ vedie na predaj lístkov.
- Ak Archa+ uvádza akcie v iných priestoroch (ako Akropolis), rovnaké pravidlo: akcie mimo vlastných priestorov vyraď a zaloguj.

### Forum Karlín
- Program: https://forumkarlin.cz/program/ (WordPress, bloky s triedou `event`; podľa prieskumu je názov v `alt` obrázka, to je krehké – hľadaj, či je názov aj v texte alebo odkaze).
- Výpis nemá čas: dosťahuj čas z detailu akcie ako pri Čitárni (rešpektuj `max_requests`, `timeout_secs`). Ak detail uvádza „otevření“/„dveře“ a „začátek“ oddelene, použi `doors_time` a `start_time` podľa dátového modelu.

### Otázky z kontroly úlohy 011
1. Akropolis: report 011 uvádza „27 vyradených pre externé priestory“, v behu 2026-11-02 to bolo 8. Rozpíš, z akých dôvodov sa akcie Akropolisu vyraďujú (cudzia sála / mimo okna / iné) s počtami. Ak je cudzích sál naozaj 27, vypíš ich zoznam, mohlo sa niečo zmeniť na webe alebo v porovnávaní názvov sál (napr. „Jazz Bar“ vs „Jazz bar“).
2. Fuchs2: z 23 akcií sa 2 odfiltrovali – ktoré a prečo?
3. Fuchs2 sitemap: filter `lastmod >= dnes - 90 dní` môže vynechať budúcu akciu, ktorej stránka vznikla skôr a odvtedy sa nemenila (napr. festival zverejnený v lete). Zmeraj, koľko URL by pribudlo pri 365 dňoch a koľko z nich sú budúce akcie. Ak to nepresiahne rozumný počet požiadaviek (približne 150 za beh), okno rozšír; inak navrhni iné riešenie.
4. Fuchs2 a Bike Jesus majú rovnaké súradnice (ostrov Štvanice). Je to pravda podľa OSM, ok; len to poznač do `status.md` pre PWA (body na mape sa prekryjú).

### Spoločné
- Záznamy v `venues.json`: IG Archa+ `_archaplus_`, Forum Karlín `forum_karlin`; `ra_url` Archa+ https://ra.co/clubs/266130, Forum Karlín https://ra.co/clubs/91332; adresa z webu podniku (URL) a súradnice z overiteľného zdroja. Štítky prázdne.
- Fixtures, testy, pipeline, `status.md`, čísla cez `scripts/stats.py`, overenie 3 akcií na podnik voči webu (URL, dátum, čas).

## Report
