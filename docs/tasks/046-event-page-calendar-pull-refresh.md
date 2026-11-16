# 046: Stránka akcie (cena, Idem, Na mape), kalendár, obnovenie potiahnutím

## Zadanie

Robí sa po 045.

**Čítaj:** `design.md` časť 7 (posledné dva odseky „Zmena 2026-11-16“ a „Kalendár (2026-11-16)“) a v časti 4 riadok „Obnovenie potiahnutím“. V kóde: `web/src/pages/EventPage.tsx`, `core/store.ts` (Idem), `core/events.ts` (`eventEndsAt`), súbor, ktorý dnes robí `.ics` (`grep -rn "ics\|VCALENDAR" web/src`), `App.tsx` (`goToMap`, načítanie `events.json`), `pages/EventsPage.tsx` a `pages/PlacesPage.tsx` (scroll kontajnery), `index.html` / `styles/global.css`, `components/SelectorSheet.tsx`, `components/DaySelector.tsx`, v `pages/MapPage.tsx` a `pages/EventsPage.tsx` len `pushState`/`popstate`.

Každá časť s vlastným commitom.

### 1. Riadok s cenou a Idem
Podľa `design.md` 7: pod štítkami riadok – vľavo `price_text` presne ako zo zdroja (bez slova „vstupné“), 17/600; pri `sold_out` prečiarknutá sivá cena + štítok „vypredané“; bez ceny len Idem. Vpravo okrúhle tlačidlo **Idem** 40 px bez textu: vypnuté tmavé s obrysom a ikonou plus v kruhu, zapnuté ružové s ikonou fajky v kruhu. Po ťuknutí krátka správa dole (toast ~2 s): „Pridané do Idem“ / „Odobrané z Idem“ (CZ „Přidáno do Jdu“ / „Odebráno z Jdu“, EN „Added to Going“ / „Removed from Going“). `aria-label`. Cena z riadku „deň dátum · čas · cena“ sa odstráni (je už v novom riadku).

### 2. Rad menších tlačidiel
Kalendár, Zdieľať, Spotify, **Na mape**, Navigovať (Idem z radu vypadne). Na mape = existujúce `goToMap(venueId, date)`; ak akcia práve beží v nočnom režime, vyber „Teraz v noci“. Ikona Na mape: pin mapy (rovnaký štýl ako ostatné).

### 3. Kalendár
Na Androide (`/Android/i.test(navigator.userAgent)`) tlačidlo Kalendár otvorí Google Kalendár s predvyplnenou akciou:
`https://calendar.google.com/calendar/render?action=TEMPLATE&text=<názov>&dates=<YYYYMMDDTHHMMSS>/<YYYYMMDDTHHMMSS>&ctz=Europe/Prague&details=<odkaz na zdroj akcie>&location=<miesto, adresa>` (všetko URL-encode; časy pražské bez `Z`; koniec = `end_time`, inak `eventEndsAt`; akcia bez času začiatku = celodenná `YYYYMMDD/YYYYMMDD+1`). Ostatné zariadenia: `.ics` ako doteraz. Test na zostavenie URL (vrátane akcie cez polnoc a celodennej).

### 4. Obnovenie potiahnutím (Akcie, Miesta)
Príčina: Chrome pri potiahnutí načíta celú stránku znova (tenký pásik načítania hore sa nedá skryť) a pri krátkom zozname sa gesto nespustí (Matej: pri Zajtra nereaguje).
- Natívne obnovenie vypni (`overscroll-behavior-y: contain` na `html, body` aj na scroll kontajneroch).
- Vlastné: keď je zoznam navrchu a používateľ ťahá nadol, zobraz koliesko so šípkou (vzhľad podobný Chromu, farby appky), po prekročení ~70 px a pustení: koliesko sa točí, appka znova stiahne `events.json` (`cache: 'no-store'`) a prekreslí; bez načítania stránky. Funguje aj pri krátkom alebo prázdnom zozname. Na mape nie.
- Chyba siete: koliesko zmizne, krátka správa „Nepodarilo sa obnoviť“.

### 5. Späť zatvorí panel aj na mape (doplnok z 045)
V 045 je Späť → zatvorenie panelu len v `EventsPage` (`history.pushState({sheet:true})`). Rovnako urob pre výber dňa na mape (`DaySelector`) a kalendár „Iný dátum“ na mape – najlepšie raz priamo v `SelectorSheet` (otvorenie = `pushState`, `popstate` = zatvorenie), aby to platilo všade a `EventsPage` nemal vlastnú kópiu. Nesmie sa biť s existujúcim `pushState({panel:'open'})` pre kartu miesta v `MapPage`.

### Overenie
- `npm test`, `npm run build`, číslo nasadenia.
- Snímky Playwright do `docs/tasks/046/`: `01-akcia-cena-idem.jpg` (s rozsahom ceny), `02-akcia-vypredane-idem-zapnute.jpg`, `03-akcie-potiahnutie.jpg` (koliesko počas ťahania, ak sa dá nasimulovať; inak vynechaj a napíš).
- V reporte, ako si Matej overí kalendár a obnovenie potiahnutím v telefóne.

## Report

**Dátum:** 2026-11-16

