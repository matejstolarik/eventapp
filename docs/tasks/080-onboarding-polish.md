# 080: Doladenie onboardingu, Pre teba bez preferencií, Preferencie akcií

## Zadanie

**Schválené Matejom 2026-11-19 16:23–16:32 (po teste 079).** Mení len appku (`web/`) → **pipeline nespúšťaj**, over len nasadenie `deploy-app`. Čo nie je jasné, spýtaj sa (nevymýšľaj UI).

**Čítaj:** report 079; `docs/design.md` 7c (aj **blok „Zmena 2026-11-19 večer (080)“**); `web/src/pages/OnboardingPage.tsx`, `web/src/components/PrefPickers.tsx`, `web/src/pages/PreferencesPage.tsx`, `web/src/pages/MyAccountPage.tsx`, `web/src/components/SetupPromptCard.tsx`, `web/src/components/FilterEmptyCard.tsx`, `web/src/pages/EventsPage.tsx` (Pre teba, prázdny stav – `grep -n "forYou\|empty"`), `web/src/i18n/*.ts` (sekcia onboardingu a preferencií).

### 1. Texty (nahrádzajú texty z 079)
| Kde | sk | cs | en |
|---|---|---|---|
| Uvítanie text | Vyber miesta, akcie a hudbu, ktoré ťa bavia. Označíme ti akcie, ktoré by sa ti mohli páčiť. | Vyber místa, akce a hudbu, které tě baví. Označíme ti akce, které by se ti mohly líbit. | Pick the places, events and music you're into. We'll mark events you might like. |
| Potvrdenie preskočenia – text | Bez nastavenia ti nevieme odporučiť akcie, ktoré by ťa mohli baviť. | Bez nastavení ti nedokážeme doporučit akce, které by tě mohly bavit. | Without it, we can't recommend events you might like. |
| Miesta – podnadpis | Označ svoje obľúbené. | Označ svá oblíbená. | Pick your favourites. |
| Názov v Môj účet a nadpis stránky (nahrádza „Tvoje preferencie“) | Preferencie akcií | Preference akcí | Event preferences |
| Toast po preskočení | Nastaviť to môžeš kedykoľvek v Môj účet → Preferencie akcií. | Nastavit to můžeš kdykoli v Můj účet → Preference akcí. | You can set this up anytime in My account → Event preferences. |
| ~~Toast po uložení preferencií~~ (**zrušené 16:35, Matej** – žiadny toast) | ~~Uložené~~ | ~~Uloženo~~ | ~~Saved~~ |

Ostatné texty z 079 bez zmeny.

### 2. Ďalej bez výberu
- V každom kroku výberu (miesta, typy, žánre): ťuk na **Ďalej** bez jediného výberu → tlačidlo sa krátko zatrasie (~300 ms do strán) a telefón jemne zavibruje, ak to prehliadač podporuje (`navigator.vibrate`, bez chyby, keď nie). Do ďalšieho kroku sa nejde. Preskočiť ostáva na preskočenie. `prefers-reduced-motion`: bez trasenia, len vibrácia.

### 3. Ružové čiary po odkliknutí
- Po vybratí a zrušení karty typu (DJ, kultúra a ďalšie) ostáva pod kartou ružová čiara / zvyšok obrysu (kultúra aj po zbalení podtypov). **Odstrániť** – zrušená karta má vyzerať presne ako nikdy nevybratá (skontroluj obrys, `outline`/focus, tieň, zvyšok rozbalenej plochy, prechod). Rovnako skontroluj čipy podtypov a žánrov a srdiečka.

### 4. Obrazovka Hotovo – preusporiadať
- **Obe karty rovnako:** vľavo skutočné tlačidlo (✦ Pre teba čip; **Filter ako pilulka s ikonou a textom „Filter“ / „Filtr“ / „Filter“ v rovnakom tvare a veľkosti ako čip Pre teba** – len na tejto obrazovke), vpravo ukážka, pod tým veta. Filter nie je nad ukážkou, ale vedľa nej, ako pri Pre teba.
- Ukážky realistickejšie: riadky ako malá kostra riadku akcie (obrázok vo farbe typu + dva sivé pruhy textu). Pre teba: 3 riadky, 2 s iskrou na obrázku, žiadny nezmizne. Filter: 4 riadky → šípka **zvislo v strede medzi stĺpcami** → 2 riadky (rovnaký typ).
- Zarovnať: rovnaké vnútorné okraje kariet, rovnaká šírka ľavého stĺpca s tlačidlom v oboch kartách, text pod ukážkou zarovnaný vľavo s tlačidlom.

