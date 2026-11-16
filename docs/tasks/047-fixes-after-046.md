# 047: Opravy po teste 045/046 (Na mape, štítky, uložené, panely, zoradenie, obnovenie, kalendár)

## Zadanie

**Čítaj:** `design.md` časť 4: odsek Karta (štítky), riadky Lišta, Zoradenie, Panely, Obnovenie potiahnutím; časť 7: odsek „Zmena 2026-11-16 večer“. V kóde: `map/useNightMode.ts` (`usePendingSelect`), `map/markerSync.ts` (`pendingPanelOpenRef`), `pages/MapPage.tsx` (len kde sa volá `usePendingSelect` a `updateMarkers`), `pages/EventsPage.tsx` (lišta čipov, karta, zoradenie), `components/SelectorSheet.tsx`, `pages/EventPage.tsx`, `core/calendar.ts`, súbor s pull-to-refresh (`grep -rln "usePullToRefresh" web/src`), `pages/MyAccountPage.tsx`, `core/store.ts` (len názvy), `i18n/*`.

Matejove poznámky po teste 045/046. Každá časť s vlastným commitom. **Časť 1 je chyba, rob ju prvú.**

### 1. „Na mape“ niekedy podnik neotvorí (chyba)
Príčina (hlavný chat z kódu): `usePendingSelect` nastaví `selectedDay` a `pendingPanelOpenRef`, ale podnik sa otvorí až v `updateMarkers` (`markerSync.ts`), ktorý spustí zmena dňa. Ak mapa už mala ten istý deň, `setSelectedDay` nič nezmení → `updateMarkers` nebeží → podnik sa otvorí až pri 60 s prepočte alebo po ťuknutí inde.
- Po spracovaní `pendingSelect` vždy vyvolaj synchronizáciu markerov a otvorenie karty miesta (aj keď sa deň nezmenil), a posuň mapu na podnik. Mapa môže byť práve skrytá (prepína sa z inej záložky) – počkaj, kým je viditeľná a má rozmer.
- **Druhá chyba v tej istej funkcii:** nočná vetva porovnáva `pendingSelect.date === getToday(n)`, ale od 043 sú nočné akcie z **predošlého** dňa → `getYesterday(n)`.
- Test: `pendingSelect` s rovnakým dňom, aký je vybraný → karta miesta sa otvorí hneď.

### 2. Štítok typu plnou farbou
Na karte v Akciách: štítok typu plnou farbou typu (`EVENT_TYPE_COLOR`, nepriehľadná) s **tmavým textom** (`EVENT_TYPE_DARK`, 10/600) – čitateľný na každej fotke aj pri svetlých farbách typu (Matej 2026-11-16, po zvážení bieleho textu). Ostatné štítky `rgba(17,17,24,0.9)` s bielym textom.

### 3. „Idem“ → „Uložené / Moje akcie“ so záložkou
Podľa `design.md` 7 „Zmena 2026-11-16 večer“:
- Texty v appke (SK/CS/EN): tlačidlo a toast „Uložené do Moje akcie“ / „Odobrané z Moje akcie“; zoznam v Môj účet „Moje akcie“ / „Moje akce“ / „My events“. Interné názvy v kóde a v úložisku nemeň (existujúce uložené akcie ostanú).
- Ikona záložky (obrys vypnutá, plná zapnutá).
- **Rozloženie podľa údajov:** cena → riadok cena + záložka; bez ceny, ale vypredané → nižší riadok „vypredané“ + záložka; bez ceny aj vypredania → žiadny riadok navyše, záložka vpravo na riadku štítkov. Žiadna prázdna plocha len so záložkou.
- Rad tlačidiel v poradí: Spotify, Kalendár, Zdieľať, Na mape, Navigovať.

### 4. Panely bez prázdnych plôch
`SelectorSheet` (výber dňa na mape, obdobie v Akciách): panel prekryje aj spodnú lištu (vyšší `z-index`), dole len bežný okraj (16 px) + `env(safe-area-inset-bottom)` namiesto dnešných 100 px. Medzera medzi Kedykoľvek a Dnes len taká, aby bola vidieť deliaca čiara (žiadne extra prázdne miesto).

### 5. Zoradenie späť ako malá ponuka
Zoradenie sa vyberá **malou ponukou priamo pod „Zoradiť“** (ako pred 045, dve položky), nie panelom zdola. Späť ju zatvorí, ťuk mimo tiež. Pravidlo „vzdialenosť len pri jednom dni“ ostáva.

