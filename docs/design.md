# Design v1 (PWA)

Napísal hlavný chat 2026-11-09 podľa dizajnu, ktorý Matej schválil 2026-11-08 a 2026-11-09 (artefakt „EventApp – mapa“ na claude.ai, Code ho nevidí).

**Toto je záväzná predloha. Matej chce appku takmer 1:1 podľa nej.** Ak niečo v tomto súbore chýba alebo sa nedá spraviť, zastav sa a spýtaj sa, nevymýšľaj vlastné riešenie.

Podklady:
- `docs/design/screens/*.png`: snímky obrazoviek (390 × 844, @2x),
- `docs/design/html/*.html`: tie isté obrazovky ako statické HTML s presnými rozmermi, farbami, písmami a SVG ikonami. Pri pochybnosti o rozmere alebo farbe platí HTML.

Texty na snímkach sú po slovensky. Appka je primárne v češtine (SK a EN ako ďalšie jazyky). Údaje na snímkach (časy, ceny, dni, popisy) sú ilustračné.

## 1. Všeobecné

- **Tmavá appka**, hravá a farebná (inšpirácia Spotify, dating appky).
- **Písma:** nadpisy Bricolage Grotesque (500, 700), text Outfit (400–700), Google Fonts.
- **Appka tyká** („Pre teba“, „Hľadať miesto“).
- **Štítky (tagy) vždy po anglicky, malými písmenami**, bez ohľadu na jazyk appky (`party`, `dj`, `techno`, `queer-friendly`).
- **Spodná lišta je vždy viditeľná:** plávajúci tmavý pás (`#1C1C27`, výška 72, zaoblenie 36, 16 px od okrajov, 28 px od spodku). Aktívna záložka je ružová pilulka s ikonou a názvom, ostatné len sivé ikony. Záložky: **Mapa** (otvorí sa ako prvá), **Akcie**, **Miesta**, **Môj účet** (ikona osoby; vo v1 tam je zoznam „Idem“ a nastavenia).

### Farby
| Účel | Farba | Tmavá dvojica (text/ikona na farbe) |
|---|---|---|
| Pozadie appky | `#111118` | |
| Plochy (lišta, karty) | `#1C1C27` | |
| Neaktívne ovládanie | `#23232F` | text `#B9B6CC` |
| Text | `#F4F2FF` | sekundárny `#B9B6CC`, terciárny `#8E8AA6` |
| **Farba appky** (Filter, aktívna záložka, Obľúbené zapnuté, hlavné tlačidlo, obľúbené srdiečka) | `#FF4D8D` ružová | `#1A0710` |
| Typ **koncert** (`concert`) | `#8B6CFF` fialová | `#14063A` |
| Typ **párty** (`party`) | `#FF8A3D` oranžová | `#2A1200` |
| Typ **DJ** (`dj` bez `party`) | `#2FD4C0` tyrkysová | `#002B26` |
| Typ **kultúra** (`theatre`, `dance`, `talk`, `comedy`, `film`, `opening`, `workshop`, `quiz`) | `#C6F432` limetková | `#1B2600` |
| Žánrový štítok | `#2A2838` | `#E4DEFF` |
| Štítok charakteru miesta | priehľadný, obrys `#5D5677` 1,5 px | `#F4F2FF` |

**Pravidlo: farba nesie len typ akcie.** Ovládanie nikdy nepoužíva farbu typu. Biele (`#F4F2FF` s textom `#111118`) je tlačidlo Dnes, zapnuté Všetko, tlačidlo Moja poloha a vyhľadávacie pole.

**Typ akcie pre farbu a ikonu značky** (akcia môže mať viac formátov, rozhoduje prvé, čo platí): `party` → párty; inak `dj` → DJ; inak `concert` alebo `music` → koncert; inak formáty kultúry → kultúra; inak `other` → kultúra.

### Ikony
Obrysové, ťah 2 px, zaoblené konce. Koncert = ručný mikrofón, párty = koktailový pohár, DJ = gramofón, kultúra = divadelné masky. Presné SVG sú v `docs/design/html/`. Pri stavbe sa môže použiť hotová sada (Phosphor, Tabler) s rovnakými motívmi, ale **mikrofón, pohár, gramofón a masky musia ostať**.

## 2. Mapa (`01-mapa-piny.png`; prepracované 2026-11-09, staré pilulky `01-mapa.png` už neplatia)

