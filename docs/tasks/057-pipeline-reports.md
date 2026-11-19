# 057: Upozornenia a týždenný report pipeline cez GitHub Issues

## Zadanie

**Robí sa po 060.** **Schválené Matejom 2026-11-17:** kanál GitHub Issues (notifikácie cez appku GitHub / e-mail), týždenný report v pondelok ráno.

**Čítaj:** `.github/workflows/daily.yml`; `pipeline/main.py` (kde vzniká job summary a riadok „New events“); `pipeline/checks.py`; `docs/data-model.md` časť Quality checks (`grep -n "Quality" docs/data-model.md`); `data/overrides.json` (formát).

Zistenie hlavného chatu: upozornenie pri zlyhaní denného behu dnes neexistuje (úloha 020 riešila niečo iné).

Každá časť vlastný commit. Žiadna nová služba ani kľúč; použi `GITHUB_TOKEN` workflowu (`permissions: issues: write`).

### 1. Denné čísla behu
Každý denný beh uloží zhrnutie `run_summary.json` (do cache medzi behmi, napr. `data/cache/run_summaries/`, posledných ~60 dní): čas, úspech, po podnikoch: počet akcií, nové, zmiznuté, chyby/varovania zdroja, počty chýbajúcich polí (obrázok, čas, cena, žáner pri hudbe, popis), AI: hľadania, cena, zmeny typu, nič nenájdené, zahodené ceny, `primary_format` s nízkou istotou.

### 2. Okamžité upozornenie (issue so štítkom `alert`)
Len pri:
- zlyhaní denného behu alebo nasadenia (krok `if: failure()`),
- zdroji s 0 akciami alebo s poklesom o > 50 % oproti mediánu posledných 7 behov,
- minutí mesačného limitu hľadaní alebo kreditu AI (HTTP 402).
- Rovnaký problém neotvára nové issue, kým je staré otvorené (pridá komentár). Keď zmizne, beh issue zavrie s komentárom.

### 3. Týždenný report (issue so štítkom `weekly-report`, pondelok ~7:00 Praha)
Nový workflow s cron (a `workflow_dispatch` na test), číta `run_summaries` za posledných 7 dní. **Jedna obrazovka v telefóne**, po slovensky:
1. **Stav:** „Všetko v poriadku“ alebo 1–3 najdôležitejšie problémy navrchu.
2. **Podniky** (tabuľka): akcie spolu, nové za týždeň, trend oproti minulému týždňu, varovania.
3. **Chýbajúce údaje** len tam, kde je podnik výrazne horší ako jeho bežný stav alebo > 30 % akcií bez poľa.
4. **Na kontrolu** (najviac 10, s odkazom na zdroj a na akciu v appke): AI nič nenašla, nízka istota typu, zahodená cena, zmena typu AI.
5. **Návrhy nových žánrov** (z `data/genre_proposals.json`, len ≥ 3 akcie): názov, typ, počet, 2–3 príklady s odkazom; Matej odpovie schváliť / zlúčiť s X / zamietnuť.
6. **Na doplnenie v chate** (hlavný chat to číta z issue): hlavní interpreti nových koncertov/DJ nocí bez Spotify odkazu (meno, akcia, odkaz); akcie s cenou `verified: false` v najbližších 14 dňoch; akcie „na kontrolu“ (nič nenájdené, nízka istota typu, zahodené žánre).
7. **AI:** hľadania a cena za týždeň a za mesiac / limit.
- **Každý bod má krátke ID** (napr. `W47-03`), aby naň Matej mohol odkazovať.
- Pravidlá reportu (prahy, čo hlásiť, ignorované body) v **`docs/report-rules.md`** + `data/report_ignore.json` (ID typu `venue:pole` alebo `event_id`, ktoré sa už nehlásia). Hlavný chat ich bude upravovať podľa Matejových hodnotení.
- Report uzavrie predošlý týždenný issue.

