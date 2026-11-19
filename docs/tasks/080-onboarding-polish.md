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
| Toast po uložení preferencií | Uložené | Uloženo | Saved |

Ostatné texty z 079 bez zmeny.

### 2. Ďalej bez výberu
- V každom kroku výberu (miesta, typy, žánre): ťuk na **Ďalej** bez jediného výberu → tlačidlo sa krátko zatrasie (~300 ms do strán) a telefón jemne zavibruje, ak to prehliadač podporuje (`navigator.vibrate`, bez chyby, keď nie). Do ďalšieho kroku sa nejde. Preskočiť ostáva na preskočenie. `prefers-reduced-motion`: bez trasenia, len vibrácia.

### 3. Ružové čiary po odkliknutí
- Po vybratí a zrušení karty typu (DJ, kultúra a ďalšie) ostáva pod kartou ružová čiara / zvyšok obrysu (kultúra aj po zbalení podtypov). **Odstrániť** – zrušená karta má vyzerať presne ako nikdy nevybratá (skontroluj obrys, `outline`/focus, tieň, zvyšok rozbalenej plochy, prechod). Rovnako skontroluj čipy podtypov a žánrov a srdiečka.

### 4. Obrazovka Hotovo – preusporiadať
- **Obe karty rovnako:** vľavo skutočné tlačidlo (✦ Pre teba čip; **Filter ako pilulka s ikonou a textom „Filter“ / „Filtr“ / „Filter“ v rovnakom tvare a veľkosti ako čip Pre teba** – len na tejto obrazovke), vpravo ukážka, pod tým veta. Filter nie je nad ukážkou, ale vedľa nej, ako pri Pre teba.
- Ukážky realistickejšie: riadky ako malá kostra riadku akcie (obrázok vo farbe typu + dva sivé pruhy textu). Pre teba: 3 riadky, 2 s iskrou na obrázku, žiadny nezmizne. Filter: 4 riadky → šípka **zvislo v strede medzi stĺpcami** → 2 riadky (rovnaký typ).
- Zarovnať: rovnaké vnútorné okraje kariet, rovnaká šírka ľavého stĺpca s tlačidlom v oboch kartách, text pod ukážkou zarovnaný vľavo s tlačidlom.

### 5. Pre teba bez preferencií v Akciách
- Ťuk na Pre teba bez akýchkoľvek preferencií: **čip sa normálne zapne**, zoznam je prázdny a **v strede zoznamu** je správa (rovnaký štýl ako prázdny stav filtra `FilterEmptyCard`, ale samostatný komponent/text): „Nastav si, čo ťa baví, a označíme ti akcie ✦“ (cs „Nastav si, co tě baví, a označíme ti akce ✦“, en „Set what you're into and we'll mark events for you ✦“) a ružové tlačidlo **Nastaviť** / Nastavit / Set up → Preferencie akcií. **Karta nad lištou (toast z 079) sa ruší.** Po nastavení a návrate sa zoznam ukáže podľa nových preferencií.
- Ak preferencie sú, ale v období nie je žiadna akcia pre teba, ostáva doterajší prázdny stav (bez zmeny).

### 6. Preferencie akcií (stránka)
- Poradie sekcií: **Typy → Žánre → Obľúbené miesta** (miesta naposledy, sú najdlhšie). Zoznam miest celý ako doteraz (s hľadaním), bez skracovania.
- Hore v hlavičke vpravo okrúhle tlačidlo len s **ikonou fajky** (44 px, štýl tlačidiel hlavičky – `#23232F`, ikona `#F4F2FF`); hlavička sa posúva so stránkou (nie je prilepená). Ťuk → stránka sa zavrie (ako Späť) a toast „Uložené“. Ukladá sa ďalej hneď pri každej zmene; tlačidlo je pre pocit istoty.

## Overenie a report
- `npm test -- --reporter=dot` (trasenie/neprechod pri prázdnom výbere, Pre teba bez preferencií = prázdny stav so správou, poradie sekcií), `npm run build`; nasadenie `deploy-app` (číslo behu). Dáta sa nemenia.
- Snímky JPEG 390 × 844 (Playwright, skript z 079) do `docs/tasks/080/`: `onb-1-welcome.jpg`, `onb-2-places.jpg`, `onb-3-types-deselected.jpg` (DJ a kultúra vybraté a znova zrušené – bez čiar), `onb-5-done.jpg`, `onb-skip-confirm.jpg`, `events-for-you-empty.jpg` (bez preferencií, Pre teba zapnuté), `preferences.jpg` (hore s fajkou).
