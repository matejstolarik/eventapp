# 042: Akcie – zbaliteľná hlavička, šípka navrch, návrat Späť, drobnosti

## Zadanie

**Čítaj:** `design.md` časť 4 (riadky „Riadok pod lištou“, „Pri scrolle“, „Zmena = navrch“, „Šípka navrch“, „Ťuk na aktívnu záložku“, „alt“) a časť 5 (prvý riadok); snímka `docs/design/screens/13-akcie-zbalene.png` a HTML `docs/design/html/13-akcie-zbalene.html`. V kóde: `web/src/App.tsx` (`parseHash`, `navigate`, `goBack`, `handleTabChange`, vykreslenie záložiek), `pages/EventsPage.tsx`, `pages/PlacesPage.tsx`, `components/BottomNav.tsx`, miesto, kde sa vykresľujú štítky (`grep -rn "character" web/src --include=*.tsx`).

Matejove poznámky po teste 041. Malé, samostatné časti; každá s vlastným commitom.

### 1. Späť zo stránky akcie → mapa (chyba)
Príčina (hlavný chat z kódu): záložky `events` a `account` nemajú vlastný hash. `parseHash` pre prázdny hash vráti `map`; po `history.back()` zo `#/akcia/…` sa hash vráti na prázdny a `onHashChange` prepne na mapu. Navyše `EventsPage` sa pri otvorenej stránke akcie odmontuje (`activeTab === 'events' && !isOverlay`), takže by sa stratil text hľadania aj scroll.
- Pridaj routy `#/akcie` a `#/ucet` (parseHash, navigate, handleTabChange, onHashChange). Prepnutie záložky nastaví hash; Späť zo stránky akcie/miesta vráti na záložku, z ktorej prišiel používateľ.
- `EventsPage` (a `MyAccountPage`) ostávajú namontované aj pod stránkou akcie (skryté, ako mapa), aby sa zachoval stav: obdobie, Pre teba/Nové, otvorené hľadanie s textom, zoradenie a **pozícia scrollu**.
- Test: `parseHash` pre nové routy; prechod Akcie → akcia → Späť = Akcie.

### 2. Kedykoľvek bez počtu
Pri období Kedykoľvek sa vľavo nad mriežkou nezobrazuje počet (ani „· N pre teba“); vpravo ostáva Zoradiť.

### 3. Zbaliteľná hlavička
Podľa `design.md` 4 „Pri scrolle“ a snímky `13`: pri scrolle nadol odíde nadpis a riadok s počtom/zoradením; prilepená ostane kompaktná lišta (obdobie, Pre teba, Nové, lupa, miesto pre Filter). Prechod plynulý (hlavička scrolluje normálne so zoznamom, kompaktná lišta je `position: sticky` – žiadne skoky obsahu, žiadne prepočítavanie pri každom pixeli scrollu v Reacte; ak treba sledovať scroll, `IntersectionObserver` na hlavičke). Ťuk na lupu v kompaktnej lište: navrch + rozbalenie + otvorenie hľadania. Animácia hľadania z 041 sa nesmie rozbiť.
Poznámka k 041: roztiahnutie poľa hľadania je urobené cez `scaleX`; ak sa pri ňom text alebo ikona v poli počas animácie deformuje, zmeň na animáciu šírky (`width` / `clip-path`).

### 4. Zmena = navrch
Po akejkoľvek zmene obdobia, Pre teba, Nové, zoradenia alebo textu hľadania (po debounce) sa zoznam plynulo vyroluje navrch (`scrollTo({top:0, behavior:'smooth'})`) a hlavička sa rozbalí.

### 5. Šípka navrch + ťuk na aktívnu záložku (Akcie aj Miesta)
- Okrúhle tlačidlo podľa `design.md` 4 (44 px, `#23232F`, šípka nahor, vpravo 16 px, spodok 116 px), objaví sa po odscrollovaní ~2 výšok obrazovky, ťuk → plynulý scroll navrch, potom zmizne. V Akciách aj v Miestach.
- Ťuk na už aktívnu záložku Akcie alebo Miesta v `BottomNav` vyroluje zoznam navrch.

### 6. `alternative` → `alt`
Štítok `alternative` sa všade v UI (karty Akcií, profil miesta, karta na mape, filter) zobrazuje ako `alt`. Len zobrazenie (jedna mapovacia funkcia pre popisky štítkov), dáta sa nemenia.

### 7. Plynulé animácie (Matej 2026-11-15)
Všetko z bodov 3–5 a zmeny obsahu mriežky majú ísť plynulo, nič nesmie skočiť:
- **Lupa** sa pri zbalení hlavičky presunie z hlavičky do kompaktnej lišty plynulo (napr. prelínanie + posun, ~200 ms), pri rozbalení naspäť. Nadpis a riadok s počtom pri odchode stmavnú/vyblednú spolu so scrollom, nie naraz.
- **Karty pri zmene filtra** (obdobie, Pre teba, Nové, hľadanie, zoradenie): odchádzajúce karty krátko vyblednú (opacity + scale 1 → 0,96, ~120 ms), nové sa objavia (opacity 0 → 1, scale 0,96 → 1, ~180 ms, `ease-out`), v štýle objavovania pinov na mape. Animuj len karty vo viditeľnej časti (prvé ~12), ostatné bez animácie. Súčasne s plynulým scrollom navrch (bod 4), bez trhania.
- **Šípka navrch** sa objaví/zmizne prelínaním (~150 ms).
- Len `opacity` a `transform` (žiadne animácie výšky/šírky v zozname), `prefers-reduced-motion` = bez animácií.
- Over na pomalšom zariadení: v DevTools CPU 4× spomalenie, scroll a zmena filtra bez viditeľného trhania; v reporte jedna veta, ako to dopadlo.

### Overenie
- `npm test`, `npm run build`, číslo nasadenia.
- Snímky Playwright do `docs/tasks/042/`: `01-akcie-kedykolvek.jpg` (bez počtu), `02-akcie-zbalene.jpg` (odscrollované, kompaktná lišta + šípka), `03-miesta-sipka.jpg`.
- V reporte postup, ako si Matej overí bod 1 v telefóne.

## Report