- **Spresnenie 16:40 (Matej, pred spustením; podľa snímky z 079 a návrhu v chate) – platí pred bodmi vyššie, kde sa líšia.** Rozloženie ostáva ako v 079 (tlačidlo vľavo, ukážka vpravo, veta pod tým), len bez chýb:
  - Obe karty majú **rovnakú mriežku**: ľavý stĺpec s pilulkou rovnakej šírky (Pre teba aj Filter rovnako široké, vertikálne v strede ukážky), vpravo ukážka; rovnaké okraje kariet.
  - **Riadky ukážok rovnaké v oboch kartách** (rovnaká výška, obrázok, dva pruhy textu, rovnaké medzery).
  - **Pre teba:** 4 riadky, **iskra na obrázku riadku vľavo hore** (ako skutočný odznak), nie samostatne na pravom okraji karty; iskru majú 2 zo 4.
  - **Filter:** 4 riadky → šípka → 2 riadky; **šípka aj pravý stĺpec zvislo v strede ľavého stĺpca**; pravý stĺpec = tie isté 2 riadky z ľavého (rovnaké farby). ~~Filter ako pilulka s textom (nie kruh).~~ **Zmena 16:38 (Matej): Filter = skutočné tlačidlo Filtra z appky (ružový kruh 44 px s ikonou, bez textu, bez odznaku), v strede ľavého stĺpca rovnakej šírky ako pri Pre teba.** Platí aj pre bod vyššie o „Filter ako pilulka“ – zrušené.

### 5. Pre teba bez preferencií v Akciách
- Ťuk na Pre teba bez akýchkoľvek preferencií: **čip sa normálne zapne**, zoznam je prázdny a **v strede zoznamu** je správa (rovnaký štýl ako prázdny stav filtra `FilterEmptyCard`, ale samostatný komponent/text): „Nastav si, čo ťa baví, a označíme ti akcie ✦“ (cs „Nastav si, co tě baví, a označíme ti akce ✦“, en „Set what you're into and we'll mark events for you ✦“) a ružové tlačidlo **Nastaviť** / Nastavit / Set up → Preferencie akcií. **Karta nad lištou (toast z 079) sa ruší.** Po nastavení a návrate sa zoznam ukáže podľa nových preferencií.
- Ak preferencie sú, ale v období nie je žiadna akcia pre teba, ostáva doterajší prázdny stav (bez zmeny).

### 6. Preferencie akcií (stránka)
- Poradie sekcií: **Typy → Žánre → Obľúbené miesta** (miesta naposledy, sú najdlhšie). Zoznam miest celý ako doteraz (s hľadaním), bez skracovania.
- Hore v hlavičke vpravo okrúhle tlačidlo len s **ikonou fajky** (44 px, štýl tlačidiel hlavičky – `#23232F`, ikona `#F4F2FF`); hlavička sa posúva so stránkou (nie je prilepená). Ťuk → stránka sa zavrie (ako Späť), ~~a toast „Uložené“~~ **bez toastu** (zmena 16:35, Matej: Späť ukladá tiež, bez správy – toast len pri fajke by mýlil). Ukladá sa ďalej hneď pri každej zmene; tlačidlo je pre pocit istoty.

## Overenie a report
- `npm test -- --reporter=dot` (trasenie/neprechod pri prázdnom výbere, Pre teba bez preferencií = prázdny stav so správou, poradie sekcií), `npm run build`; nasadenie `deploy-app` (číslo behu). Dáta sa nemenia.
- Snímky JPEG 390 × 844 (Playwright, skript z 079) do `docs/tasks/080/`: `onb-1-welcome.jpg`, `onb-2-places.jpg`, `onb-3-types-deselected.jpg` (DJ a kultúra vybraté a znova zrušené – bez čiar), `onb-5-done.jpg`, `onb-skip-confirm.jpg`, `events-for-you-empty.jpg` (bez preferencií, Pre teba zapnuté), `preferences.jpg` (hore s fajkou).

## Report

**2026-11-19**, commit `4de9449` (appka, testy, Playwright skript, snímky, decisions), report v nasledujúcom commite. Mení len appku → pipeline sa nespúšťal, dáta bez zmeny. Nasadenie **Deploy web app #54** (run 44558906987): **success**, `4de9449`; na Pages je balík `assets/index-Dp3OXJOl.js` (obsahuje „Preferencie akcií“, „Označ svoje obľúbené“, `for-you-setup`, `onbShake`).