### 4. Overenie
- Testy (pytest) na výpočet upozornení a reportu z fixtúrnych `run_summary`.
- Ručne: `workflow_dispatch` týždenného reportu → issue vznikne (odkaz do reportu); simulované upozornenie (napr. testovací prepínač, ktorý nasimuluje 0 akcií jedného zdroja) → issue s `alert` vznikne a pri ďalšom normálnom behu sa zavrie. Testovacie issues po overení zavri.
- Text prvého reportu skopíruj do reportu úlohy (na Matejovo hodnotenie).

## Report

**2026-11-19** · commity `41dd999` (časť 1), `4cf7be0` (časť 2), `24bdadc` + `cce58e3` (časť 3), report v ďalšom commite.

### Hotovo
1. **Denné čísla** – `pipeline/run_summary.py`: po každom behu `data/cache/run_summaries/<YYYY-MM-DD>.json` (60 dní, cache Actions). Po podnikoch: akcie, nové, zmiznuté, zdroje (počet + varovanie), chýbajúce polia (obrázok, čas, cena, žáner pri hudbe, popis). AI: hľadania, cena, mesiac/limit, zmeny typu (`enrich_ai` teraz zapisuje aj id + starý/nový typ), nič nenájdené, zahodené ceny, nízka istota typu (< 0,6). Plus zoznamy pre report (na kontrolu, bez Spotify, neoverené ceny 14 dní, návrhy žánrov). Formát v `docs/data-model.md` („Zhrnutie denného behu“).
2. **Upozornenia** – `pipeline/alerts.py` + `pipeline/github_issues.py`, krok `Alerts` (`if: always()`) v `daily.yml` a `deploy-app.yml`, `permissions: issues: write`. Zlyhaný beh/nasadenie, zdroj 0 akcií alebo < 50 % mediánu 7 behov, HTTP 402 / limit hľadaní / mesačný rozpočet AI. Otvorené issue s rovnakým kľúčom dostane komentár, po vyriešení sa zavrie s komentárom. Testovací prepínač: vstup `simulate_zero_source`.
3. **Týždenný report** – `pipeline/weekly_report.py`, `.github/workflows/weekly-report.yml` (pondelok 05:43 UTC = 6:43 Praha v zime, + `workflow_dispatch`), časti 1–7, ID `W<týždeň>-NN`, zatvorí predošlý report. Pravidlá: `docs/report-rules.md`, ignorované: `data/report_ignore.json` (zatiaľ prázdny).
4. **Testy** – `tests/test_run_report.py` (13 testov: zhrnutie, upozornenia vrátane otvor/komentuj/zavri, report, ignorovanie, zatvorenie predošlého reportu). Celé `pytest`: 642 passed.

### Rozhodnutia (samostatne)
- Zhrnutia v cache Actions, nie na Pages (`deploy-app` by ich zmazal) – riziko: GitHub zmaže cache nepoužitú 7 dní; denný beh ju používa každý deň.
- Upozornenie pri 0 akciách sa hlási aj bez histórie; presne polovica mediánu nie je „pokles o > 50 %“.
- Ignorovaný zoznam platí aj pre upozornenia zdrojov (`<venue>:source`, `<venue>/<label>`); návrh žánru sa ignoruje ako `genre:<názov>`.
- Časť 6 je zbalená (`<details>`) a časť 3 ukáže 8 riadkov, zvyšok zbalený – kvôli „jednej obrazovke“.
- Čas reportu 05:43 UTC (mimo celej hodiny, po dennom behu), takže v lete 7:43.
- Zápis do `docs/decisions.md` (2026-11-19).

### Čísla
Posledný beh pipeline: run 44424531413, `generated_at` 2026-11-19T01:03:06+01:00. Príkaz:
`python -c "import json,collections;d=json.load(open('site/events.json',encoding='utf-8'));E=d['events'];print(d['generated_at'],len(E));print(dict(sorted(collections.Counter(e['venue_id'] for e in E).items())))"`
(po `curl -s https://matejstolarik.github.io/eventapp/events.json -o site/events.json`)
- 373 akcií: archa-plus 58, bike-jesus 26, citarna-unijazz 15, cross-club 15, epic 36, forum-karlin 24, fuchs2 21, kasarna-karlin 13, meetfactory 35, palac-akropolis 85, roxy 45. Nové v tomto behu: 0.