- **Knižnica MapLibre GL JS, podklad OpenFreeMap** (bez kľúča). **Štýl: hotový overený tmavý štýl pre schému OpenMapTiles (napr. Dark Matter, licencia umožňuje úpravy), prefarbený do palety variantu A** (zem `#1E1E2A`, voda `#1D3352` všade rovnaká, parky `#1C2E24`, ulice `#34344A`/`#4A4A66`/`#5E5E7E`, text `#B4B0CC`). Vlastné skladanie štýlu po vrstvách sa nerobí (3 neúspešné pokusy). **Najväčšie oddialenie = celá Praha** (pri väčšom sú dáta dlaždíc zjednodušené). Popisy: štvrte, ulice, Vltava a ostrovy; **stanice metra a dôležité budovy ako malé sivé ikonky** (pozri nižšie Ikonky metra a budov). Farby liniek metra sa nepoužívajú (farba patrí len typom akcií).
- Mapa je **na celú obrazovku**, posúva sa **jedným prstom**, priblíženie dvoma. (Nie „dva prsty na posun“, to je pre mapy vložené v stránke.)
- **Na mape sú len miesta, ktoré majú akciu vo zvolenom dni.** Miesto bez akcie sa neukazuje.
- **Značka = pin** (kvapka so stredne ostrým hrotom dole, presný tvar v `01-mapa-piny.html`): plochý, vo farbe typu, **bez mena miesta a bez času**, v strede tmavý kruh 36 px s ikonou typu 22 px vo farbe typu. **Tieň pod pinom** (`drop-shadow`), aby pin pôsobil, že je nad mapou. Žiadne 3D prechody.
  - Obľúbené miesto: biely odznak 20 px vpravo hore s čiernym vyplneným srdiečkom.
  - Viac akcií v ten deň: tmavý odznak `+1`, `+2` vľavo hore (pozadie `#111118`, biely text a obrys).
  - **Akcia, ktorá už skončila, sa na mape neukazuje.** Skončená = má `end_time` a ten už uplynul. Ak koniec nepoznáme, akcia ostáva na mape do prepnutia dňa o 5:00 (nehádame, kedy skončila).
  - **Práve prebiehajúca akcia:** okolo kruhu pinu pulzuje žiara vo farbe typu (1,6 s, kód v `01-mapa-piny.html`, trieda `.pinlive`; pri `prefers-reduced-motion` statický prstenec).
  - **Vybraný pin** (po ťuknutí, `02-mapa-vybrany-pin-karta.png`): zmení sa na **pilulku vo farbe typu** (výška 48) s tmavým kruhom a ikonou a **menom miesta tmavým písmom** (+ srdiečko, ak je obľúbené), s **chvostom dole** na presnom bode. Ostatné piny sa nehýbu.
- **Animácie (Matej 2026-11-10: „živé, ale nie chaotické“):**
  - **Výber pinu:** pin sa plynule **rozšíri do pilulky** a meno sa vysunie (šírka a tvar 220 ms, `ease-out`, meno sa objaví s oneskorením ~80 ms). Zrušenie výberu = opačná animácia. Pri prepnutí na iný pin sa starý zbalí a nový rozbalí naraz.
  - **Karta** sa vysunie zdola (200 ms) a pri zatvorení zasunie; pri prepnutí miesta šípkou sa obsah karty len prelína, karta neodchádza.
  - **Zmena dňa alebo filtra:** nové piny sa jemne objavia (krátke zväčšenie z ~0,8 a zosvetlenie, 180 ms, mierne postupne), zmiznuté zmiznú. Žiadne poskakovanie ani padanie zhora.
  - Nič sa nehýbe samo okrem pulzu prebiehajúcej akcie. Pri `prefers-reduced-motion` sa animácie vypnú (okamžitá zmena).
