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
Na karte v Akciách: štítok typu plnou farbou typu (`EVENT_TYPE_COLOR`, nepriehľadná) s **bielym textom** `#F4F2FF` 10/600 – konzistentne s tmavými štítkami, ktoré majú tiež biely text (Matej 2026-11-16). Ostatné štítky `rgba(17,17,24,0.9)`. Pri svetlých farbách typu (limetková kultúra, oranžová párty) pridaj jemný tieň textu (`text-shadow: 0 0 2px rgba(0,0,0,.45)`), aby bol biely text čitateľný.

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
