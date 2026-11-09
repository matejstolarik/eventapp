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

## 2. Mapa (`01-mapa.png`)

- **Knižnica MapLibre GL JS, podklad OpenFreeMap** (bez kľúča). Štýl podkladu **tmavý, ale čitateľný** (upravené 2026-11-09 po teste v telefóne: pôvodné farby z kresby mali na skutočnej mape príliš malý kontrast). Paleta a vrstvy podľa úlohy 024: vidno ulice, Vltavu, parky; **ostávajú názvy štvrtí, hlavných ulíc, Vltavy a ostrovov a stanice metra**; preč sú obchody, reštaurácie a ostatné body záujmu. Značky akcií musia byť na podklade najvýraznejšie.
- Mapa je **na celú obrazovku**, posúva sa **jedným prstom**, priblíženie dvoma. (Nie „dva prsty na posun“, to je pre mapy vložené v stránke.)
- **Na mape sú len miesta, ktoré majú akciu vo zvolenom dni.** Miesto bez akcie sa neukazuje.
- **Značka = pilulka vo farbe typu akcie:** výška 40, zaoblenie 20, vľavo tmavý kruh 32 px s ikonou typu vo farbe typu, potom názov miesta (Outfit 15/600, tmavá dvojica). **Bez času.**
  - Obľúbené miesto: za názvom malé **vyplnené srdiečko** v tmavej farbe dvojice.
  - Viac akcií v ten deň: za názvom odznak `+1`, `+2` (pozadie `#23232F`, text `#F4F2FF`).
  - **Akcia, ktorá už skončila, sa na mape neukazuje** (Matej 2026-11-09: sivé pilulky nemajú pre používateľa hodnotu). Skončená = má `end_time` a ten už uplynul. Ak koniec nepoznáme, akcia ostáva na mape do prepnutia dňa o 5:00 (nehádame, kedy skončila).
  - **Práve prebiehajúca akcia:** okolo pilulky prstenec vo farbe typu s tmavou medzerou (`box-shadow: 0 0 0 4px #111118, 0 0 0 8px <farba>`) a **pulzujúca žiara** (animácia 1,6 s, presný kód v `01-mapa.html`, trieda `.live`). Bez štítku „teraz“. Pri `prefers-reduced-motion` statický prstenec.
  - **Vybraná značka** (po ťuknutí): pilulka zosvetlí na `#F4F2FF` s tmavým textom, zväčší sa (scale 1,12) a dostane tieň; ikona ostáva v kruhu farby typu (`02-mapa-panel.png`).
- **Žiadne zhlukovanie (clustering).** Pri oddialení sa značky zmenšia na farebné body (26 px, biely okraj 3 px), názvy sa ukazujú tam, kde je miesto.
- **Dve značky sa nikdy nespájajú do jednej a žiadna nesmie zmiznúť.** Ak sa prekrývajú (napr. Fuchs2 a Bike Jesus na Štvanici, rovnaký bod v OSM), posunú sa nad seba, každá s vlastnou farbou a ikonou (`01-mapa.png`).
  - **Posunutá pilulka má spojnicu k skutočnému bodu** (upravené 2026-11-09): tenká čiara 2 px vo farbe typu od pilulky k malej bodke (8 px, farba typu, tmavý okraj) na presnom mieste, aby bolo vidno, kde miesto naozaj je.
- **Horná lišta** (16 px od okrajov, 56 px od vrchu, mriežka na celú šírku, všetky prvky **výška 44**):
  1. **Dnes ▾** (biele): výber **jedného dňa**. „Dnes“ sa prepína o 5:00 ráno (do 5:00 je „dnes“ ešte predošlý večer).
  2. Prepínač **Všetko | Obľúbené** (rovnako široké polovice, zapnutá polovica vypĺňa celú výšku): zapnuté Všetko = biele; zapnuté Obľúbené = ružové s **vyplneným čiernym srdiečkom**, vypnuté = obrys srdiečka.
  3. **Filter:** ružový kruh len s ikonou (bez textu), počet aktívnych filtrov ako biely odznak v rohu. Filter: formát (vrátane `party`), žáner, typ miesta, charakter, veľkosť; kombinovateľné. **Panel filtra zároveň slúži ako legenda:** typy akcií v ňom majú rovnakú farbu a ikonu ako značky. (Panel filtra ešte nie je nakreslený; navrhni ho v tomto štýle a ukáž Matejovi pred dokončením.)
- **Autorstvo mapy** (OpenFreeMap / OpenStreetMap) je povinné podľa licencie, nesmie sa odstrániť. Zobrazuje sa ako malá ikonka „i“, ktorá sa rozbalí po ťuknutí, umiestnená tak, aby nič neprekrývala (upravené 2026-11-09).
- **Moja poloha:** biely kruh 52 px vpravo nad spodnou lištou. Poloha len so súhlasom; bez súhlasu mapa funguje, iba bez vzdialeností.

## 3. Panel akcie na mape (`02-mapa-panel.png`)

- **Otvorí sa ťuknutím na značku** (nie potiahnutím). Je to **malá karta, ktorá pláva nad spodnou lištou** (12 px od okrajov, 112 px od spodku, `#1C1C27`, zaoblenie 28, obrys `#2E2D3C`), nie panel z boku ani na celú obrazovku.
- Obsah: vľavo obrázok 88 × 88 (zaoblenie 18), vpravo názov akcie (Bricolage 21/700) a riadok „miesto · čas · vzdialenosť“; pod tým **štítky v dvoch riadkoch** (výška 32, zaoblenie 16; upravené 2026-11-09): **1. riadok štítky akcie** (formáty vo farbe typu, potom žánre), **2. riadok štítky miesta** (charakter ako obrys). Každý riadok je jeden, **vodorovne posúvateľný**, a pri pravom okraji sa štítky **rozplynú** (prechod do priehľadnosti), aby bolo vidno, že ich je viac. Karta tak má vždy rovnakú výšku.
- **Pri otvorenej karte ostáva mapa plne ovládateľná** (posun, priblíženie, ťuk na inú pilulku prepne kartu); otvorenie ani zatvorenie karty nemení polohu mapy. **Späť** (systémové/prehliadač) kartu zavrie. Priblíženie dvoma prstami nikdy nezväčšuje celú appku. (Matej 2026-11-09)
- **Ťuknutie kdekoľvek na kartu otvorí stránku akcie.** Ak má miesto v ten deň viac akcií, karta ukáže prvú a dá sa listovať (doplniť po dohode s Matejom).
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
- Názov (Bricolage 28/700), **miesto s odkazom na profil**, „deň dátum · čas · cena“ (cena a vypredané len ak ich zdroj dáva), štítky.
- **Hlavné tlačidlo (ružové, výška 54): Lístky**, ak má akcia `ticket_url`; inak **Stránka akcie** (pôvodný zdroj). Zdroj musí byť dostupný vždy.
- Pod tým štyri menšie tlačidlá: **Idem** (CZ „Jdu“; zoznam v Môj účet), **Kalendár** (`.ics`), **Zdieľať**, **IG miesta**.
- **Popis akcie** pod tým.

## 8. Čo nie je nakreslené (navrhni v rovnakom štýle a ukáž Matejovi)
Panel filtra, výber dňa (Dnes ▾), kalendár vlastných dní, Môj účet / zoznam Idem, onboarding, prázdne stavy (žiadne akcie v deň, žiadne obľúbené), načítavanie a offline.
