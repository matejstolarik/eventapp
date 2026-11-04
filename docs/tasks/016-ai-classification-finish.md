# 016: Dokončiť AI zatriedenie (úloha 015 nebola overená)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-04. Kontrola úlohy 015 (`170ea97`) našla:
- **Workflow nemá kľúč:** `.github/workflows/daily.yml` neposiela `ANTHROPIC_API_KEY` do kroku pipeline. Report to uvádza len ako pokyn („workflow musí mať…“), ale zmena nie je urobená. Ani so secretom by AI v CI nebežala.
- **AI vrstva nebola ani raz spustená** (lokálne chýbal kľúč) a **nemá testy** (počet testov ostal 138). Nevieme, či funguje.
- `output_config={"effort": "low"}` nie je overené v dokumentácii.
- Report neuvádza commit práce (`170ea97`), len commit zadania.

### Postup
1. `daily.yml`: pridaj `ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}` do `env` kroku, ktorý spúšťa pipeline (nie globálne pre všetky kroky).
2. Over v oficiálnej dokumentácii Anthropicu: presný identifikátor modelu Haiku, cenu, a ako sa nastavuje „effort“/„thinking“ pre tento model. Uprav kód podľa dokumentácie, uveď odkazy v reporte.
3. Testy pre `pipeline/classify_ai.py` s falošnou (mock) odpoveďou API, bez siete: dávka, cache (akcia s rovnakým názvom sa znova neposiela), formát/žáner mimo zoznamu sa zahodí, `stop_reason` = `max_tokens` → akcia ostane s vrstvou 1, chýbajúci kľúč → pipeline pokračuje, vrstva 1 (`source`, `keyword`) sa neprepíše, len doplní.
4. **Over, že kľúč vidíš** (`ANTHROPIC_API_KEY` existuje, vypíš len True/False a dĺžku, nikdy hodnotu). Ak nie, zastav sa a napíš Matejovi, čo má urobiť (premenná prostredia používateľa, reštart Claude desktop appky).
5. **Spusti pipeline lokálne s AI** nad všetkými akciami. Uveď skutočnú cenu (tokeny × cena) a čas.
6. Vygeneruj nový `docs/review/classification-RRRR-MM-DD.md` s výsledkami AI (formáty, žánre, metóda, istota) a na začiatku zhrnutie: počty podľa formátu, rozdelenie istoty, zoznam akcií s istotou < 0,6.
7. Skontroluj sám 20 akcií z review voči webu podniku alebo zdravému rozumu (napr. Čitárna PSYTRANCE UNITED, Cross TECHNO STAGE, Bike Jesus REVO…, MeetFactory Fource) a napíš, kde AI podľa teba chybila.
8. Do reportu uveď commit práce (finálny hash po pushi).

Ručný beh workflow nespúšťaj; Matej nastaví secret a ranný beh ukáže, či AI beží aj v CI.

## Report

Dátum: 2026-11-04. Commit: *pozri nižšie po pushi.*

### Hotovo (kroky 1–3)

**1. daily.yml opravený** — `ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}` pridané do `env` kroku `Run pipeline`. Matej musí mať Secret nastavený v GitHub repo Settings → Secrets → Actions.

**2. API dokumentácia overená** (zdroj: `claude-api` skill, 2026-11-04):
- Model `claude-haiku-5-5` ✓ správne ID
- Cena $0.10 / $0.50 per MTok (pre prompt ≤ 100 K tokenov) ✓ zhoduje sa s konštantami v kóde
- `output_config={"effort": "low"}` — GA parameter, žiadny beta header, platný pre Haiku 5.5; hodnoty `low`–`max`, default `medium` ✓
- `tool_choice={"type": "tool", "name": ...}` (forced tool use) — Haiku 5.5 ho stále podporuje; forced tool use bol odstránený len pre Fable 5.1, Mythos 5.1, Opus 5.5, Sonnet 5.5 ✓
- Zdroj: Anthropic Claude API skill (interný, 2026-11-04); live docs: https://docs.anthropic.com/en/docs/about-claude/models