- **Ikonky metra a budov:** použiť **existujúcu sadu ikon z mapových štýlov** (sprite tmavého štýlu, typicky Maki/Temaki, voľná licencia), nie vlastné kreslenie. Len vybrané triedy: stanice metra, vlakové stanice, divadlá, múzeá, pamiatky/landmarky (napr. Národní divadlo, Tančící dům). Tlmene sivé (ikona `#B9B6CC` na `#3A3A50` alebo podľa sprite), od priblíženia ~14 (metro od ~13), s riedkym rozostupom popisov, aby mapa bola živá, ale nie preplnená. Piny akcií musia byť vždy výraznejšie.
- **Žiadne zhlukovanie. Piny sa môžu prekrývať**, používateľ priblíži (Matej 2026-11-09; nahrádza pravidlo „žiadna značka nesmie zmiznúť“ a posúvanie nad seba so spojnicami). Ťuk na prekryté miesto vyberie vrchný pin.
- **Horná lišta** (16 px od okrajov, 56 px od vrchu, mriežka na celú šírku, všetky prvky **výška 44**):
  1. **Dnes ▾** (biele): výber **jedného dňa**. „Dnes“ sa prepína o 5:00 ráno (do 5:00 je „dnes“ ešte predošlý večer).
  2. Prepínač **Všetko | Obľúbené** (rovnako široké polovice, zapnutá polovica vypĺňa celú výšku): zapnuté Všetko = biele; zapnuté Obľúbené = ružové s **vyplneným čiernym srdiečkom**, vypnuté = obrys srdiečka.
  3. **Filter:** ružový kruh len s ikonou (bez textu), počet aktívnych filtrov ako biely odznak v rohu. Filter: formát (vrátane `party`), žáner, typ miesta, charakter, veľkosť; kombinovateľné. **Panel filtra zároveň slúži ako legenda:** typy akcií v ňom majú rovnakú farbu a ikonu ako značky. (Panel filtra ešte nie je nakreslený; navrhni ho v tomto štýle a ukáž Matejovi pred dokončením.)
- **Autorstvo mapy** (OpenFreeMap / OpenStreetMap) je povinné podľa licencie, nesmie sa odstrániť. Zobrazuje sa ako malá ikonka „i“, ktorá sa rozbalí po ťuknutí, umiestnená tak, aby nič neprekrývala (upravené 2026-11-09).
- **Moja poloha:** biely kruh 52 px vpravo nad spodnou lištou. Poloha len so súhlasom; bez súhlasu mapa funguje, iba bez vzdialeností.

## 3. Panel akcie na mape (`02-mapa-vybrany-pin-karta.png`)

- **Otvorí sa ťuknutím na pin** (nie potiahnutím). Je to **malá karta, ktorá pláva nad spodnou lištou** (12 px od okrajov, 112 px od spodku, `#1C1C27`, zaoblenie 28, obrys `#2E2D3C`). **Prvé ťuknutie mapu nepresúva ani necentruje.**
- Obsah: vľavo obrázok 88 × 88 (zaoblenie 18), vpravo názov akcie (Bricolage 21/700) a riadok „miesto · čas · vzdialenosť“; pod tým **jeden riadok štítkov akcie** (formáty vo farbe typu, potom žánre; výška 32, zaoblenie 16), vodorovne posúvateľný, pri pravom okraji sa rozplynie. **Štítky miesta (charakter) sa v karte neukazujú** (Matej 2026-11-09).
- **Viac akcií na mieste v ten deň:** potiahnutie karty doľava/doprava, bodky pod štítkami.
- **Šípky ‹ › na prechod na ďalšie miesto:** biele kruhy 36 px nad kartou (vľavo a vpravo). **Poradie podľa polohy, aby mapa neskákala: ‹ = najbližšie miesto na západ, › = najbližšie na východ** (zoradenie podľa zemepisnej dĺžky miest s akciou vo zvolenom dni a podľa filtra). Šípka vyberie pin ďalšieho miesta, otvorí jeho kartu a **plynulo posunie mapu** tak, aby bol pin vidieť. Na krajoch sa šípka skryje.
- **Pri otvorenej karte ostáva mapa plne ovládateľná** (posun, priblíženie, ťuk na iný pin prepne kartu); otvorenie ani zatvorenie karty nemení polohu mapy. **Späť** (systémové/prehliadač) kartu zavrie. Priblíženie dvoma prstami nikdy nezväčšuje celú appku.
- **Ťuknutie na kartu otvorí stránku akcie.**
- Chýba obrázok → ikona typu akcie na farebnom pozadí typu.

## 4. Akcie (`03-akcie-riadky.png`, `04-akcie-zoznam.png`)

