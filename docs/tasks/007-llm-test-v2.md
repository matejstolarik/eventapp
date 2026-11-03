# 007: Porovnanie parser vs. LLM (experiment)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02, **prepísané 2026-11-03 pred odovzdaním** (pôvodná verzia: test len na Akropolise a Twiste, v histórii gitu).

**Spustiť po úlohách 011 a 012**, najneskôr 2026-11-08 (kľúč `ANTHROPIC_API_KEY` platí do 2026-11-09; hodnotu nikdy nevypisuj ani neukladaj). Rozpočet max 3 USD (kredit 5 USD). Denný beh sa nemení, kód experimentu len v `scripts/llm_test/`.

### Prečo
Prieskum (008) ukázal, že projekt LLM nepotrebuje. Matej chce experiment aj tak, ako všeobecné porovnanie: kedy sa oplatí deterministický parser a kedy „pustiť na to AI“, so všetkými faktormi (presnosť, stabilita, cena, rýchlosť, náročnosť vývoja, odolnosť voči zmene webu). Výsledok má byť použiteľný aj mimo tohto projektu.

### Poučenie z 1. kola (úloha 006)
Porovnávať rovnaký rozsah; obmedziť „thinking“ (zisti v dokumentácii Anthropicu ako); štruktúrovaný výstup (tool use / JSON schéma); kontrolovať `stop_reason` (neúplná odpoveď = zlyhanie, nič potichu neopakovať); overiť, že čistenie HTML nezahodí čas a sálu; rok dopočítava kód.

### Dáta (pevný snímok, nie živý web)
Všetko nad uloženými stránkami z jedného dňa, aby sa výsledky dali zopakovať. Pravda = výstup našich adaptérov na tých istých súboroch.
- So spoľahlivou pravdou: Akropolis, Archa+, Forum Karlín (parsery), MeetFactory, Fuchs2 (JSON-LD), Bike Jesus (JSON rozhranie), Cross Club (RSS; LLM dostane HTML programu, nie RSS).
- Bez parsera (scenár „rýchly štart cez AI“): Jazz Republic, Futurum, El Magico. Pravda: ručná kontrola vzorky 10 akcií na podnik voči uloženej stránke.
- Twist vynechaj (program sa skladá cez JavaScript).

### Merania (každý web)
1. Úplnosť a presnosť: zhoda / chýba / navyše; správnosť polí (dátum, čas, názov, sála a vypredané tam, kde ich máme); vymyslené hodnoty (hodnota, ktorá nie je doslova na stránke).
2. Stabilita: 3 behy, rovnaký vstup.
3. Cena a rýchlosť: tokeny vstup/výstup, USD, čas odpovede.
4. Varianty vstupu: (A) len bloky akcií ako pri parseri, (B) celá stránka po čistení.
5. Model: Claude Haiku 5.5 na všetkom. Ak to rozpočet dovolí, silnejší model (napr. Sonnet; cenu over v oficiálnom cenníku) na 2–3 weboch, aby bolo vidno, či pomáha väčší model.
6. **Odolnosť voči zmene webu:** na 2–3 weboch s parserom simuluj redizajn (premenuj CSS triedy, zmeň poradie prvkov v uloženom HTML). Zaznamenaj, či parser spadne/vráti 0 a či LLM výsledok prežije.
7. **Náročnosť vývoja:** z histórie gitu a kódu odhadni pre každý parser počet riadkov a počet úloh/opráv, ktoré potreboval (napr. Akropolis: kódy lístkov, cudzie sály). Pre LLM: veľkosť promptu a koľko úprav promptu bolo treba.

### Výstup
- Report v tomto súbore (čísla v tabuľke na web × variant × model, cena celkom, príklady chýb).
- Súhrn `docs/experiments/llm-vs-parser.md`: zrozumiteľne aj pre nevývojára, faktory a kedy čo použiť, s číslami z experimentu. Toto je hlavný výstup pre Mateja.
- Ak by experiment prekročil rozpočet, zastav sa a napíš, čo chýba.

## Report
