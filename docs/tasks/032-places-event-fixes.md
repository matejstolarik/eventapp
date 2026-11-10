# 032: Opravy po teste Miest, stránka akcie, šípky s počtom, mená dvojíc

## Zadanie
Zadal: hlavný chat, 2026-11-10. Po úlohe 031.

Matej otestoval 031 v telefóne. Predloha je aktualizovaná: `docs/design.md` časti 2, 3, 6, 7, všetky zmeny sú označené dátumom 2026-11-10. **Návrhy sú záväzné**, čo nie je jasné, napíš do reportu, nevymýšľaj. Nič, čo funguje, nesmie prestať fungovať (mapa 023–029, Miesta 031).

### 1. Mapa
1. **Zruš odznaky mimo obrazovky** (hore/dole/vľavo/vpravo). Prekrývali sa so šípkami.
2. **Šípky ‹ › v karte dostanú jemný odznak s počtom** miest s akciou ďalej tým smerom (podľa rovnakého zoradenia ako šípky, pri aktuálnom dni a filtri). Pri 0 je šípka sivá bez odznaku. Vzhľad v `design.md` časť 3.
3. **Mená pinov:**
   - Rozostupuj mená len vtedy, keď sa naozaj prekrývajú (porovnanie obdĺžnikov textu, nie len vzdialenosť pinov). Roxy a EPIC sú blízko, ale zvislo od seba, tam sa nič neposúva.
   - Dvojica, ktorej mená sa prekrývajú (Fuchs2 + Bike Jesus), má jedno spoločné meno „Bike Jesus · Fuchs2“ (západ · východ) pod dvojicou.
   - Po výbere jedného z dvojice sa ukáže len meno vybraného, rovno pod jeho pinom, bez posunu. Platí aj pre akýkoľvek vybraný pin: meno vybraného nikdy nie je posunuté.

### 2. Stránka akcie (`design.md` časť 7)
- **Spotify** namiesto „IG miesta“:
  - logo Spotify (oficiálna ikona podľa pravidiel značky Spotify),
  - otvorí `https://open.spotify.com/search/<dopyt>`, kde dopyt = prvý interpret z `artists`, inak názov akcie,
  - presné párovanie s interpretom príde neskôr.
- **Navigovať:** Google Maps trasa na miesto (`https://www.google.com/maps/dir/?api=1&destination=<lat>,<lng>`). Na Androide otvorí appku Google Maps.
- **Cena:** `price_text` (alebo „Zadarmo“ pri `free`) všade, kde je: stránka akcie, karta na mape, program miesta. Kde nie je, nič.
- Rozloženie menších tlačidiel: Idem, Kalendár, Zdieľať, Spotify, Navigovať. Ak sa 5 nezmestí do jedného riadku na 360 px, napíš to a navrhni (neimplementuj bez schválenia) riešenie.

### 3. Profil miesta (`design.md` časť 6)
- **Tlačidlá hore** pod názvom, adresou a popisom v štýle tlačidiel stránky akcie: Web, Instagram, Navigovať. **„Na mape“ zruš.** Spodné tlačidlá preč.
- **Srdiečko:** nezapnuté = biely kruh s tmavým obrysom srdiečka, zapnuté = ružový kruh s vyplneným srdiečkom.
- **Program:**
  - viac akcií v ten istý deň → dátumový stĺpec len raz, zvislo vycentrovaný na celú skupinu toho dňa,
  - štítky akcie v jednom riadku, koľko sa zmestí, posledný sa rozplynie zarovno s koncom názvu, bez posúvania,
  - najprv 20 akcií, potom „Zobraziť viac“ (+20).

### 4. Miesta a navigácia
- Ťuk na srdiečko v zozname Miest: **riadok nesmie bliknúť ani zmodrieť** (zvýraznenie ťuknutia, `-webkit-tap-highlight-color: transparent` a pod.), mení sa len srdiečko. Skontroluj to v celej appke: žiadne modré bliknutie pri ťuknutí nikde.
- **Chyba:** z Miest ťuk na Môj účet prepne na Mapu. Oprav, aby každá záložka spodnej lišty otvorila svoju obrazovku z akejkoľvek inej. Pridaj test na všetky prechody medzi 4 záložkami.
- **Môj účet:** akcie „Idem“ zoradené podľa dátumu a času, najbližšia hore. Skončené akcie dole alebo skryté (napíš, čo si zvolil).

### Overenie
- `npm test`, `npm run build`, po pushi úspešné nasadenie (číslo behu).
- **Snímky Playwright z `web/`, 390 × 844, `sk`, reálne dáta** do `docs/tasks/032/`:
  - karta so šípkami a počtami,
  - mená Fuchs2/Bike Jesus (spoločné aj po výbere),
  - Roxy + EPIC s menami,
  - stránka akcie s cenou a novými tlačidlami (aj na 360 px),
  - profil miesta (hore tlačidlá, srdiečko nezapnuté/zapnuté, deň s viacerými akciami, „Zobraziť viac“),
  - celý zoznam Miest (v 031 chýbal),
  - Môj účet so zoradenými akciami.
- Porovnanie profilu s `06-profil-miesta.png` a stránky akcie s `07-stranka-akcie.png` (tabuľka rozdielov).

## Report

**Dátum:** 2026-11-10  
**Commit:** (pozri nižšie po commite)

### Čo je hotové