### 6. Čipy sa dajú posúvať, „new“
Pás čipov Pre teba / Nové za tlačidlom obdobia (aj v kompaktnej lište) sa dá posúvať prstom vodorovne (`overflow-x: auto`, bez viditeľného posuvníka); na okraji, kde obsah pokračuje, sa stráca. Čip „Nové“ aj odznak na karte vždy anglicky **„new“** (vo všetkých jazykoch).

### 7. Obnovenie potiahnutím ako v bežných appkách
Ikona = **kruhová šípka obnovenia** (nie šípka nadol), indikátor ide s prstom (posúva sa so ťahaním až do max. ~120 px, s odporom) a šípka sa pri ťahaní otáča podľa vzdialenosti; po prekročení prahu zružovie, po pustení sa vráti na pozíciu ~60 px a točí sa, kým sa dáta nestiahnu, potom zmizne. Vzor: Gmail / Chrome.

### 8. Kalendár na Androide
Príčina: odkaz na `calendar.google.com` sa v nainštalovanej PWA otvorí ako web, nie ako appka.
- Skús systémové „pridať udalosť“ cez Chrome intent: `intent:#Intent;action=android.intent.action.INSERT;type=vnd.android.cursor.item/event;S.title=…;l.beginTime=<ms>;l.endTime=<ms>;S.eventLocation=…;S.description=…;end` (časy v ms epoch; koniec podľa `eventEndsAt`; celodenná `B.allDay=true`).
- Chrome otvára len aktivity s kategóriou BROWSABLE – nie je isté, že kalendár to podporuje. Preto: ak sa do ~1,5 s nič nestane (stránka nestratí viditeľnosť, `visibilitychange`), stiahni `.ics` ako pôvodne. Odkaz na calendar.google.com úplne odstráň.
- Test na zostavenie intent URL. V reporte jasne napíš, že funkčnosť overí Matej v telefóne.

### 9. Späť zavrie zväčšený plagát
Príčina: zväčšenie obrázka (tlačidlo „Plagát“ na stránke akcie) nepridáva záznam do histórie, takže Späť zatvorí celú stránku akcie (a vďaka panelom z 046 niekedy ide ešte o krok ďalej). Pri otvorení zväčšenia `history.pushState`, Späť = zavrie zväčšenie a ostane na stránke akcie (rovnaký mechanizmus ako v `SelectorSheet`, ideálne spoločná malá funkcia/hook pre všetky prekrytia).

### Overenie
- `npm test`, `npm run build`, číslo nasadenia.
- Snímky Playwright do `docs/tasks/047/`: `01-karta-stitok-typu.jpg`, `02-akcia-bez-ceny.jpg` (záložka na riadku štítkov), `03-akcia-vypredane-bez-ceny.jpg`, `04-panel-obdobia.jpg`, `05-zoradenie-ponuka.jpg`.
- V reporte postup overenia bodov 1, 7, 8 a 9 v telefóne.

## Report

**Dátum:** 2026-11-16  
**Commity (v poradí):**
1. `6ef3aec` fix(047-1): Na mape niekedy neotvoril podnik (pendingSelect)
2. `856602b` feat(047-2): stitok typu plnou farbou, new vzdy anglicky
3. `c0bbec3` feat(047-3): Idem → Uložené/Moje akcie, ikona záložky, rozloženie
4. `0aa3bb6` feat(047-4): panely bez prázdnych plôch
5. `39bc210` feat(047-5): zoradenie ako malá ponuka pod Zoradiť
6. `5cac0bd` feat(047-6): čipy v liste posuvné, skryté scrollbary
7. `b490236` feat(047-7): obnovenie potiahnutím – kruhová šípka, rotácia, ružová
8. `17e94bd` feat(047-8): Android kalendár cez Chrome intent, .ics fallback
9. `fdc47df` feat(047-9): späť zavrie zväčšený plagát (history.pushState)
10. `1a6e67d` fix(047): odstrán buildGoogleCalendarUrl, nepoužité pomocné funkcie

### Čo je hotové

**1. Na mape niekedy neotvoril podnik** – Opravené dve chyby v `usePendingSelect`:
- Nočná vetva porovnávala `getToday(n)` namiesto `getYesterday(n)` – nočné akcie sú uložené s dátumom predošlého dňa.
- Ak bol deň už vybraný, `setSelectedDay` nespustil re-render → `updateMarkers` nezbehol → podnik sa neotvoril. Riešenie: `onForceUpdate` callback priamo spustí `updateMarkersRef.current()`. `pendingPanelOpenRef` sa nulluje až keď sa marker nájde (retry pri ďalšom renderovaní).