### Overenie
- Simulované upozornenie: run 44422913807 so `simulate_zero_source=cross-club` → https://github.com/matejstolarik/eventapp/issues/1 „⚠ Zdroj cross-club/rss: 0 akcií“ (štítok `alert`). Ďalší normálny beh 44424531413 ho zavrel s komentárom „Vyriešené (2026-11-19): problém sa v tomto behu neopakoval.“
- Týždenný report: `workflow_dispatch` run 44424527080 → https://github.com/matejstolarik/eventapp/issues/2 (štítok `weekly-report`); po overení zavretý. Obe testovacie issues sú zavreté.
- Neoverené naživo: upozornenie pri zlyhaní workflowu, pri 402/limite a uzavretie predošlého týždenného reportu (pokryté testami).

### Text prvého reportu (na Matejovo hodnotenie)
Report vznikol hneď po simulovanom behu, preto je v ňom 1 beh, „chýbajú čísla z 6 dní“ a cross-club s 0 akciami (simulácia).

## Týždenný report W47 (13. 11. – 19. 11. 2026)

### 1. Stav
- **W47-01** Chýbajú čísla z 6 dní (beh neprebehol alebo sa nezapísal).
- **W47-02** Zdroj `cross-club/rss` dal v poslednom behu 0 akcií.

### 2. Podniky

| Podnik | Akcie | Nové | Trend | Varovania |
|---|--:|--:|--:|---|
| archa-plus | 58 | 0 | – |  |
| bike-jesus | 26 | 1 | – |  |
| citarna-unijazz | 15 | 0 | – |  |
| cross-club | 15 | 1 | – | 1× zdroj |
| epic | 36 | 0 | – |  |
| forum-karlin | 24 | 0 | – |  |
| fuchs2 | 21 | 0 | – |  |
| kasarna-karlin | 13 | 0 | – |  |
| meetfactory | 35 | 0 | – |  |
| palac-akropolis | 85 | 0 | – |  |
| roxy | 45 | 0 | – |  |
| **spolu** | **373** | **2** | – | |

### 3. Chýbajúce údaje

- **W47-03** `bike-jesus:image` obrázok chýba 100 % (26/26)
- **W47-04** `forum-karlin:price` cena chýba 96 % (23/24)
- **W47-05** `palac-akropolis:price` cena chýba 87 % (74/85)
- **W47-06** `archa-plus:price` cena chýba 86 % (50/58)
- **W47-07** `kasarna-karlin:price` cena chýba 85 % (11/13)
- **W47-08** `fuchs2:price` cena chýba 81 % (17/21)
- **W47-09** `bike-jesus:price` cena chýba 73 % (19/26)
- **W47-10** `citarna-unijazz:image` obrázok chýba 53 % (8/15)

<details><summary>ďalšie (6)</summary>

- **W47-11** `bike-jesus:description` popis chýba 46 % (12/26)
- **W47-12** `bike-jesus:time` čas chýba 46 % (12/26)
- **W47-13** `meetfactory:time` čas chýba 46 % (16/35)
- **W47-14** `cross-club:price` cena chýba 40 % (6/15)
- **W47-15** `fuchs2:description` popis chýba 38 % (8/21)
- **W47-16** `citarna-unijazz:price` cena chýba 33 % (5/15)

</details>

### 4. Na kontrolu