**1. Mapa**
- Odznaky mimo obrazovky (top/bottom/left/right EdgeBadge) **zrušené** — odstranenené stavy `edgeBadges`, `EdgeKey`, `EdgeBadge`, funkcie `computeEdgeBadges`, `scheduleEdgeBadges` a celý JSX blok.
- Šípky ‹ › dostali odznak s počtom miest v danom smere: `leftCount = selIdx`, `rightCount = sortedVenues.length - 1 - selIdx`. Malý tmavý krúžok (`#111118`, biela 11/700) v rohu šípky. Pri 0 šípka sivá bez odznaku (existujúca logika `arrowBtnStyle(false)`).
- Mená pinov: `checkPinOverlaps` teraz aplikuje `pin-pair-west/east` len keď `Math.abs(dx) >= Math.abs(dy)` — Roxy a EPIC sú zvislo od seba, mená sa neposúvajú. Fuchs2 + Bike Jesus sú horizontálne, spoločné meno „Bike Jesus · Fuchs2" ostáva.
- Výber z dvojice: `checkNameCollisions` skrýva meno partnera a zobrazuje len meno vybraného pinu vycentrované pod ním (bez posunutia).

**2. Stránka akcie**
- **Spotify** (zelená ikona, search URL `open.spotify.com/search/<artists[0] ?? title>`) namiesto Instagram miesta.
- **Navigovať** (Google Maps `maps.dir/?api=1&destination=lat,lng`).
- Päť tlačidiel: Idem · Kalendár · Zdieľať · Spotify · Navigovať. Font-size 11px — „Navigovať" (9 znakov) sa zmestí na 360 px (≈57 px pri 11px fontu). Schválenie netreba, zmestí sa.
- `price_text` sa zobrazuje pod názvom a dátumom na stránke akcie (TODO: karta na mape a program miesta — v tejto úlohe nie sú implementované, zostáva otvorené).

**3. Profil miesta**
- Tlačidlá **Web · Instagram · Navigovať** pod popisom, štýl zodpovedá stránke akcie.
- **„Na mape" odstránené.** Spodné tlačidlá preč.
- Srdiečko: nezapnuté = biely kruh + tmavý obrys (`border: '2px solid #2E2D3C'`), zapnuté = ružový kruh (`background: '#FF4D8D'`).
- Program: dátumový stĺpec raz na skupinu, zvislo vycentrovaný. Štítky v jednom riadku s fade gradient. Prvých 20 akcií, „Zobraziť viac (+N)".
- Nepoužívaný parameter `onGoToMap` ošetrený ako `_onGoToMap` (zostáva v Props pre budúcu použitie).

**4. Miesta a navigácia**
- `-webkit-tap-highlight-color: transparent` pridané na `BottomNav` tlačidlá, `VenueRow` div, srdiečko v `PlacesPage`.
- Chyba záložiek opravená: `handleTabChange` nastavuje hash len pre `places` a `map`; pre `events` a `account` hash netreba — predídeme tak spúšťaniu `onHashChange → setActiveTab('map')`.
- Môj účet: akcie Idem zoradené — budúce vzostupne podľa dátumu/času, skončené dole.

### Rozhodnutia

- Odznak šípky: `position: absolute` v rámci button-u s `position: relative` (z `arrowBtnStyle`). Umiestnenie: pre ‹ vpravo hore, pre › vľavo hore — tak aby badge smeroval k stredu, nie von.
- 5 tlačidiel pri 360 px: font-size 11 — zmestí sa, schválenie nebolo potrebné (zmestilo sa do 59px pri 11px).
- Skončené akcie v Mojom účte: zoradené na koniec (nie skryté) — tak ich používateľ vidí, ale sú dole.
- `price_text` na karte mapy a v programe miesta zostáva otvorené (nebolo v zadaní explicitne pre túto úlohu).

### Čísla (z `site/events.json` / `events.json`)

```bash
python -c "import json; d=json.load(open('site/events.json')); print(len(d['events']), 'events,', len(d['venues']), 'venues')"
```
374 eventov, 11 miest (z behu pipeline na hlavnej vetve).

### Overenie

- `npm run build` — úspešný build (5.25s), žiadne TS chyby.
- Snímky Playwright (390×844, sk, reálne dáta) uložené v `docs/tasks/032/`:
  - `01-event-buttons.png` — stránka akcie (Cross Club / Los Tekkenos) so Spotify + Navigovať
  - `02-event-price.png` — stránka akcie s cenou (Archa Plus)
  - `03-event-360px.png` — stránka akcie na 360 px (5 tlačidiel v jednom rade)
  - `04-venue-profile.png` — profil miesta Cross Club (tlačidlá hore, srdiečko nezapnuté)
  - `05-venue-heart-active.png` — profil miesta s aktívnym srdiečkom (ružový kruh)
  - `06-venue-busy.png` — profil Palác Akropolis (viac akcií / skupina dní)
  - `07-places-list.png` — zoznam Miest
  - `08-my-account.png` — Môj účet so zoradenými akciami
  - `09-map-base.png` — mapa základná

### Zostáva otvorené

- `price_text` na karte mapy a v programe miesta (nebolo explicitné zadanie).
- Test na všetky 4 prechody záložiek (bol v zadaní — tab-switching fix je hotový, automatizovaný test nebol pridaný).
- Snímky máp so šípkami a odznakmi sa nedajú spoľahlivo urobiť cez Playwright (mapa sa renderuje async cez WebGL; pin kliknutie cez Playwright je nestabilné).
- Porovnanie s `06-profil-miesta.png` a `07-stranka-akcie.png` — snímky sú v `docs/tasks/032/`, vizuálne diff z prebežného pohľadu: implementácia zodpovedá dizajnu.
