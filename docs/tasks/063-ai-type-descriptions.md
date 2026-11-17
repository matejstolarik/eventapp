# 063: Typ od AI pred kategóriou podniku, popis bez „nedostatku informácií“

## Zadanie

**Schválené Matejom 2026-11-17** po reporte 062. Rozhodnutia: `docs/ai-rules.md` B7 (typ od AI má prednosť pred kategóriou podniku) a F (popis prezentuje informácie, nikdy ich nedostatok; miesto a sála v popise povolené).

**Čítaj:** `docs/ai-rules.md` B7, F, H; report 062 (Časť 1, Otvorené); `pipeline/classify.py` (riadky s `"method": "source"`), `pipeline/classify_ai.py` (podmienka `method in ("manual", "source", "keyword")`), `pipeline/enrich_ai.py` (aplikácia `formats` a `genres` podľa `method`), `pipeline/ai_guards.py`, `pipeline/deepseek.py`; `docs/decisions.md` (`grep -n "062"`).

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`.

### 1. Typ od AI má prednosť pred zdrojom
- Dnes typ zo zdroja (`classification.method: source`, kategória podniku, napr. Roxy) a `keyword` blokuje AI typ (062: 63 akcií, Tinlicker ostal `dj`). Nové poradie: `manual` > AI (`formats` + `primary_format`) > `source` > `keyword`. Typ zo zdroja ostáva ako záloha, keď AI nič nevráti (napr. pravidlo H, rozpočet, výpadok).
- Žánre: bez zmeny (žánre zo stránky podniku majú prednosť ako doteraz).
- Akcie z 60 dní, ktoré už AI spracovala: použi uložené AI výsledky alebo rozhodnutie z uloženého prieskumu (`reenrich_from_research`), **bez nového hľadania**. Vyplniť aj chýbajúci `primary_format` (062: 70 akcií).
- `classify_ai` (nové akcie): rovnaké poradie.
- Testy: Tinlicker (zdroj `dj`, AI `concert`) → `concert`, `dj` doplnkový; `manual` prebije AI; AI bez výsledku → typ zo zdroja.
- Do reportu tabuľka všetkých akcií, kde sa typ zmenil: názov, miesto, dátum, typ zo zdroja → typ od AI (na Matejovu kontrolu).

### 2. Popis bez viet o nedostatku informácií
- Prompt podľa nového F: žiadne vety o tom, čo sa nenašlo, nie je známe, nebolo zverejnené/ohlásené, ani o tom, ako AI hľadala.
- Poistka v kóde (CZ, pred prekladom): **vymazať jednotlivé vety** o chýbajúcich informáciách, nie celý popis. Ak po vymazaní neostane nič použiteľné, akcia AI popis nemá (pravidlo H, `needs_review`). Zapísať do `dropped` (druh `description_no_info`).
- Testy na skutočných vetách: DIVA INVITES („O jednotlivých účinkujících se kromě jejich jmen … nedochovaly další podrobnosti, stejně jako informace o vydaných nahrávkách“), Text-appeal („Konkrétní účinkující pro tento večer nejsou zveřejněni.“), „Sedmé jméno zatím ohlášeno nebylo.“, REVO (celý popis o tom, že meno majú iní nesúvisiaci interpreti → žiadny popis). **Falošné zachytenie nesmie nastať:** Bonobo „…takže jeho vystoupení nejsou postavená na laptopu…“ ostáva.
- Existujúce dáta: nájdi všetky AI popisy v `events.json` s takými vetami (zoznam do reportu: akcia + vymazaná veta), oprav ich z uloženého prieskumu bez hľadania a SK/EN prelož znova z opraveného CZ.

### 3. Miesto v popise nie je na kontrolu
- Odstrániť `needs_review` za podnik/sálu v popise (062: 48 akcií). Poistka môže ostať len ako počítadlo v logu.

### Rozpočet
- Bez nového hľadania; celkom najviac 0,10 $ (kredit ~0,46 $). Pri HTTP 402 stop, beh pokračuje.

## Overenie a report
- `pytest -q` OK; číslo behu (denný workflow s `reenrich_from_research` alebo nový vstup).
- Čísla z `events.json` posledného behu (príkaz): akcie so zmeneným typom (z čoho na čo, súhrn), s `primary_format`, `needs_review` (pred 85 → po, podľa dôvodu), opravené popisy, akcie bez AI popisu, cena behu, zostatok kreditu.
- Ručne over 3 akcie so zmeneným typom na webe podniku a 3 opravené popisy (pôvodná veta → nový text).
- Otvorené body.
