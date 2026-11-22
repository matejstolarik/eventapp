# 090: El Magico – celý mesiac z mesačného plagátu (DeepSeek s obrázkovým vstupom)

## Zadanie

**Schválené Matejom 2026-11-20 23:13 a 2026-11-22 12:48.** Nový typ zdroja (obrázok → text) – **Matej súhlasí**. Mení dáta → jeden beh pipeline na konci. **Spustiť po 089** (089 zavádza pravidlo mesačného limitu pri behoch z úloh). Postup pre `venues.json`, `first_loaded`, obrázok miesta, AI okno ako v 085/086/089. Čo nie je jasné, spýtaj sa.

**Čítaj:** report **083** (El Magico, sekcie „Dôležité zistenia“ a „El Magico – OCR“), `docs/tasks/083/elmagico/program-listopad-2026-el-magico.jpg` a **ručný referenčný prepis** `docs/tasks/083/elmagico/poster-reference-listopad-2026.md` (21 akcií), hárok El Magico v `docs/tasks/083/venue-survey.xlsx`, fixtures El Magico v `tests/fixtures/survey2/`, `docs/ai-rules.md` (typy), `pipeline/enrich_ai.py` (ako sa volá DeepSeek, limity, rozpočet).

### 1. Dva zdroje jedného miesta
- **HTML** `elmagico.cz/program/`: vždy 2 najbližšie akcie s detailom a plagátom (`hp-datum-akce`/`hp-mesic-akce`) – bežný adaptér.
- **Mesačný plagát:** `/wp-content/uploads/YYYY/MM/program-<mesiac>-YYYY-el-magico*.jpg` (názov nie vždy rovnaký: `-FINAL`, `-korekce-01`) – nájsť cez `/wp-json/wp/v2/media?…` (083) alebo odkaz zo stránky programu. Aktuálny aj nasledujúci mesiac, ak už je.

### 2. Čítanie plagátu cez DeepSeek
- **Model s podporou obrázkov over v oficiálnej dokumentácii** (api-docs.deepseek.com, sekcia Vision; podľa nej obrázky prijíma `deepseek-v4-flash-vision-exp`, iné zdroje uvádzajú podporu priamo v `deepseek-flash` od 9/2026). Použi ten, ktorý podľa docs funguje; zapíš do `docs/decisions.md` aj s URL. Žiadny nový kľúč ani platená služba navyše.
- Výstup: zoznam akcií (dátum, názov, prípadne čas – El Magico ho zvyčajne nemá) v pevnej JSON schéme. **Kontroly:** dátum v danom mesiaci; ak plagát uvádza deň v týždni, musí sedieť; pri neistote akciu nepridať (zalogovať). Nič nedomýšľať.
- **Plagát sa číta raz** (cache podľa URL/hash obrázka); nový/zmenený plagát = nové čítanie. Náklady zapíš (očakávané zlomky centu).
- **Test proti referenčnému prepisu novembra** (21 akcií): koľko akcií, dátumov a názvov model prečítal správne – tabuľka v reporte. Ak je presnosť zlá (napr. chybné dátumy), **zastav a napíš** pred zapojením do denného behu.

### 3. Akcie z plagátu vs. z webu
- Akcia z plagátu = jednoduchá akcia (názov, dátum, bez času, bez plagátu → obrázok miesta podľa pravidla 082). **Keď rovnaká akcia pribudne v HTML** (s plagátom a detailom), **nahradí tú z plagátu** – párovanie dátum + podobnosť názvu; v jeden deň môžu byť dve akcie (napr. kvíz a DJ), nespárovať nesprávnu. `id` a `first_seen` zostanú akcie z plagátu (nie je to nová akcia).
- Typy (Matej 2026-11-22): **turnaje a beer pong → párty, kvíz → kultúra / quiz**; ostatné určí AI ako pri iných miestach (doplniť do `docs/ai-rules.md` ako pravidlo pre tieto akcie, nie len pre El Magico).

### 4. Kontrola Matejom
- **Prvý mesiac skontroluje Matej:** v reporte tabuľka všetkých akcií z plagátu (dátum, názov, typ) vedľa plagátu; opravy pôjdu do `data/manual.json` (ako iné ručné opravy). Plagáty vyzerajú vždy rovnako – ďalej to má bežať samo.

### 5. Miesto vo `venues.json`
- El Magico, Chemická 953, Praha 4 – Chodov. Kapacita **300** (Matej). IG `elmagico_club`. Obrázok miesta: fotka 1000×667 z 083. Štítky: návrh s ukážkami akcií (Matej schvaľuje).

## Overenie a report
- `pytest -q` (hľadanie plagátu, schéma výstupu, kontroly dátumu, párovanie plagát ↔ HTML vrátane dvoch akcií v jeden deň, cache plagátu).
- Presnosť čítania novembrového plagátu proti referenčnému prepisu (tabuľka).
- **Jeden beh pipeline** (`ignore_monthly_cap` podľa 089). Počet akcií El Magico (z plagátu / z HTML / nahradených), cena čítania plagátu, AI doplnenie.
- Tabuľka akcií z plagátu na kontrolu Matejom; návrh štítkov.
