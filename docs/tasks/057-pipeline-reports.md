# 057: Upozornenia a týždenný report pipeline cez GitHub Issues

## Zadanie

**Robí sa po 056.** **Schválené Matejom 2026-11-17:** kanál GitHub Issues (notifikácie cez appku GitHub / e-mail), týždenný report v pondelok ráno.

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
5. **AI:** hľadania a cena za týždeň a za mesiac / limit.
- **Každý bod má krátke ID** (napr. `W47-03`), aby naň Matej mohol odkazovať.
- Pravidlá reportu (prahy, čo hlásiť, ignorované body) v **`docs/report-rules.md`** + `data/report_ignore.json` (ID typu `venue:pole` alebo `event_id`, ktoré sa už nehlásia). Hlavný chat ich bude upravovať podľa Matejových hodnotení.
- Report uzavrie predošlý týždenný issue.

### 4. Overenie
- Testy (pytest) na výpočet upozornení a reportu z fixtúrnych `run_summary`.
- Ručne: `workflow_dispatch` týždenného reportu → issue vznikne (odkaz do reportu); simulované upozornenie (napr. testovací prepínač, ktorý nasimuluje 0 akcií jedného zdroja) → issue s `alert` vznikne a pri ďalšom normálnom behu sa zavrie. Testovacie issues po overení zavri.
- Text prvého reportu skopíruj do reportu úlohy (na Matejovo hodnotenie).
