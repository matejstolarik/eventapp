# 006: Test extrakcie akcií z HTML pomocou LLM

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02. Jednorazový test, lokálne u Mateja. Denný beh ani `venues.json` sa nemenia.

Cieľ: zistiť, či LLM (Claude Haiku 5.5 cez Anthropic API) spoľahlivo vytiahne akcie z HTML programu podniku. Od výsledku závisí, či zvyšné podniky pridáme cez jeden LLM adaptér, alebo cez parsery na mieru.

### Kľúč a peniaze (platená služba, odsúhlasená Matejom 2026-11-02)
- Kľúč je v premennej prostredia `ANTHROPIC_API_KEY`. Najprv over, že existuje, **bez vypísania hodnoty** (napr. vypíš len `True`/`False` a dĺžku). Hodnotu kľúča nikdy nevypisuj, neukladaj do súboru, logu ani do repa.
- Model: najlacnejší Haiku (over presný identifikátor modelu v dokumentácii Anthropicu). Uveď v reporte cenu za milión tokenov podľa oficiálneho cenníka.
- Rozpočet testu: max 0,50 USD. Pred každým volaním odhadni tokeny; ak by test prekročil rozpočet, zastav sa.
- Nová závislosť (`anthropic` SDK) len ak je potrebná; inak priamy HTTP request cez `requests`.

### Postup
1. Ulož aktuálne HTML programov ako fixtures do `tests/fixtures/llm/`: Twist (https://twistbar.co/music) a Akropolis (prvé 2 strany sekcie hudba). Test beží nad uloženými kópiami, nie nad živým webom.
2. Pred poslaním modelu HTML zredukuj na text/čistejšie HTML (bez skriptov, štýlov, navigácie), aby vstup bol čo najmenší. Uveď počet tokenov vstupu.
3. Prompt: vráť JSON zoznam akcií (title, date `YYYY-MM-DD`, start_time `HH:MM`, room, sold_out), len údaje, ktoré sú na stránke; chýbajúce = null; nedomýšľať rok, čas ani nič iné. Uveď dnešný dátum, aby model vedel doplniť rok podľa nášho pravidla (dátum pred včerajškom = budúci rok) — alebo rok dopočítaj v kóde, model nech vráti len deň a mesiac. Zvoľ a zdôvodni.
4. Kontrola po modeli (v kóde): každý dátum (deň a mesiac) a čas, ktorý model vrátil, musí byť doslova v texte stránky; inak hodnotu vymaž a započítaj ako „vymyslené“.
5. Porovnanie:
   - Akropolis: výsledok LLM vs. náš parser (`html_akropolis`) na tých istých stranách, akcia po akcii: chýbajúce, navyše, zlý dátum, zlý čas, zlá sála, zlé `sold_out`. Pozor: `sold_out` parser berie z `/pub/vstupne_6`, nie z HTML; porovnaj len ak je stav v HTML.
   - Twist: parser nemáme. Vypíš tabuľku akcií od LLM (dátum, deň v týždni zo stránky, názov) a pri 5 náhodných akciách porovnaj s webom.
6. Spusti extrakciu 3× na tej istej stránke a uveď, či sú výsledky rovnaké (stabilita).
7. Kód testu ulož do `scripts/llm_test/` (nie do `pipeline/`). Žiadny zásah do denného behu.

### Report navyše
- Presnosť v číslach pre každý podnik (zhoda / chýba / navyše / chyba dátumu / chyba času / vymyslené hodnoty).
- Skutočná cena testu (tokeny × cena) a odhad mesačnej ceny pri dennom behu pre 15 podnikov.
- Príklady chýb.
- Odporúčanie: LLM adaptér, parsery na mieru, alebo kombinácia (LLM + kontrola), so zdôvodnením.
- Pripomenutie Matejovi: kľúč s expiráciou 9. 11. po teste vymazať alebo nechať vypršať.

## Report