### Hotové
1. **Texty** (sk, cs, en) presne podľa tabuľky: uvítanie, potvrdenie preskočenia, podnadpis miest, „Preferencie akcií“ (riadok v Môj účet aj nadpis stránky), toast po preskočení. Toast po uložení nie je (zrušený).
2. **Ďalej bez výberu** (miesta, typy, žánre): tlačidlo sa zatrasie 300 ms do strán, `navigator.vibrate(30)` (v `try`, bez chyby, keď nie je); krok sa nemení. `prefers-reduced-motion`: len vibrácia. Logika `stepHasPick` v `core/preferences.ts`.
3. **Ružové zvyšky:** obrys karty typu je vnútorný `box-shadow` na vlastnej vrstve namiesto 1,5 px `border`; zbalené podtypy `visibility: hidden`; tlačidlá kariet, čipov a srdiečok bez `outline` a tap highlight. Test: po vybratí a zrušení DJ a kultúry je obrys rovnaký ako pri nikdy nevybratej karte a výška podtypov 0.
4. **Hotovo:** obe karty rovnaká mriežka (ľavý stĺpec 116 px, tlačidlo v strede: čip Pre teba / skutočné okrúhle tlačidlo Filtra 44 px), vpravo ukážka, veta pod tým zarovnaná vľavo. Riadky ukážok rovnaké (22 px, obrázok vo farbe typu, 2 pruhy). Pre teba: 4 riadky, ✦ vľavo hore na obrázku 2 zo 4. Filter: 4 riadky → šípka → 2 riadky (tie isté 2 DJ), zvislo v strede.
5. **Pre teba bez preferencií:** čip sa zapne, v strede zoznamu karta `ForYouSetupCard` (štýl `FilterEmptyCard`) s textom a ružovým „Nastaviť“ → Preferencie akcií. Karta nad lištou (`SetupPromptCard`) zmazaná. Po nastavení a návrate sa zoznam prepočíta (overené v Playwright: po výbere miesta a typu a fajke karta zmizne). Prázdny stav s preferenciami bez zmeny.
6. **Preferencie akcií:** poradie Typy → Žánre → Obľúbené miesta (celý zoznam s hľadaním), v hlavičke vpravo okrúhle tlačidlo s fajkou (44 px, `#23232F`, ikona `#F4F2FF`), hlavička sa posúva so stránkou; ťuk = zavrieť ako Späť, bez toastu.

### Rozhodnutia (samostatne, v `docs/decisions.md`)
- Uložené zapnuté Pre teba bez preferencií sa už nevypína (nahrádza rozhodnutie 079) – zobrazí kartu Nastaviť.
- Karta Nastaviť má prednosť pred prázdnym stavom filtra.
- „Výber“ v kroku miest = aspoň jedno obľúbené miesto (aj z predošla).
- Príčina ružového zvyšku je odhad (zlomkový okraj + zbaľovanie v Chrome); oprava odstraňuje všetky možné zdroje (okraj, outline, tap highlight, viditeľnosť podtypov). Na skutočnom telefóne som neoveroval.

### Overenie
- `npm test -- --reporter=dot` (z `web/`): **16 súborov, 264 testov passed** (nové: neprechod pri prázdnom výbere v každom kroku, poradie sekcií, Pre teba bez preferencií = karta). `npm run build` OK.
- Playwright `tests/playwright/screenshots-080.spec.ts` (z `web/`, `NODE_PATH=web/node_modules`, dáta z Pages, čas 19. 11. 19:00): **3 passed** – trasenie a zostanie v kroku (miesta, typy, žánre), bez zvyšku po zrušení, Hotovo (rovnaký ľavý stĺpec, 4 riadky / 2 iskry, 4 → 2), toast „…Preferencie akcií.“, Pre teba bez preferencií → karta v strede (y 367–462 px z 844), poradie sekcií, fajka zavrie.
- Snímky v `docs/tasks/080/`: `onb-1-welcome.jpg`, `onb-2-places.jpg`, `onb-3-types-deselected.jpg`, `onb-5-done.jpg`, `onb-skip-confirm.jpg`, `events-for-you-empty.jpg`, `preferences.jpg`. Podľa pravidiel som ich neprezeral – vzhľad posúdi Matej.

### Otvorené
- Vibrácia a ružový zvyšok na skutočnom telefóne neoverené (Playwright nevibruje; zvyšok sa v Chromiu nedá spoľahlivo vyvolať).