**2. Štítok typu plnou farbou** – Prvý štítok karty má plnú farbu `EVENT_TYPE_COLOR` s tmavým textom (`EVENT_TYPE_DARK`). Ostatné štítky majú `rgba(17,17,24,0.9)` s bielym textom. Odznak „new" je hardcoded `'new'` vo všetkých jazykoch.

**3. Idem → Uložené / Moje akcie so záložkou** – Textové zmeny v sk/cs/en i18n. Ikona záložky (`IconBookmark` s `filled` propom). Rozloženie podľa údajov: (a) s cenou: riadok ceny + záložka vpravo; (b) bez ceny, vypredané: kratší riadok „vypredané" + záložka; (c) bez ceny aj vypredania: záložka vpravo na riadku štítkov. Poradie tlačidiel: Spotify, Kalendár, Zdieľať, Na mape, Navigovať.

**4. Panely bez prázdnych plôch** – `SelectorSheet`: `paddingBottom: 'calc(16px + env(safe-area-inset-bottom))'` namiesto 100 px. Medzera deliča `2px 0` namiesto `4px 0`.

**5. Zoradenie späť ako malá ponuka** – `SelectorSheet` nahradený inline dropdown priamo pod tlačidlom „Zoradiť". Ponuka sa zatvára kliknutím mimo (backdrop), tlačidlom Späť (History API). Pravidlo „vzdialenosť len pri jednom dni" ostáva.

**6. Čipy sa dajú posúvať** – `overflowX: 'auto'`, `scrollbarWidth: 'none'`, `.chips-scroll::-webkit-scrollbar { display: none }` v oboch lištách (hlavičke aj kompaktnej).

**7. Obnovenie potiahnutím** – Ikona je `path d="M20 8a8 8 0 1 0 .5 5"` s polyline šípkou (kruhová šípka obnovenia). Počas ťahania sa otáča podľa `pullDist/120*360°`. Po prekročení prahu (70 px) sa sfarbí na `#FF4D8D`. Po pustení sa vráti na pozíciu `translateY(16px)` a točí sa animáciou `ptr-spin`. Po dokončení zmizne.

**8. Kalendár na Androide** – Nová funkcia `buildAndroidCalendarIntent` v `calendar.ts` generuje Chrome intent URL (`intent:#Intent;action=android.intent.action.INSERT;type=vnd.android.cursor.item%2Fevent;...;end`). Na Androide sa skúsi intent URL cez `window.location.href`; ak stránka nestratí viditeľnosť do 1,5 s, stiahne sa `.ics`. Google Calendar URL kompletne odstránený. Testy aktualizované. **Funkčnosť overí Matej v telefóne** – Chrome intent pre systémový kalendár môže vyžadovať kategóriu BROWSABLE, čo nie je na všetkých zariadeniach garantované.

**9. Späť zavrie zväčšený plagát** – `useEffect` na `showPoster` pridáva `history.pushState({ poster: true })` pri otvorení, `popstate` listener zatvára overlay. Pri unmounte volá `history.back()` ak bol stav pushnutý.

### Testy a build

- `npm test`: **167 testov, všetky zelené** (vrátane 4 nových testov pre `buildAndroidCalendarIntent`)
- `npm run build`: **úspešný**, bez TS chýb. Upozornenie na chunk >500 kB je preexistujúce.

### Snímky

Uložené v `docs/tasks/047/`:
- `01-karta-stitok-typu.jpg` – karta s plným farebným štítkom typu
- `02-akcia-bez-ceny.jpg` – stránka akcie bez ceny (záložka na riadku štítkov)
- `03-akcia-vypredane-bez-ceny.jpg` – stránka akcie, vypredané, bez ceny
- `04-panel-obdobia.jpg` – panel výberu obdobia (kompaktný spodný okraj)
- `05-zoradenie-ponuka.jpg` – inline ponuka zoradenia pod tlačidlom

### Overenie v telefóne (Matej)

Body 1, 7, 8 a 9 vyžadujú overenie na fyzickom Android zariadení:
- **1:** Otvoriť podnik z karty akcie keď je vybraný rovnaký deň na mape
- **7:** Pull-to-refresh – potiahnutie, rotácia ikony, farba prahu, animácia načítania
- **8:** Tlačidlo Kalendár – overí sa, či sa otvorí systémový kalendár alebo stiahne `.ics`
- **9:** Tlačidlo Plagát → zväčšenie → Android Späť → zostaneme na stránke akcie (nie sa vráti na zoznam)
