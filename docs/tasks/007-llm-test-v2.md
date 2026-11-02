# 007: Test LLM extrakcie, druhé kolo (opravený návrh testu)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02 (upravené pred odovzdaním: Twist nedostupný). Jednorazový test lokálne u Mateja. Denný beh sa nemení. Rozpočet max 1 USD (kľúč `ANTHROPIC_API_KEY`, hodnotu nikdy nevypisuj ani neukladaj).

Prvé kolo (úloha 006) nič nerozhodlo, lebo test bol zle postavený:
- parser a LLM porovnávali rôzny rozsah (parser 21 položiek výpisu na stranu, LLM celý text stránky s ďalšími blokmi, 93 „akcií“ na p1); vysvetlenie „120 navyše mimo okna“ je chybné, jan.–apr. 2027 je v okne +180 dní,
- nekontrolované „thinking“ a dôvod ukončenia odpovede (beh s 18 akciami),
- nevedno, či čas a sála vôbec prežili čistenie HTML,
- Twist sa netestoval.

### Postup
1. **Twist fixture:** Matej uloží stránku z prehliadača do `tests/fixtures/llm/twist_music.html` (prípadne s priečinkom súborov, ktorý prehliadač vytvorí). Ak súbor nie je k dispozícii, Twist preskoč (body 4 a 10 urob len zisťovanie dostupnosti) a sprav Akropolis; Twist uveď v reporte ako otvorený. Pozor: 2026-11-02 sa twistbar.co neotváral ani Matejovi v prehliadači („This site can't be reached“), takže príčina môže byť výpadok webu alebo DNS, nie blokovanie skriptov; zisti, čo platí (DNS záznam, odpoveď servera). Doplnené: Matejovi web ide cez mobilné dáta, nejde cez jeho domácu sieť. Príčina „ConnectionResetError“ v úlohe 006 je teda pravdepodobne Matejova sieť, nie blokovanie skriptov. Ak je Matejov počítač pripojený cez mobilné dáta (hotspot), skús stiahnuť stránku aj skriptom; do reportu zapíš výsledok. Ak súbor je, over, že v ňom je program (nie prázdna JS kostra).
2. **Akropolis, variant A (rovnaký rozsah):** LLM dostane len HTML/text položiek výpisu (`.basic_cont3`), presne tie, ktoré číta parser. Porovnanie akcia po akcii s parserom.
3. **Akropolis, variant B (realistický):** LLM dostane celú stránku po čistení, ako by to robil všeobecný adaptér. Výsledok porovnaj s parserom a zvlášť vypíš, čo LLM vrátilo navyše a odkiaľ zo stránky to je (ktorý blok).
4. **Twist:** celá stránka po čistení. Kontrola: každá akcia musí mať dátum doslova na stránke; vypíš celú tabuľku (dátum zo stránky, deň v týždni, názov) a porovnaj počet s počtom riadkov programu na stránke, ktoré spočítaš v kóde jednoduchým regexom (napr. `\d{1,2}/\d{1,2}`).
5. **Model a volanie:**
   - over v dokumentácii Anthropicu, ako vypnúť alebo obmedziť „thinking“/effort pre Haiku 5.5, a použi najnižšie nastavenie; uveď ho v reporte,
   - pre výstup použi štruktúrovaný formát (tool use / JSON schéma), nie voľný text,
   - po každom volaní skontroluj `stop_reason`; ak odpoveď nie je úplná, beh označ ako zlyhaný a zapíš to, nič potichu neopakuj,
   - rok dopočítava kód (ako v 006).
6. **Čistenie:** pred volaním over a vypíš, že v čistenom vstupe sú časy a sály (počet výskytov). Ak tam nie sú, chyba je v čistení, nie v modeli; oprav čistenie.
7. **Párovanie:** dátum + normalizovaný názov (malé písmená, bez diakritiky, bez `►`, bez prípon krajín typu `/CH`). Všetky nespárované položky vypíš v reporte, nech sa dajú skontrolovať ručne.
8. **Stabilita:** každý variant 3×. Uveď počet akcií a zhodu medzi behmi.
9. Závislosť `anthropic` presuň z hlavného `requirements.txt` do `scripts/llm_test/requirements.txt` (denný beh ju nepotrebuje).
10. **Twist sťahovanie (len zistiť, neimplementovať):** prečo twistbar.co odmieta skriptované spojenie (User-Agent, TLS, ochrana typu Cloudflare?) a či ho odmieta aj z GitHub Actions. Možné riešenia popíš do reportu; ak by riešenie menilo spôsob sťahovania (napr. headless prehliadač), je to rozhodnutie pre Mateja.

### Report navyše
- Tabuľka pre Akropolis A, Akropolis B, Twist: počet akcií, zhoda / chýba / navyše / zlý dátum / zlý čas / zlá sála / vymyslené, stabilita 3 behov.
- Cena testu a odhad mesačnej ceny (15 podnikov denne).
- Odporúčanie a s akou istotou; čo by sa ešte muselo overiť.

## Report
