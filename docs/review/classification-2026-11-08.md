# Klasifikácia — 2026-11-08

Generované z `site/events.json` po behu pipeline (úloha 019).

Príkaz: `python -m pipeline.main` (lokálny beh, bez `ANTHROPIC_API_KEY` → AI vrstva preskočená)

## Súhrn

| Metóda | Počet |
|--------|-------|
| source | — |
| keyword | — |
| llm | 0 (AI preskočená lokálne) |
| ∅ (neklasifikované) | — |

| Formát | Počet |
|--------|-------|
| concert | 72 |
| dj | 29 |
| music | 170 |
| dance | 9 |
| theatre | 59 |
| talk | 4 |
| workshop | 4 |
| opening | 2 |
| other | 2 |
| quiz | 1 |
| **party** | 0 (AI preskočená) |

**Poznámka:** `party` = 0 lokálne pretože AI vrstva 2 bola preskočená (bez `ANTHROPIC_API_KEY`). V GitHub Actions s API kľúčom bude `party` pridaný kde vhodné (keyword + AI vrstva 2).

## Nové podniky

### ROXY (42 akcií)

| Dátum | Čas | Titul | Formát | Sekcia (hashtag) | Zdroj URL |
|-------|-----|-------|--------|-----------------|-----------|
| 2026-11-08 | 20:00 | PLATINA | concert | concert | https://www.roxy.cz/events/detail/5183/platina |
| 2026-11-10 | 20:00 | OHM SQUARE 30 | concert | concert | https://www.roxy.cz/events/detail/5067/ohm-square-30 |
| 2026-11-11 | 19:30 | BRATŘI | concert | concert | https://www.roxy.cz/events/detail/4743/bratri |
| 2026-11-13 | 23:00 | AGENTS OF TIME | dj | dj | https://www.roxy.cz/events/detail/4999/agents-of-time |

Hashtag mapovanie funguje: `#concert` → `concert`, `#dj` → `dj`. Prípadné `#party` → `['dj','party']` sa overí pri ďalšom behu s API kľúčom.

### EPIC Prague (23 akcií)

| Dátum | Čas | Titul | Formát | Zdroj URL |
|-------|-----|-------|--------|-----------|
| 2026-11-08 | 22:00 | SUNDAY RITUALS - REGGAETON & LATINO | music → dj+party (AI) | https://www.epicprague.com/program/2253/sunday-rituals-reggaeton-latin |
| 2026-11-11 | 22:00 | WINTER BREAK | music → dj+party (AI) | https://www.epicprague.com/program/2293/winter-break |
| 2026-11-13 | 22:00 | LET IT ROLL pres. PENDULUM (DJ SET) | dj | https://www.epicprague.com/program/2263/let-it-roll-pres-pendulum-dj-set |

Keyword `DJ SET` v titule → `dj` (layer 1). Ostatné akcie zostávajú `music` → AI vrstva 2 bude klasifikovať pri ďalšom behu.

## Otvorené

- `party` formát pre existujúce akcie: retroaktívne pridanie bude pri ďalšom CI behu (s API kľúčom).
- EPIC akcie bez keywords: AI vrstva 2 pri ďalšom CI behu ich klasifikuje na `dj+party` / `dj` / `other` podľa titulov.
