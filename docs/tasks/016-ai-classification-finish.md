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