- **W47-17** nízka istota typu (music 0.2): [REVO: Z Gumy Do Gumy](https://matejstolarik.github.io/eventapp/#/akcia/bike-jesus-2026-11-20-revo-z-gumy-do-gumy) · bike-jesus · 2026-11-20 · [zdroj](https://bikejesus.com)
- **W47-18** nízka istota typu (dj 0.4): [FEVERDREAM](https://matejstolarik.github.io/eventapp/#/akcia/bike-jesus-2026-11-26-feverdream) · bike-jesus · 2026-11-26 · [zdroj](https://bikejesus.com)
- **W47-19** nízka istota typu (dj 0.5): [REVO: SOUR ROOM](https://matejstolarik.github.io/eventapp/#/akcia/bike-jesus-2026-11-27-revo-sour-room) · bike-jesus · 2026-11-27 · [zdroj](https://bikejesus.com)
- **W47-20** nízka istota typu (concert 0.45): [Podzemnická vánoční besídka](https://matejstolarik.github.io/eventapp/#/akcia/citarna-unijazz-2026-12-05-podzemnicka-vanocni-besidka) · citarna-unijazz · 2026-12-05 · [zdroj](https://citarna.unijazz.cz/events/podzemnicka-vanocni-besidka/)
- **W47-21** nízka istota typu (concert 0.55): [vánoční večírek DPvJU](https://matejstolarik.github.io/eventapp/#/akcia/citarna-unijazz-2026-12-11-vanocni-vecirek-dpvju) · citarna-unijazz · 2026-12-11 · [zdroj](https://citarna.unijazz.cz/events/vanocni-vecirek-dpvju/)
- **W47-22** nízka istota typu (dj 0.55): [NYE Warm Up](https://matejstolarik.github.io/eventapp/#/akcia/roxy-2026-12-30-nye-warm-up) · roxy · 2026-12-30 · [zdroj](https://www.roxy.cz/events/detail/5209/nye-warm-up)
- **W47-23** nízka istota typu (party 0.4): [NATTE VISSTICK](https://matejstolarik.github.io/eventapp/#/akcia/epic-2027-02-19-natte-visstick) · epic · 2027-02-19 · [zdroj](https://www.epicprague.com/program/2303/natte-visstick)
- **W47-24** nízka istota typu (concert 0.5): [Winter Prague Gothic Treffen](https://matejstolarik.github.io/eventapp/#/akcia/meetfactory-2027-02-27-winter-prague-gothic-treffen) · meetfactory · 2027-02-27 · [zdroj](http://www.meetfactory.cz/cs/program/detail/winter-prague-gothic-treffen)
- **W47-25** nízka istota typu (party 0.5): [ANDEREX x EXPROZ](https://matejstolarik.github.io/eventapp/#/akcia/epic-2027-02-27-anderex-x-exproz) · epic · 2027-02-27 · [zdroj](https://www.epicprague.com/program/2287/anderex-x-exproz)
- **W47-26** nízka istota typu (music 0.2): [Iluka](https://matejstolarik.github.io/eventapp/#/akcia/bike-jesus-2027-03-13-iluka) · bike-jesus · 2027-03-13 · [zdroj](https://bikejesus.com)
- … ďalších 1 v časti 6.

### 6. Na doplnenie v chate

<details><summary>Spotify 1 · neoverené ceny 2 · na kontrolu 11</summary>

**Interpreti bez Spotify (nové koncerty / DJ noci):**

- **W47-27** The Wilderness, VBPS — [VIANOČNÝ PUNK: THE WILDERNESS (SK) ✚ VBPS (SK) /live](https://matejstolarik.github.io/eventapp/#/akcia/bike-jesus-2026-12-17-vianocny-punk-the-wilderness-sk-vbps-sk-live) · bike-jesus · 2026-12-17 · [zdroj](https://bikejesus.com)

**Ceny `verified: false` v najbližších 14 dňoch:**

- **W47-28** 150 Kč — [DRUMSTATION](https://matejstolarik.github.io/eventapp/#/akcia/cross-club-2026-11-27-drumstation) · cross-club · 2026-11-27 · [zdroj](https://www.crossclub.cz/cs/program/8724-drumstation/) · [cena](https://goout.net/cs/drumstation-subzero%2Bmagenta%2Bdalsi/szpyuny/)
- **W47-29** od 600 Kč — [TROS SKETOS](https://matejstolarik.github.io/eventapp/#/akcia/palac-akropolis-2026-11-28-tros-sketos) · palac-akropolis · 2026-11-28 · [zdroj](https://palacakropolis.cz/work/33298?event_id=40554&genre=1&no=62&page_id=33824) · [cena](https://goout.net/uk/tros-sketos/szwujfy/)

**Na kontrolu (všetko):**

- **W47-30** nízka istota typu (concert 0.5): [Winter Prague Gothic Treffen](https://matejstolarik.github.io/eventapp/#/akcia/meetfactory-2027-02-27-winter-prague-gothic-treffen) · meetfactory · 2027-02-27 · [zdroj](http://www.meetfactory.cz/cs/program/detail/winter-prague-gothic-treffen)
- **W47-31** nízka istota typu (concert 0.45): [Podzemnická vánoční besídka](https://matejstolarik.github.io/eventapp/#/akcia/citarna-unijazz-2026-12-05-podzemnicka-vanocni-besidka) · citarna-unijazz · 2026-12-05 · [zdroj](https://citarna.unijazz.cz/events/podzemnicka-vanocni-besidka/)
- **W47-32** nízka istota typu (concert 0.55): [vánoční večírek DPvJU](https://matejstolarik.github.io/eventapp/#/akcia/citarna-unijazz-2026-12-11-vanocni-vecirek-dpvju) · citarna-unijazz · 2026-12-11 · [zdroj](https://citarna.unijazz.cz/events/vanocni-vecirek-dpvju/)
- **W47-33** nízka istota typu (music 0.2): [Iluka](https://matejstolarik.github.io/eventapp/#/akcia/bike-jesus-2027-03-13-iluka) · bike-jesus · 2027-03-13 · [zdroj](https://bikejesus.com)
- **W47-34** nízka istota typu (music 0.2): [REVO: Z Gumy Do Gumy](https://matejstolarik.github.io/eventapp/#/akcia/bike-jesus-2026-11-20-revo-z-gumy-do-gumy) · bike-jesus · 2026-11-20 · [zdroj](https://bikejesus.com)
- **W47-35** nízka istota typu (dj 0.4): [FEVERDREAM](https://matejstolarik.github.io/eventapp/#/akcia/bike-jesus-2026-11-26-feverdream) · bike-jesus · 2026-11-26 · [zdroj](https://bikejesus.com)
- **W47-36** nízka istota typu (dj 0.5): [REVO: SOUR ROOM](https://matejstolarik.github.io/eventapp/#/akcia/bike-jesus-2026-11-27-revo-sour-room) · bike-jesus · 2026-11-27 · [zdroj](https://bikejesus.com)
- **W47-37** AI nič nenašla: [Going Nowhere](https://matejstolarik.github.io/eventapp/#/akcia/archa-plus-2026-11-30-going-nowhere) · archa-plus · 2026-11-30 · [zdroj](https://archa-plus.cz/cz/program/detail/954/2026-11-30-going-nowhere)
- **W47-38** nízka istota typu (dj 0.55): [NYE Warm Up](https://matejstolarik.github.io/eventapp/#/akcia/roxy-2026-12-30-nye-warm-up) · roxy · 2026-12-30 · [zdroj](https://www.roxy.cz/events/detail/5209/nye-warm-up)
- **W47-39** nízka istota typu (party 0.4): [NATTE VISSTICK](https://matejstolarik.github.io/eventapp/#/akcia/epic-2027-02-19-natte-visstick) · epic · 2027-02-19 · [zdroj](https://www.epicprague.com/program/2303/natte-visstick)
- **W47-40** nízka istota typu (party 0.5): [ANDEREX x EXPROZ](https://matejstolarik.github.io/eventapp/#/akcia/epic-2027-02-27-anderex-x-exproz) · epic · 2027-02-27 · [zdroj](https://www.epicprague.com/program/2287/anderex-x-exproz)

</details>

### 7. AI

- Týždeň: 3 hľadaní, $0.00
- Mesiac 2026-11: $1.37 / $3.00, 994 / 3000 hľadaní

_Pravidlá: `docs/report-rules.md`, ignorované: `data/report_ignore.json`. Behov v týždni: 1._



### Otvorené
- Prvý report je dlhý: 14 riadkov chýbajúcich údajov (hlavne ceny 33–96 %, bike-jesus bez obrázkov) a 24 akcií s nízkou istotou typu. Treba doplniť `data/report_ignore.json` alebo upraviť prahy podľa Matejovho hodnotenia.
- Trend a „bežný stav“ chýbajúcich údajov budú zmysluplné až po týždni / dvoch zhrnutí.
- Cena AI za týždeň ukazuje /usr/bin/bash.00, pretože v testovacích behoch sa takmer nič nedopĺňalo (3 hľadania).
