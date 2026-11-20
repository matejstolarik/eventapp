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
| `ai:limit` | HTTP 402 od AI, minutý mesačný limit hľadaní, alebo mesačná cena AI ≥ rozpočet (5 $ od task 085, predtým 3 $) − 0,005 $ | ďalší denný beh bez toho |
| `ai:low-credit` | zostatok kreditu DeepSeek < **0,20 $** (task 074) | denný beh so zisteným zostatkom ≥ 0,20 $ (pri nezistenom zostatku ostáva otvorené) |
| `venue-image:<venue>` | aktívne miesto nemá `image_url`, alebo sa jeho obrázok nepodarilo stiahnuť (`image_card` je `null`) (task 085) | denný beh, v ktorom miesto obrázok má |

- Kľúč je v tele issue (`<!-- alert-key: … -->`). Kým je issue s kľúčom otvorené, opakovaný problém pridá komentár „Stále trvá“, nové issue nevznikne.
- Denný beh zatvára len kľúče `workflow:daily`, `source:*`, `ai:limit`, `ai:low-credit` (to len pri zistenom zostatku), `venue-image:*` (len keď zhrnutie behu má pole `venue_images_missing`); `deploy-app` len `workflow:deploy-app`.
- Denný rozpočet behu (0,30 $) nie je upozornenie, je to bežné zastavenie.
- Test: `workflow_dispatch` denného behu so vstupom `simulate_zero_source = <venue_id>` – zdroje podniku sa v zhrnutí zapíšu s 0 akciami (dáta sa nemenia).

## Týždenný report (issue so štítkom `weekly-report`)

Workflow `weekly-report.yml`: pondelok 05:43 UTC (6:43 / 7:43 Praha, po dennom behu) a `workflow_dispatch`. Číta zhrnutia za posledných 7 dní (dnes − 6 … dnes), trend porovnáva s posledným zhrnutím týždňa predtým. Nový report zatvorí predošlý otvorený report. Každý bod má ID `W<týždeň ISO>-<poradie>` (napr. `W48-03`), čísluje sa zhora nadol.

1. **Stav** – „✅ Všetko v poriadku“ alebo najviac **3** problémy v tomto poradí: zlyhané behy v týždni; dni bez zhrnutia; zdroj s 0 akciami v poslednom behu; AI narazila na limit / HTTP 402; najviac 2 polia podniku výrazne horšie ako bežne (časť 3).
2. **Podniky** – akcie v poslednom behu, nové za týždeň (súčet `new`), trend = rozdiel akcií oproti poslednému behu minulého týždňa, varovania = počet zdrojových varovaní v týždni.
3. **Chýbajúce údaje** – pole podniku sa hlási, ak chýba pri **> 30 %** akcií, alebo je o **≥ 15 bodov** horšie ako bežný stav (medián podielu zo zhrnutí starších ako 7 dní). Podnik s menej ako **3** akciami (pri žánri hudobnými) sa neposudzuje. Zobrazí sa **8** riadkov (najprv „horšie ako bežne“, potom podľa podielu), ďalšie zbalené.
4. **Na kontrolu** – najviac **10**: zahodená cena → zmena typu AI → nízka istota typu (< 0,6) → AI nič nenašla; len akcie od dnes, unikátne za týždeň, odkaz do appky a na zdroj.
5. **Návrhy nových žánrov** – z posledného behu, **≥ 3** akcie, 3 príklady; Matej odpovie schváliť / zlúčiť s X / zamietnuť.
6. **Na doplnenie v chate** (zbalené, pre hlavný chat) – interpreti nových koncertov/DJ nocí bez Spotify (za týždeň), ceny `verified: false` v najbližších 14 dňoch (posledný beh), všetky body na kontrolu vrátane zahodených žánrov.
7. **AI** – hľadania a cena za týždeň; mesiac: cena / rozpočet, hľadania / limit (z posledného behu); zostatok DeepSeek z posledného behu, kde bol zistený (task 074).