**Commity:**
- `62fbffd` feat(046-1-2): cena+Idem riadok, Na mape tlacidlo
- `3ade35b` feat(046-3): kalendar Android Google Calendar, ios/desktop ics
- `46e2f18` feat(046-4): obnovenie potiahnuti (pull-to-refresh)
- `14ccfdd` feat(046-5): spat zatvori SelectorSheet aj na mape (popstate v SelectorSheet)

**Čo je hotové:**

1. **Riadok s cenou a Idem** – `EventPage` má nový riadok pod štítkami: vľavo `price_text` (17 px/600, pri `sold_out` prečiarknutá sivá + ružový štítok „vypredané"), vpravo okrúhle 40 px tlačidlo Idem (tmavé + ikona plus v kruhu / ružové + ikona fajky v kruhu). Toast „Pridané do Idem" / „Odobrané z Idem" (~2 s) po stlačení. Cena vypadla z meta riadku dátumu/času.

2. **Rad menších tlačidiel** – Idem vypadol z radu, pribudlo „Na mape" (pin ikona). Volá `goToMap(venueId, date)`; ak akcia práve beží v nočnom režime, pošle `NIGHT_DAY`.

3. **Kalendár** – Na Androide (`/Android/i.test(navigator.userAgent)`) sa otvorí Google Kalendár URL s parametrami `action=TEMPLATE`, `text`, `dates` (pražský čas bez Z, koniec = `eventEndsAt`; celodenná `YYYYMMDD/YYYYMMDD+1`), `ctz=Europe/Prague`, `details`, `location`. Ostatné zariadenia: `.ics` ako doteraz. Nový súbor `web/src/core/calendar.ts`, testy v `calendar.test.ts` (5 testov – normálna akcia, prechod cez polnoc, celodenná, bez end_time, bez venue).

4. **Obnovenie potiahnutím** – `overscroll-behavior-y: contain` na `html, body` aj scroll kontajneroch v EventsPage/PlacesPage. Hook `usePullToRefresh` (touchstart/touchmove/touchend, threshold 70 px, max 120 px, `passive: false` na touchmove). Indikátor: tmavý krúžok so šípkou (ružová ak > threshold), počas obnovy sa točí spinner. Chyba siete: krátky toast „Nepodarilo sa obnoviť". `App.tsx` extrahoval `refreshData(noStore)`, ktorý pri `noStore=true` fetchuje `cache:'no-store'`.

5. **Späť zatvorí SelectorSheet všade** – história (pushState/popstate) presunnutá z `EventsPage` priamo do `SelectorSheet`. Pri otvorení `pushState({sheet:true})`, popstate = `onClose()`. Cleanup: ak sheet zatvára parent (item vybratý), `history.back()`. Backdrop: `history.back()` + `onClose()` bez dvojitého zatvárania (`historyPushedRef`). Testované: nebije sa s `pushState({panel:'open'})` v MapPage.

**Čísla z `site/events.json`** (príkaz: `python -c "import json; d=json.load(open('site/events.json',encoding='utf-8')); evs=d['events']; print('total:', len(evs), '| price_text:', len([e for e in evs if e.get('price_text')]), '| sold_out:', len([e for e in evs if e.get('sold_out')]), '| start_time:', len([e for e in evs if e.get('start_time')]), '| venues:', len(d['venues']))"`):
- Celkom akcií: **374**, venues: **11**
- S `price_text`: **0** (pipeline momentálne cenu neextrahuje)
- `sold_out`: **11** (testovanie sold_out štítku je vizuálne funkčné, len bez price_text)
- S `start_time`: **283** (zvyšok celodenné → Google Kalendár pošle celodenný event)

**Snímky:**
- `docs/tasks/046/01-akcia-cena-idem.jpg` – stránka akcie, Idem vypnuté (tmavé tlačidlo s +)
- `docs/tasks/046/02-akcia-vypredane-idem-zapnute.jpg` – stránka akcie, Idem zapnuté (ružové tlačidlo s fajkou + toast „Pridané do Idem")
- `03-akcie-potiahnutie.jpg` – vynechané; Playwright nemôže simulovať touch gesture v headless Chrome

**Ako Matej overí v telefóne:**

*Kalendár:* Na Androide otvor akciu so `start_time`, ťukni Kalendár → má sa otvoriť Google Kalendár s predvyplneným názvom, dátumom, časom a adresou. Na iPhone/desktope rovnaká akcia → má sa stiahnuť `.ics` súbor a otvoriť v Kalendári.

*Obnovenie potiahnutím:* Na Akciách alebo Miestach stiahni prstom nadol z vrchu zoznamu (nie počas scrollovania). Po ~70 px a pustení sa má objaviť spinner a zoznam sa prekreslí. Chrómové natívne obnovenie (tenký pásik hore) sa nesmie objaviť.

*Späť na mape:* Na mape otvor DaySelector (ťukni na deň v bare), ťukni Späť na telefóne → sheet sa má zatvoriť bez odchodu zo stránky.

**Otvorené / nedokončené:**
- `price_text` v `events.json` je prázdne – pipeline cenu neextrahuje, takže riadok s cenou sa nezobrazuje; Idem tlačidlo funguje aj bez ceny.
- `03-akcie-potiahnutie.jpg` nebola vytvorená (Playwright / headless bez touch support).
