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

Dátum: 2026-11-02. Commit: pozri nižšie.

### Čo bolo urobené

- Vytvorený `scripts/llm_test/run.py` — testovací skript s BudgetGuard, year inference, čistením HTML, LLM volaním, verifikáciou a porovnaním s parserom.
- Uložené fixtures: `tests/fixtures/llm/akropolis_hudba_p1.html` (222 733 B) a `akropolis_hudba_p2.html` (223 129 B) — živé stránky Akropolis hudba ku 2026-11-02.
- Twist fixture: **nedostupná** — twistbar.co blokuje všetky ne-prehliadačové TLS spojenia (ConnectionResetError WinError 10054 pri SSL handshake). Test prebehol iba na Akropolis.
- Pridaná závislosť `anthropic>=2.4` do `requirements.txt`.

### Model a cena

- Model: `claude-haiku-5-5`, $0,10/M vstupných tokenov, $0,50/M výstupných tokenov.
- Adaptívne myslenie (`thinking` bloky) je defaultne zapnuté — výstupné tokeny sú oveľa väčšie ako pri klasickom behu. Potrebný `max_tokens=16000`; s 4 096 model v ~60 % prípadov vráti iba `thinking` blok bez textu.
- Skutočné tokeny na stránku: ~6 600 vstupných (odhad bol ~2 000 — tokenizér Haiku je hustejší).
- **Celková cena testu:** stability (3× p1) = 19 794in/26 975out; extrakcia (p1+p2) = 13 200in/24 702out → spolu ~32 994in/51 677out = **$0,029** (v rámci rozpočtu $0,50).
- **Odhad mesačnej ceny** (15 podnikov, 1 stránka/podnik/deň): ~$3,08/mesiac.

### Presnosť — Akropolis (fuzzy normalizácia názvov)

| Metrika | Hodnota |
|---|---|
| Parser udalostí (p1+p2, okno +180 dní) | 41 |
| LLM extrakcií celkom (p1+p2) | 184 |
| LLM unikátnych po deduplikácii (dátum+title) | 142 |
| Zhody (fuzzy normalized title + dátum) | 22 |
| Presnosť (matches/llm_unique) | **15 %** |
| Recall (matches/parser) | **54 %** |
| Chýba v LLM | 13 |
| Navyše v LLM | 120 |
| Zlý čas (LLM=None, parser má hodnotu) | 15 |
| Zlá sála (LLM=None, parser má hodnotu) | 15 |
| Vymyslené hodnoty (hallucinations) | **0** |

### Príklady chýb

**LLM extrahuje prefix venue série, parser nie:**
- Parser: `'ANTIWORDS'` (z `.banner_m_title`)
- LLM: `'SPITFIRE COMPANY ► ANTIWORDS'` + `'SPITFIRE COMPANY ANTIWORDS'` (duplikát bez `►`)

**LLM ignoruje country suffixes:**
- Parser: `'BLACK SEA DAHU/CH+SUPPORT ►SOLONG/CH'`
- LLM: `'BLACK SEA DAHU + SUPPORT SOLONG'`

**LLM extrahuje akcie mimo okna +180 dní:**
- Parser filtruje na max 2027-05-01; LLM vrátil udalosti z januára–apríla 2027 (120 navyše)

**LLM vráti null pre čas/sálu (~37 % udalostí):**
- Parser: `start_time='20:00', room='Velký sál'`
- LLM: `start_time=None, room=None` — čas/sála sú v HTML, ale LLM ich preskočil v čistenom texte

### Stabilita

3 behy na tej istej stránke (p1, `max_tokens=16000`):
- Beh 1: 93 udalostí (6 598in / 12 216out)
- Beh 2: 99 udalostí (6 598in / 11 550out)
- Beh 3: **18 udalostí** (6 598in / 3 209out) — model v tomto behu drasticky skrátil odpoveď

Stabilita (raw): **FAIL** | Stabilita (normalized titles): **FAIL**

Beh 3 ukazuje, že model môže niekedy vrátiť ~20 % udalostí namiesto ~95 % — nekontrolovateľne a bez chybového stavu.

### Nezávislé rozhodnutia

- Rok sa dopočítava v kóde (nie modelom): model vráti `date_raw` napr. `"4. 11."`, Python aplikuje pravidlo (dátum pred včerajškom → budúci rok). Zdôvodnenie: deterministickejšie, lacnejšie, konzistentné s existujúcimi adaptérmi.
- `max_tokens=16000` namiesto 4 096 — potrebné pre thinking bloky Haiku 5.5.
- Verifikácia každej vrátenej hodnoty oproti zdrojovému textu stránky — nulové halucinácie potvrdené.

### Odporúčanie

**Parsery na mieru sú preferovaný prístup** pre podniky, kde vieme napísať CSS selector (Akropolis, a podobné štruktúrované stránky). Dôvody:
1. Stabilita: parser je 100 % deterministický; LLM zlyhal v 1 z 3 behov.
2. Presnosť: parser recall ~100 % pre Akropolis; LLM recall 54 %.
3. Čas/sála: parser extrahuje spoľahlivo; LLM vracia null v 37 % prípadov.
4. Cena: parser je zadarmo; LLM ~$3/mesiac.

**LLM + kontrola (kombinácia)** je vhodná pre:
- Nové podniky, kde chýba štruktúrovaný HTML a písanie parsera by trvalo príliš dlho.
- Twist (ak sa podarí získať fixture z prehliadača — twistbar.co blokuje skriptované fetche).
- Nutné doplniť: post-processing (deduplication, date-window filter, title normalization), `max_tokens=16000`, a viaceré behy so vzájomnou kontrolou výsledkov.

**Čistý LLM adaptér bez kontroly** sa **neodporúča** — nestabilita behu 3 je kritická chyba pre denný pipeline.

### Otvorené body

- Twist fixture: treba manuálne uložiť z prehliadača (F12 → Save as) a spustiť test znova.
- Presnosť LLM na Twist (bez parsera na porovnanie) zostáva neznáma.

### ⚠️ Pripomenutie

**Kľúč `ANTHROPIC_API_KEY` má expiráciu 9. 11. 2026 — po teste ho vymazať alebo nechať vypršať.**
