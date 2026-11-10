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
