# Pravidlá upozornení a týždenného reportu (task 057)

Kanál: GitHub Issues v repe (notifikácie cez appku GitHub / e-mail). Žiadna nová služba ani kľúč, workflow používa `GITHUB_TOKEN` (`permissions: issues: write`).
Podklad: denné zhrnutia behu `data/cache/run_summaries/` (formát v `docs/data-model.md`, „Zhrnutie denného behu“).
Toto je jediné miesto s pravidlami; prahy sú konštanty na začiatku `pipeline/alerts.py` a `pipeline/weekly_report.py` (pri zmene upraviť aj tu).
Hlavný chat pravidlá a ignorovaný zoznam upravuje podľa Matejových hodnotení.

## Ignorované body (`data/report_ignore.json`)

`{"ignore": [{"id": "…", "note": "prečo, dátum"}]}`. Tvary `id`:

| id | čo sa už nehlási |
|---|---|
| `<venue>:<pole>` (pole `image`, `time`, `price`, `genre`, `description`) | chýbajúce údaje podniku (report, časť 3) |
| `<event_id>` | akcia v častiach 4 a 6 reportu |
| `genre:<názov>` | návrh žánru (časť 5) |
| `<venue>:source` | upozornenia aj stav reportu pre všetky zdroje podniku |
| `<venue>/<label zdroja>` | upozornenie pre jeden zdroj |

## Okamžité upozornenia (issue so štítkom `alert`)

Spúšťa ich krok `Alerts` na konci `daily.yml` a `deploy-app.yml` (vždy, aj pri zlyhaní).

| kľúč | kedy | zavrie sa |
|---|---|---|
| `workflow:daily`, `workflow:deploy-app` | job skončil inak ako `success` | ďalší úspešný beh toho istého workflowu |
| `source:<venue>/<label>` | zdroj vrátil 0 akcií (aj chyba zdroja), alebo menej ako **50 %** mediánu posledných **7** behov (presne polovica nie je pokles) | ďalší denný beh, v ktorom problém nie je |
| `ai:limit` | HTTP 402 od AI, minutý mesačný limit hľadaní, alebo mesačná cena AI ≥ rozpočet (3 $) − 0,005 $ | ďalší denný beh bez toho |

- Kľúč je v tele issue (`<!-- alert-key: … -->`). Kým je issue s kľúčom otvorené, opakovaný problém pridá komentár „Stále trvá“, nové issue nevznikne.
- Denný beh zatvára len kľúče `workflow:daily`, `source:*`, `ai:*`; `deploy-app` len `workflow:deploy-app`.
- Denný rozpočet behu (0,30 $) nie je upozornenie, je to bežné zastavenie.
- Test: `workflow_dispatch` denného behu so vstupom `simulate_zero_source = <venue_id>` – zdroje podniku sa v zhrnutí zapíšu s 0 akciami (dáta sa nemenia).
