# 046: Stránka akcie (cena, Idem, Na mape), kalendár, obnovenie potiahnutím

## Zadanie

Robí sa po 045.

**Čítaj:** `design.md` časť 7 (posledné dva odseky „Zmena 2026-11-16“ a „Kalendár (2026-11-16)“) a v časti 4 riadok „Obnovenie potiahnutím“. V kóde: `web/src/pages/EventPage.tsx`, `core/store.ts` (Idem), `core/events.ts` (`eventEndsAt`), súbor, ktorý dnes robí `.ics` (`grep -rn "ics\|VCALENDAR" web/src`), `App.tsx` (`goToMap`, načítanie `events.json`), `pages/EventsPage.tsx` a `pages/PlacesPage.tsx` (scroll kontajnery), `index.html` / `styles/global.css`.

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

### Overenie
- `npm test`, `npm run build`, číslo nasadenia.
- Snímky Playwright do `docs/tasks/046/`: `01-akcia-cena-idem.jpg` (s rozsahom ceny), `02-akcia-vypredane-idem-zapnute.jpg`, `03-akcie-potiahnutie.jpg` (koliesko počas ťahania, ak sa dá nasimulovať; inak vynechaj a napíš).
- V reporte, ako si Matej overí kalendár a obnovenie potiahnutím v telefóne.

## Report
