# Classification review — 2026-11-04

Beh: workflow_dispatch 2026-11-04 15:43 UTC, commit c4bc2de.
Celkovo: **305 akcií**, z toho **167 cez AI (Claude Haiku 5.5)**, cena **$0.0057**.

## Súhrn formátov

| Format | Count | % |
|---|---|---|
| live | 165 | 54 % |
| theatre | 60 | 20 % |
| dj | 43 | 14 % |
| music | 19 | 6 % |
| dance | 10 | 3 % |
| talk | 6 | 2 % |
| workshop | 4 | 1 % |
| other | 3 | <1 % |
| opening | 2 | <1 % |
| comedy | 1 | <1 % |
| film | 1 | <1 % |
| quiz | 1 | <1 % |

## Súhrn metód

| Method | Count |
|---|---|
| source | 78 |
| keyword | 60 |
| llm | 167 |

## Poznámky

- `music` (19) — akcie, ktoré AI nedokázala zaradiť presnejšie; väčšinou akcie bez sekcie, bez kľúčových slov a s nejednoznačným názvom.
- `theatre` (60) — prevažne Archa+ (63 akcií, z toho väčšina divadlo/tanec/talk) a Palác Akropolis.
- `live` (165) — dominantný formát; zahŕňa koncerty zo všetkých podnikov.
- Vrstva 1 `source` (78): akcie so sekciou (`hudba`, `divadlo`, atď.) priamo z adaptéra.
- Vrstva 1 `keyword` (60): detegované kľúčové slová v názve (`live`, `křest`, `tour`, `rave`, atď.).
- AI `llm` (167): 9 dávok × ~18 akcií, 0 chýb po oprave `.strip()` na API kľúči.

## Otvorené otázky

- 19 akcií s `music` — zvážiť rozšírenie kľúčových slov alebo lepší kontext do AI promptu.
- Kasárna Karlín má len 2 akcie — sezónny podnik (outdoor, leto); nízky počet je očakávaný.