Rozdelenie: **Mapa = konkrétny deň a teraz, Akcie = čo sa chystá.**
- Hore nadpis **Akcie** (Bricolage 32/700) a ružový **Filter** (rovnaký ako na mape).
- **Obdobie:** čipy **Dnes | Tento týždeň | Víkend | Mesiac** + ikona kalendára (vlastné dni). Zapnutý čip biely, ostatné `#23232F`. Predvolene Tento týždeň.
- **Bez prepínača Všetko | Obľúbené** (nahrádza ho riadok Pre teba).
- **Predvolene riadky ako Netflix**: nadpis riadku (Bricolage 22/700) + sivý podnadpis + šípka; pod ním vodorovne posúvateľné karty (148 px): štvorcový obrázok, „deň dátum · čas“ vo farbe typu, názov (2 riadky), **miesto tučne**. Riadky:
  - **Pre teba** (obľúbené miesta + žánre z onboardingu),
  - **Novo pridané** (akcie, ktoré pribudli za posledných 7 dní; treba dátum prvého výskytu akcie),
  - **Tento víkend**, **Zadarmo**, **Vypredáva sa** (len ak je dosť akcií),
  - podľa formátu/žánru: Koncerty, Párty, DJ, …
  - Riadok s menej ako 3 akciami sa neukazuje.
- **Ťuknutie na nadpis riadku alebo zapnutie filtra** prepne na **kompaktný zoznam** (`04`): hore aktívny štítok (napr. `party ✕`) a počet akcií, zoznam s nadpismi dní („STREDA 11. 11.“, veľké písmená, `#8E8AA6`), riadok = obrázok 72 × 72, čas vo farbe typu, názov, **miesto tučne**, max 3 štítky. Zrušenie štítku vráti riadky.
- Čo práve beží sa tu nezvýrazňuje.

## 5. Miesta (`05-miesta.png`)
- Nadpis **Miesta**. **Hlavný prvok je vyhľadávanie:** biele pole výšky 52 „Hľadať miesto“.
- Pod ním **Všetko | Obľúbené** (rovnaký prepínač ako na mape).
- Zoznam **abecedne**: okrúhla fotka 56, názov (Bricolage 17/700), 2 štítky charakteru, vpravo srdiečko (ružové vyplnené = obľúbené, inak obrys). Ťuk na srdiečko pridá/odoberie z obľúbených.

## 6. Profil miesta (`06-profil-miesta.png`)
- Hore fotka miesta (výška 200) so stmavnutím do pozadia, tlačidlo Späť a ružové srdiečko.
- Názov (Bricolage 34/700), „adresa · vzdialenosť“.
- **Popis miesta: 2 riadky hneď pod adresou, končí „…“, pod ním odkaz „Viac o mieste“**, ktorý popis rozbalí. (Miesta dnes popis v dátach nemajú, treba pole vo `venues.json`.)
- Štítky charakteru (obrys).
- **Program** hneď pod tým: dátum v stĺpci (deň v týždni, číslo, mesiac), názov, čas vo farbe typu, štítky, vpravo malý obrázok.
- Dole tlačidlá **Web**, **Instagram**, **Na mape**.
- Cieľ: nahradiť chodenie na web a IG miesta, takže program je najdôležitejší.

## 7. Stránka akcie (`07-stranka-akcie.png`)
- Hore **veľký obrázok** (štvorec cez celú šírku) so stmavnutím; tlačidlo **„Plagát“** otvorí obrázok na celú obrazovku (často je to oficiálny plagát).
- Názov (Bricolage 28/700), **miesto s odkazom na profil**, „deň dátum · čas · cena“ (cena a vypredané len ak ich zdroj dáva), **len štítky akcie** (formáty, žánre). Štítky miesta tu nie sú (Matej 2026-11-09), patria do profilu miesta.
- **Hlavné tlačidlo (ružové, výška 54): Lístky**, ak má akcia `ticket_url`; inak **Stránka akcie** (pôvodný zdroj). Zdroj musí byť dostupný vždy.
- Pod tým štyri menšie tlačidlá: **Idem** (CZ „Jdu“; zoznam v Môj účet), **Kalendár** (`.ics`), **Zdieľať**, **IG miesta**.
- **Popis akcie** pod tým.

## 8. Čo nie je nakreslené (navrhni v rovnakom štýle a ukáž Matejovi)
Panel filtra, výber dňa (Dnes ▾), kalendár vlastných dní, Môj účet / zoznam Idem, onboarding, prázdne stavy (žiadne akcie v deň, žiadne obľúbené), načítavanie a offline.