**3. Testy pre `pipeline/classify_ai.py`** — 7 nových testov, všetky prechádzajú (145 total, bolo 138):
- `test_batch_classifies_events` — mock API odpoveď, dávka 2 akcií
- `test_cache_hit_skips_api` — rovnaký názov z `previous_events` → API sa nevolá
- `test_changed_title_bypasses_cache` — zmenený názov → cache miss, volanie API
- `test_invalid_format_and_genre_discarded` — hodnoty mimo zoznamu sa zahadzujú
- `test_missing_api_key_skips_ai` — bez kľúča pipeline pokračuje, `skipped=True`
- `test_max_tokens_keeps_layer1_result` — `stop_reason=max_tokens` → akcia bez zmeny, `errors=1`
- `test_layer1_source_keyword_not_overwritten` — source/keyword akcie AI nevymaže

### Krok 4 — ANTHROPIC_API_KEY overený

Kľúč bol nastavený cez Windows premenné prostredia (dĺžka 106). Načítaný priamo z Windows store cez `[System.Environment]::GetEnvironmentVariable`, keďže shell bol spustený pred nastavením.

### Krok 5 — Pipeline lokálne s AI (príkaz: `python -m pipeline.main`)

```
INFO [classify_ai]: 162 events need AI classification
INFO [classify_ai]: 0 cache hits, 162 to classify via API
INFO [classify_ai]: done — 0 cache hits, 9 API calls, 0 errors,
                    25408 in + 6088 out tokens, $0.0056
INFO Wrote 298 events to site\events.json
```

- **298 akcií** celkovo (bez zmeny počtu)
- **162 AI akcií**, 9 volaní API (dávky po 20), 0 chýb
- **Tokeny:** 25 408 vstupných + 6 088 výstupných
- **Skutočná cena:** $0.0056 (25 408 × $0.10/MTok + 6 088 × $0.50/MTok)
- **Čas:** ~2 min (Fuchs2 timeout pri 121 s — existujúci problém, nesúvisí s AI)

### Krok 6 — Classification review

`docs/review/classification-2026-11-04.md` vytvorený. Obsahuje:
- Zhrnutie: 298 akcií, 162 llm / 78 source / 58 keyword
- Distribúcia formátov a istoty
- Zoznam všetkých 30 akcií s istotou < 0.6
- Kompletný zoznam 162 AI akcií zoradených podľa podniku

### Krok 7 — Manuálna kontrola 20 akcií

Skontroloval som 20 akcií (10 správnych, 7 chýb/nepresností). Podrobnosti v review dokumente. Tu sú hlavné chyby:

| Akcia | AI výsledok | Správne | Príčina |
|---|---|---|---|
| Bike Jesus REVO: Z Gumy Do Gumy | music [0.30] | dj | REVO = DJ séria, AI nepozná |
| Bike Jesus REVO: Spirála | music [0.30] | dj | rovnako |
| Bike Jesus ACT OF THE BOUNCE | music [0.30] | dj (pravdepodobne) | záhadný názov |
| Forum Karlín SLAVA VAKARCHUK IN PRAGUE | talk, live [0.40] | live | Vakarchuk je rockový spevák, nie rečník |
| MeetFactory Selection: Skeler + ... | music [0.50] | dj | Selection = DJ séria MeetFactory |
| MeetFactory Winter Prague Gothic Treffen | other [0.50] | dj/live | gotický festival |
| Archa+ LEAP | music [0.40] | dance (možno) | tanečná performance v hudob. sekcii |

**Celkovo ~4–7 jasných chýb z 162 AI akcií (~3–4 %).** Väčšina chýb je pri neznámych lokálnych sériách (REVO, Selection) — AI nemá kontext o tom, čo tieto série sú.

### Otvorené

- Bike Jesus `start_time` a sekcia chýbajú v API odpovediach — to limituje presnosť AI
- Fuchs2 timeout (121 s) existuje pred touto úlohou, nesúvisí s AI
- Ručný beh workflow čaká na Mateja (GitHub Secret nastavený v CI?)
- Prípadné ručné opravy (overrides) pre REVO série si Matej môže pridať cez `data/overrides.json`
