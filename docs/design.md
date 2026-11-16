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

## 2. Mapa (`01-mapa-piny-mena.png`, `02-mapa-vybrany-pin-ziara.png`; prepracované 2026-11-10, staré `01-mapa.png`, `01-mapa-piny.png`, `02-mapa-panel.png`, `02-mapa-vybrany-pin-karta.png` už neplatia)

- **Knižnica MapLibre GL JS, podklad OpenFreeMap** (bez kľúča). **Štýl: hotový overený tmavý štýl pre schému OpenMapTiles (napr. Dark Matter, licencia umožňuje úpravy), prefarbený do palety variantu A** (zem `#1E1E2A`, voda `#1D3352` všade rovnaká, parky `#1C2E24`, ulice `#34344A`/`#4A4A66`/`#5E5E7E`, text `#B4B0CC`). Vlastné skladanie štýlu po vrstvách sa nerobí (3 neúspešné pokusy). **Najväčšie oddialenie = celá Praha** (pri väčšom sú dáta dlaždíc zjednodušené). Popisy: štvrte, ulice, Vltava a ostrovy; **stanice metra a dôležité budovy ako malé sivé ikonky** (pozri nižšie Ikonky metra a budov). Farby liniek metra sa nepoužívajú (farba patrí len typom akcií).
- Mapa je **na celú obrazovku**, posúva sa **jedným prstom**, priblíženie dvoma. (Nie „dva prsty na posun“, to je pre mapy vložené v stránke.)
- **Na mape sú len miesta, ktoré majú akciu vo zvolenom dni.** Miesto bez akcie sa neukazuje.
- **Značka = pin** (kvapka so stredne ostrým hrotom dole, presný tvar v `01-mapa-piny-mena.html`): plochý, vo farbe typu, bez času, v strede tmavý kruh 36 px s ikonou typu 22 px vo farbe typu. **Tieň pod pinom** (`drop-shadow`), aby pin pôsobil, že je nad mapou. Žiadne 3D prechody.
  - Obľúbené miesto: biely odznak 20 px vpravo hore s čiernym vyplneným srdiečkom.
  - Viac akcií v ten deň: tmavý odznak `+1`, `+2` vľavo hore (pozadie `#111118`, biely text a obrys).
  - **Akcia, ktorá už skončila, sa na mape neukazuje.** Skončená = podľa pravidla „Kedy akcia beží“ (nižšie, Matej 2026-11-16).
  - **Práve prebiehajúca akcia:** okolo kruhu pinu pulzuje žiara vo farbe typu (1,6 s, kód v `01-mapa-piny.html`, trieda `.pinlive`; pri `prefers-reduced-motion` statický prstenec).
  - **Meno miesta pod pinom** (Matej 2026-11-10): Outfit 12/600, `#E4E2EE`, tmavý obrys textu, od priblíženia ~13 (pri celej Prahe bez mien). Pri kolízii mien sa skryje meno s nižšou prioritou (priorita: vybraný > prebiehajúca akcia > obľúbené > ostatné); **pin sa nikdy neskryje**.
  - **Vybraný pin** (po ťuknutí, `02-mapa-vybrany-pin-ziara.png`): **zväčší sa (1,22×, od hrotu) a dostane jemnú žiaru vo farbe typu**, meno pod ním biele a tučné (13/800). **Žiadna pilulka, žiadny biely obrys, žiadna bodka.** Vybraný pin je **vždy navrchu** (nad ostatnými pinmi aj menami).
- **Animácie (Matej 2026-11-10: „živé, ale nie chaotické“):**
  - **Výber pinu:** plynulé zväčšenie a objavenie žiary (220 ms, `ease-out`); **zrušenie výberu = opačná animácia** (zmenšenie, žiara zmizne). Pri prepnutí na iný pin (ťuknutím alebo šípkou) sa starý zmenší a nový zväčší naraz.
  - **Karta** sa pri prvom otvorení vysunie zdola (150 ms) a pri zatvorení zasunie. **Pri prepnutí šípkou alebo na iný pin sa karta nehýbe, len sa okamžite vymení obsah** (animuje sa len pin). (Matej 2026-11-10)
  - **Zmena dňa alebo filtra:** nové piny sa jemne objavia (krátke zväčšenie z ~0,8 a zosvetlenie, 180 ms, mierne postupne), zmiznuté zmiznú. Žiadne poskakovanie ani padanie zhora.
  - Nič sa nehýbe samo okrem pulzu prebiehajúcej akcie. Pri `prefers-reduced-motion` sa animácie vypnú (okamžitá zmena).
- **Ikonky:** **len stanice metra** (Matej 2026-11-10: ostatná doprava robí chaos), tlmene sivé (ikona metra zo sprite prefarbená na `#B9B6CC` na `#3A3A50`, alebo sivý kruh s „M“), s názvom, od priblíženia ~13. Divadlá, múzeá a pamiatky ako sivé ikonky od ~15, bez barov, reštaurácií a obchodov. Názov budovy bez ikony sa neukazuje.
- **Žiadne zhlukovanie. Piny sa môžu prekrývať**, používateľ priblíži (Matej 2026-11-09; nahrádza pravidlo „žiadna značka nesmie zmiznúť“ a posúvanie nad seba so spojnicami). Ťuk na prekryté miesto vyberie vrchný pin.
- **Horná lišta** (16 px od okrajov, 56 px od vrchu, mriežka na celú šírku, všetky prvky **výška 44**):
  1. **Deň ▾** (biele, **šírka podľa textu**, text vždy krátky: „Dnes“, „Zajtra“, „So 15. 11.“, „V noci“). Výber dňa = panel zdola: **5 možností dní** (v noci „V noci“ + 4 dni), ako šiesta **„Iný dátum“**; všetko viditeľné bez posúvania a nad spodnou lištou → malý mesačný kalendár v štýle appky, aktívne len dni v rozsahu dát (dni bez akcií stlmené).
     **Štýl panelu (Matej 2026-11-15):** rovnaký ako panel obdobia v Akciách (`11-akcie-obdobie.png`, časť 4): nadpis „Deň“ (Bricolage 20/700), riadky 48 px so zaoblením 24, vybraný deň = biela pilulka (`#F4F2FF`, text `#111118` 600), ostatné `#F4F2FF` 500, vpravo sivý dátum 13 px (`#8E8AA6`; pri „Teraz v noci“ nič (koniec sa mení, zmena 2026-11-16), pri Dnes/Zajtra dátum, pri ďalších dňoch nič), posledná položka **Iný dátum** s ikonou kalendára. Obsah a správanie ostávajú.
     - **Noc (nočný režim, zmena 2026-11-16):** medzi 0:00 a 7:00, **len kým beží aspoň jedna akcia z noci** (podľa „Kedy akcia beží“); ak nebeží nič, nočný režim nie je a „Teraz v noci“ sa v ponuke vôbec neukáže; o 7:00 vždy koniec. V nočnom režime je prvá a **predvolená** možnosť je **„Teraz v noci“** v paneli (na tlačidle krátko „V noci“; EN „Late night now“ / „Late night“; zmena 2026-11-15); po polnoci sa mapa do tohto režimu prepne sama. Obsah: akcie, ktoré **ešte bežia** podľa pravidla „Kedy akcia beží“ nižšie (koncerty a kultúra bez konca v noci prakticky nie). Pod „V noci“ nasleduje „Dnes“ (nový deň večer), „Zajtra“… Keď nočný režim skončí (skončí posledná nočná akcia, najneskôr o 7:00), „Teraz v noci“ zmizne a mapa sa prepne na Dnes. Ak po polnoci nič nebeží, mapa rovno ukáže Dnes (nový deň).
  2. Prepínač **Všetko | Obľúbené** zaberá zvyšok lišty (Filter má pevnú šírku 44); text sa nikdy neoreže ani nezalomí – pri nedostatku miesta sa zmenší okraj, potom zmizne srdiečko pri vypnutých Obľúbených, potom písmo najviac na 13 px (Matej 2026-11-10), tmavý kontajner `#23232F`, rovnako široké polovice: zapnuté Všetko = biele; zapnuté Obľúbené = ružové s **vyplneným čiernym srdiečkom**, vypnuté = obrys srdiečka.
  3. **Filter:** ružový kruh len s ikonou (bez textu), počet aktívnych filtrov ako biely odznak v rohu. Filter: formát (vrátane `party`), žáner, typ miesta, charakter, veľkosť; kombinovateľné. **Panel filtra zároveň slúži ako legenda:** typy akcií v ňom majú rovnakú farbu a ikonu ako značky. (Panel filtra ešte nie je nakreslený; navrhni ho v tomto štýle a ukáž Matejovi pred dokončením.)
- **Autorstvo mapy** (OpenFreeMap / OpenStreetMap) je povinné podľa licencie, nesmie sa odstrániť. Zobrazuje sa ako malá ikonka „i“, ktorá sa rozbalí po ťuknutí, umiestnená tak, aby nič neprekrývala (upravené 2026-11-09).
- **Kompas** (Matej 2026-11-10): keď je mapa otočená, **priamo nad tlačidlom polohy** sa ukáže biely kruh 44 px s ihlou (sever ružový); ťuk otočí mapu späť na sever a kompas zmizne.
- **Moja poloha:** biely kruh 52 px vpravo nad spodnou lištou. Poloha len so súhlasom; bez súhlasu mapa funguje, iba bez vzdialeností.
- **Úvodný pohľad** (Matej 2026-11-10): appka o polohu sama nežiada (len po stlačení tlačidla polohy). Ak je poloha už povolená a používateľ je do ~2 km od miesta s akciou vo zvolenom dni, mapa ukáže jeho polohu spolu s najbližšími akciami; inak centrum Prahy so všetkými akciami dňa.
- **Stav mapy sa zachováva:** pri prechode na stránku akcie, inú záložku alebo do pozadia a späť ostane mapa presne ako bola (poloha, priblíženie, otočenie, deň, filter, vybraný pin a karta).
- ~~**Akcie mimo obrazovky** (odznaky na okrajoch)~~ **zrušené 2026-11-10** (Matej: prekrývali sa so šípkami). Náhrada: počty pri šípkach karty (časť 3).
- **Vrstvy:** piny (aj vybraný) sú vždy **pod** ovládaním appky (horná lišta, karta, šípky, tlačidlá, spodná lišta, odznaky).
- **Vybraný pin pod ovládaním:** ak je vybraný pin (alebo jeho meno) zakrytý kartou, hornou lištou alebo tlačidlami, mapa sa plynule posunie len o toľko, aby bol vo voľnej časti (ako Google Maps). Inak sa mapa pri výbere nehýbe.
- **Miesta tesne pri sebe:** polohy sú skutočné (Fuchs2 a Bike Jesus z obrysu budovy v OSM). Ak sú dva piny na obrazovke bližšie ako ~20 px, zobrazia sa vodorovne mierne od seba (prekrytie asi do polovice, ako Google Maps), hroty pri ich bodoch. **Rozostúpenie mien len ak sa mená naozaj prekrývajú** (napr. Roxy a EPIC majú iný zvislý rozostup, tam nič). **Dvojica s prekrývajúcimi sa menami** (Fuchs2 + Bike Jesus) má **jedno spoločné meno** „Bike Jesus · Fuchs2“ (západ · východ) vycentrované pod dvojicou. **Po výbere** jedného z nich sa ukáže **len meno vybraného, rovno pod jeho pinom** (bez posunu). (Matej 2026-11-10) Pravidlá kolízií s ostatnými menami platia ďalej. (Matej 2026-11-10: skryť jedno z mien dvojice nie je riešenie.)
- **Karta sa zachováva aj pri návrate zo stránky akcie** (rovnaké miesto a akcia).

**Kedy akcia beží (platí pre pulz aj zobrazenie na mape, v Akciách a v Jdu; Matej 2026-11-16):**
- so známym koncom: od začiatku do konca;
- bez konca, `party`/`dj` alebo miesto `late-night`: do **zatvorenia miesta** v daný deň (pole `closing` miesta, `data-model.md`), ak ho nepoznáme, **do 3:00** (radšej akciu nezobraziť, než poslať človeka pred zatvorený podnik);
- bez konca, ostatné: **3 hodiny** od začiatku;
- bez času začiatku: beží celý deň do 3:00 (nepulzuje).
Skončená akcia z mapy aj zo zoznamov zmizne. Akcia z predošlého dňa sa zobrazuje najneskôr do 7:00 (koniec nočného režimu), aj keby jej koniec alebo zatvorenie bolo neskôr.

## 3. Panel akcie na mape (`02-mapa-vybrany-pin-karta.png`)

- **Otvorí sa ťuknutím na pin** (nie potiahnutím). Je to **malá karta, ktorá pláva nad spodnou lištou** (12 px od okrajov, 112 px od spodku, `#1C1C27`, zaoblenie 28, obrys `#2E2D3C`). **Prvé ťuknutie mapu nepresúva ani necentruje.**
- Obsah: vľavo obrázok 88 × 88 (zaoblenie 18), vpravo názov akcie (Bricolage 21/700) a riadok „miesto · čas · vzdialenosť“; pod tým **jeden riadok štítkov akcie** (formáty vo farbe typu, potom žánre; výška 32, zaoblenie 16), vodorovne posúvateľný, pri pravom okraji sa rozplynie. **Štítky miesta (charakter) sa v karte neukazujú** (Matej 2026-11-09).
- **Viac akcií na mieste v ten deň:** potiahnutie karty doľava/doprava, bodky pod štítkami.
- **Šípky ‹ › na prechod na ďalšie miesto:** biele kruhy **40 px** nad kartou (vľavo a vpravo). **Poradie podľa polohy, aby mapa neskákala: ‹ = najbližšie miesto na západ, › = najbližšie na východ** (zoradenie podľa zemepisnej dĺžky miest s akciou vo zvolenom dni a podľa filtra). Šípka vyberie pin ďalšieho miesta, otvorí jeho kartu a **plynulo posunie mapu** tak, aby bol pin vidieť. **Na krajoch je šípka sivá a neaktívna** (ťuk nič neurobí, karta sa nezavrie). **Pri každej šípke jemný odznak s počtom miest** s akciou ďalej tým smerom (malý tmavý krúžok `#111118` s bielym číslom 11/700 v rohu šípky; pri 0 šípka sivá bez odznaku). (Matej 2026-11-10)
- **Pri otvorenej karte ostáva mapa plne ovládateľná** (posun, priblíženie, ťuk na iný pin prepne kartu); otvorenie ani zatvorenie karty nemení polohu mapy. **Späť** (systémové/prehliadač) kartu zavrie. Priblíženie dvoma prstami nikdy nezväčšuje celú appku.
- **Ťuknutie na kartu otvorí stránku akcie.**
- Chýba obrázok → ikona typu akcie na farebnom pozadí typu.

## 4. Akcie (`10-akcie-mriezka.png`, `11-akcie-obdobie.png`, `12-akcie-hladanie.png`; prepracované 2026-11-15, staré `03-akcie-riadky.png` a `04-akcie-zoznam.png` už neplatia)

Jeden zoznam akcií (mriežka) a nad ním filtre, ktoré sa dajú ľubovoľne kombinovať: **kedy** (práve jedno obdobie) a **čo** (Pre teba, Nové, Filter, hľadanie). Riadky ako Netflix nie sú.

**Hlavička** (odsadenie 52 px zhora, 16 px zo strán, medzery 14 px):
- Nadpis **Akcie** (Bricolage 32/700) a vpravo okrúhle tlačidlo **lupy** 44 px (`#23232F`, ikona `#F4F2FF`).
- **Hľadanie:** ťuk na lupu → biele pole 44 px (zaoblenie 22, ikona lupy, text 15/500, kurzor `#FF4D8D`) sa roztiahne od lupy doľava cez nadpis, lupa sa zmení na krížik. Animácia 200 ms (šírka + priehľadnosť nadpisu), oboma smermi; **nič pod hlavičkou sa neposúva**. Klávesnica sa otvorí hneď. Hľadá sa v názve akcie, mene miesta a štítkoch (bez diakritiky, bez ohľadu na veľkosť písmen). Počas hľadania sa obdobie samo prepne na **Kedykoľvek** (vidno v lište); po zavretí hľadania sa vráti predošlé obdobie a text sa vymaže. Pre teba, Nové a Filter platia aj pri hľadaní.
- **Lišta:** biele tlačidlo **obdobia** 44 px s šípkou (rovnaké ako „Dnes ▾“ na mape), čipy **Pre teba** (ikona iskier, nie srdiečko) a **Nové** (40 px, vypnuté `#23232F` / `#B9B6CC`, zapnuté ružové `#FF4D8D` / `#1A0710`), vpravo ružový **Filter** 44 px (rovnaký ako na mape, s odznakom počtu). Filter je vždy na mieste; pás čipov (Pre teba, Nové) **sa dá posúvať prstom vodorovne** (aj v kompaktnej lište), na okraji, kde obsah pokračuje, sa stráca. Čip a odznak „Nové“ sa vždy zobrazujú anglicky **„new“** (ako štítky).
- **Riadok pod lištou** (13 px, `#8E8AA6`): vľavo počet („12 akcií · 3 pre teba“; pri zapnutom Pre teba „9 akcií pre teba“), vpravo **Zoradiť: dátum ▾** (hodnota `#F4F2FF` 600). Pri **Kedykoľvek** sa počet nezobrazuje (vľavo nič, vpravo len Zoradiť).
- **Pri scrolle (`13-akcie-zbalene.png`, Matej 2026-11-15):** nadpis a riadok s počtom/zoradením odídu so zoznamom; hore ostane prilepená **kompaktná lišta** (pozadie `#111118`, tieň nadol): obdobie, Pre teba, Nové, **lupa** (okrúhla 44 px `#23232F`, presunie sa sem z hlavičky) a Filter. Pri scrolle naspäť navrch sa hlavička rozbalí. Ťuk na lupu v kompaktnej lište: zoznam sa vyroluje navrch, hlavička sa rozbalí a otvorí sa hľadanie.
- **Zmena = navrch:** po akejkoľvek zmene (obdobie, Pre teba, Nové, filter, zoradenie, text hľadania) sa zoznam plynulo vyroluje navrch a hlavička sa rozbalí.
- **Šípka navrch:** okrúhle tlačidlo 44 px (`#23232F`, biela šípka nahor, tieň) vpravo 16 px, nad spodnou lištou (spodok 116 px); objaví sa po odscrollovaní ~2 výšok obrazovky (prelínanie 150 ms), ťuk → plynulý scroll navrch, potom zmizne. Rovnako v Miestach (časť 5).
- **Ťuk na aktívnu záložku** v spodnej lište (Akcie, Miesta) vyroluje zoznam navrch.
- **Štítok `alternative` sa zobrazuje ako `alt`** všade v appke (len zobrazenie, v dátach ostáva `alternative`).

**Noc v Akciách (Matej 2026-11-16):** počas nočného režimu (rovnako ako na mape: 0:00–7:00, len kým niečo z noci beží) je v paneli obdobia prvá a predvolená možnosť **„Teraz v noci“** (na tlačidle „V noci“) s rovnakým obsahom ako na mape; **Dnes** = nový kalendárny deň (ako na mape). Keď nočný režim skončí, možnosť zmizne a ak bola vybraná, prepne sa na Dnes.

**Obdobie** (panel zdola ako výber dňa na mape, `11`): nadpis „Obdobie“, prvá položka **Kedykoľvek** s ikonou nekonečna a textom „všetky akcie“, oddelená čiarou od ostatných; potom **Dnes**, **Zajtra**, **Tento víkend**, **Najbližších 7 dní**, **Najbližších 30 dní** (vpravo sivý rozsah dátumov), **Iný dátum** (ikona kalendára → mesačný kalendár ako na mape, výber intervalu: prvý ťuk začiatok, druhý koniec; dvakrát ten istý deň = jeden deň). Vybraná položka = biela pilulka. Rovnaký štýl panelu má od 2026-11-15 aj výber dňa na mape (časť 2). Na tlačidle krátky text: „Dnes“, „Zajtra“, „Víkend“, „7 dní“, „30 dní“, „Kedykoľvek“, „20.–24. 11.“
- **Dnes = kalendárny deň od polnoci** (zmena 2026-11-16, nahrádza hranicu dňa o 5:00 z 2026-11-03); čo z predošlého večera ešte beží, ukazuje nočný režim. **Tento víkend** = piatok až nedeľa; po–št najbližší víkend, pi–ne zvyšok aktuálneho. **7 a 30 dní** sú posuvné od dneška vrátane.
- **Predvolene Dnes**; appka si pamätá naposledy vybrané obdobie (lokálne).

**Pre teba:** akcia v obľúbenom mieste alebo so žánrom/štítkom z preferencií používateľa (preferencie zatiaľ nie sú, dovtedy len obľúbené miesta). Vypnuté = všetky akcie, akcie pre teba majú na obrázku odznak **pre teba**. Zapnuté = len akcie pre teba.
**Nové:** akcia s `first_seen` za posledných 7 dní. Na obrázku biely odznak **nové**; zapnutý čip ukáže len nové.

**Zoradenie** sa vyberá **malou ponukou priamo pod „Zoradiť“** (dve položky, rýchly výber, nie panel zdola; Späť ju zatvorí; Matej 2026-11-16 večer): **dátum** (predvolené; pri jednodňovom období – Dnes, Zajtra, Iný dátum s jedným dňom – sa volá **čas**, radí sa rovnako podľa dátumu a času začiatku) a **vzdialenosť** (len s povolenou polohou). **Bez nadpisov dní** pri akomkoľvek období a zoradení: mriežka ide súvisle bez medzier v riadkoch, dátum nesie každá karta (Matej 2026-11-15). Cena príde po doplnení cien v dátach.
- **Vzdialenosť len pri jednodňovom období** (Dnes, Zajtra, Teraz v noci, Iný dátum s jedným dňom; Matej 2026-11-16). Pri viacdňovom období sa voľba neukáže a ak bola vybraná, zoradenie sa vráti na dátum.
- **Panely (obdobie, deň na mape, kalendár, zoradenie)** sú vždy nad celou obrazovkou (nie v posúvanom zozname), samy sa neposúvajú a pod nimi sa zoznam nehýbe; **Späť ich zatvorí** (nevracia o stránku). V paneli obdobia má Kedykoľvek rovnakú výšku riadku ako ostatné, deliaca čiara má len malý odstup. **Žiadne veľké prázdne plochy v paneloch** (Matej 2026-11-16 večer): panel prekryje aj spodnú lištu, pod poslednou položkou len bežný okraj + bezpečná oblasť telefónu; platí pre výber dňa na mape aj obdobie v Akciách.
- **Hľadanie** má v prázdnom poli text „Hľadať akciu“ (CZ „Hledat akci“, EN „Search events“).
- **Obnovenie potiahnutím (Akcie, Miesta, 2026-11-16):** vlastné v appke – po potiahnutí navrchu zoznamu sa ukáže koliesko s **kruhovou šípkou obnovenia** (nie šípkou nadol), ktoré ide s prstom a pri ťahaní sa otáča podľa vzdialenosti (ako v Gmaile/Chrome) a appka znova stiahne `events.json` bez načítania stránky (bez pásika prehliadača); natívne obnovenie Chromu vypnuté (`overscroll-behavior-y: contain` na dokumente). Funguje pri akomkoľvek počte akcií.

**Mriežka:** 3 stĺpce, medzera 8 px vodorovne, 16 px zvisle, karty zarovnané hore (výška podľa obsahu, žiadna prázdna medzera pod krátkym názvom). Karta:
- štvorcový **obrázok** (zaoblenie 12) – náhľad obrázka akcie; bez obrázka plocha vo farbe typu s ikonou typu. Odznaky: vľavo hore **pre teba** (tmavý `#111118`, iskry + text 10/600), vpravo hore **nové** (biely).
- **dátum · čas** (12/500), celé sivé `#8E8AA6` (zmena 2026-11-16: farbu nesie štítok typu, nie čas). Dátum vždy, pri dnešku a zajtrajšku slovom: „Dnes · 20:00“, „Zajtra · 22:00“, inak „Pi 20. 11. · 23:00“.
- **názov** (13/700 `#F4F2FF`, normálne písmo, nie veľké písmená, max. 2 riadky, potom „…“), **miesto** (12/400 `#8E8AA6`, 1 riadok s „…“) – názov výrazne, miesto tlmene (Matej 2026-11-16, variant B).
- **štítky** priamo **na obrázku** (spodok-ľavý roh, 6 px od okraja): výška 18, 10/500, zaoblenie 9, text `#F4F2FF`. **Štítok typu** (prvý) **plnou farbou typu s tmavým textom** (tmavá dvojica typu, 10/600; biely text by bol na limetkovej a oranžovej nečitateľný) – čitateľný na svetlej aj tmavej fotke (zmena 2026-11-16 večer; priesvitný nebol čitateľný na bielych fotkách); ostatné štítky pozadie `rgba(17,17,24,0.9)`. Na pravom okraji obrázka sa strácajú.
- Ťuk na kartu → stránka akcie. Čo práve beží, sa tu nezvýrazňuje.

**Prázdny stav:** „Na dnes nič nemáme.“ + tlačidlo „Pozrieť 7 dní“ (pri inom období „Skúsiť Kedykoľvek“); pri zapnutom Pre teba / Nové / filtri tlačidlo „Zrušiť filtre“.

## 5. Miesta (`05-miesta.png`)
- Šípka navrch a ťuk na aktívnu záložku ako v Akciách (časť 4).
- Nadpis **Miesta**. **Hlavný prvok je vyhľadávanie:** biele pole výšky 52 „Hľadať miesto“.
- Pod ním **Všetko | Obľúbené** (rovnaký prepínač ako na mape).
- Zoznam **abecedne**: okrúhla fotka 56, názov (Bricolage 17/700), 2 štítky charakteru, vpravo srdiečko (ružové vyplnené = obľúbené, inak obrys). Ťuk na srdiečko pridá/odoberie z obľúbených.

## 6. Profil miesta (`06-profil-miesta.png`)
- Hore fotka miesta (výška 200) so stmavnutím do pozadia, tlačidlo Späť a ružové srdiečko.
- Názov (Bricolage 34/700), „adresa · vzdialenosť“.
- **Popis miesta: 2 riadky hneď pod adresou, končí „…“, pod ním odkaz „Viac o mieste“**, ktorý popis rozbalí. (Miesta dnes popis v dátach nemajú, treba pole vo `venues.json`.)
- Pod názvom, adresou a popisom rad tlačidiel v štýle stránky akcie (tmavé `#1C1C27`, zaoblenie 18, ikona + popis): **Web**, **Instagram**, **Navigovať** (Google Maps trasa na miesto). Tlačidlo bez údaja sa neukáže. „Na mape“ sa ruší. (Matej 2026-11-10)
- Štítky charakteru (obrys).
- **Srdiečko vpravo hore:** nezapnuté = biely kruh s tmavým obrysom srdiečka, zapnuté = ružový kruh s vyplneným tmavým srdiečkom.
- **Program** hneď pod tým: dátum v stĺpci (deň v týždni, číslo, mesiac), názov, čas vo farbe typu, štítky, vpravo malý obrázok. **Viac akcií v ten istý deň:** dátumový stĺpec sa ukáže raz, **zvislo vycentrovaný na celú skupinu** akcií toho dňa. **Štítky akcie:** v jednom riadku koľko sa zmestí, posledný sa rozplynie v rovnakom bode (zarovnane s koncom názvu), bez posúvania. **Rozsah:** najprv ~20 akcií, potom tlačidlo „Zobraziť viac“ (ďalších 20).
- ~~Dole tlačidlá Web, Instagram, Na mape~~ (presunuté hore, 2026-11-10).
- Cieľ: nahradiť chodenie na web a IG miesta, takže program je najdôležitejší.

## 7. Stránka akcie (`07-stranka-akcie.png`)
- Hore **veľký obrázok** (štvorec cez celú šírku) so stmavnutím; tlačidlo **„Plagát“** otvorí obrázok na celú obrazovku (často je to oficiálny plagát); **Späť** zväčšenie zavrie a ostane na stránke akcie.
- Názov (Bricolage 28/700), **miesto s odkazom na profil**, „deň dátum · čas“, **len štítky akcie** (formáty, žánre). Štítky miesta tu nie sú (Matej 2026-11-09), patria do profilu miesta.
- **Hlavné tlačidlo (ružové, výška 54): Lístky**, ak má akcia `ticket_url`; inak **Stránka akcie** (pôvodný zdroj). Zdroj musí byť dostupný vždy.
- Pod tým štyri menšie tlačidlá: **Idem** (CZ „Jdu“; zoznam v Môj účet), **Kalendár** (`.ics`), **Zdieľať**, **IG miesta**.
- **Zmena 2026-11-10 (Matej):** namiesto „IG miesta“ tlačidlo **Spotify** (logo Spotify, otvorí vyhľadávanie interpreta / názvu akcie na Spotify, `https://open.spotify.com/search/<dopyt>`; presné párovanie s interpretom neskôr) a nové tlačidlo **Navigovať** (Google Maps trasa na miesto). IG miesta je na profile miesta. **Cena alebo rozsah cien** všade, kde ju zdroj dáva (`price_text`).
- **Popis akcie** pod tým.
- **Zmena 2026-11-16 (Matej):** pod štítkami **riadok s cenou a Idem**: vľavo cena presne podľa zdroja (`price_text`, aj rozsah „250–390 Kč“, „zadarmo“, „dobrovoľné“; bez slova „vstupné“), 17/600 `#F4F2FF`; pri `sold_out` cena prečiarknutá sivou a vedľa štítok **vypredané** (pozadie `#3A1420`, text `#FF8FB0`, 12/600). Bez ceny sa zobrazí len Idem. Vpravo **Idem** = okrúhle tlačidlo 40 px bez textu: vypnuté `#1C1C27` s vnútorným obrysom `#5D5677` a ikonou **plus v kruhu**, zapnuté ružové `#FF4D8D` s ikonou **fajky v kruhu** (`#1A0710`); po ťuknutí krátka správa dole „Pridané do Idem“ / „Odobrané z Idem“ (~2 s); `aria-label`. Pod tým hlavné tlačidlo (Lístky / Stránka akcie, pravidlá bez zmeny) na celú šírku a rad menších tlačidiel: **Kalendár, Zdieľať, Spotify, Na mape, Navigovať** (Idem z radu vypadlo). **Na mape** prepne na záložku Mapa s dňom akcie (alebo „Teraz v noci“, ak akcia práve beží v nočnom režime) a vybraným miestom.
- **Kalendár (2026-11-16):** na Androide otvorí Google Kalendár s predvyplnenou akciou (`https://calendar.google.com/calendar/render?action=TEMPLATE&text=…&dates=…/…&ctz=Europe/Prague&details=…&location=…`; koniec podľa „Kedy akcia beží“, ak ho zdroj nedáva); na iOS a ostatných ostáva súbor `.ics`.

- **Zmena 2026-11-16 večer (Matej, nahrádza predošlé dva odseky v bodoch rozloženia, ikony a kalendára):**
  - **„Idem“ → „Uložené“ / „Moje akcie“** (CZ „Uloženo“ / „Moje akce“, EN „Saved“ / „My events“): menej záväzné ako „idem“. Tlačidlo = okrúhle 40 px s ikonou **záložky** (vypnuté: obrys záložky na `#1C1C27` s vnútorným obrysom `#5D5677`; zapnuté: plná záložka `#1A0710` na ružovej `#FF4D8D`). Toast „Uložené do Moje akcie“ / „Odobrané z Moje akcie“. Zoznam v Môj účet sa volá „Moje akcie“.
  - **Rozloženie podľa údajov:** (a) **je cena** → riadok cena + záložka vpravo (ako doteraz); (b) **nie je cena, je vypredané** → nižší riadok so štítkom „vypredané“ vľavo a záložkou vpravo; (c) **nie je cena ani vypredané** → žiadny riadok navyše, záložka je vpravo na **riadku štítkov** (štítky vľavo, ak sa nezmestia, zalomia sa pod záložku). Nikde prázdna plocha len so záložkou.
  - **Rad menších tlačidiel v poradí:** Spotify, Kalendár, Zdieľať, Na mape, Navigovať.
  - **Kalendár na Androide:** najprv systémové „pridať udalosť“ (výber kalendárnej appky v telefóne); ak sa nič neotvorí, stiahne sa `.ics`. Odkaz na calendar.google.com sa nepoužíva (v PWA otvára web).

## 7b. Filter (`09-filter.png`, Matej 2026-11-10)
- Panel zdola (výška ~85 % obrazovky, `#1C1C27`, zaoblenie hore 28), nad stmavenou mapou/zoznamom. Nadpis **Filter**, vpravo „Zrušiť všetko“. Obsah sa posúva, tlačidlo dole je stále viditeľné.
- **Typ akcie:** Koncert, Párty, DJ, Kultúra ako čipy s ikonou typu; zapnutý = plná farba typu, vypnutý = farebný obrys a farebná ikona. **Slúži zároveň ako legenda farieb.**
- **Žáner:** 12 najčastejších + „Všetky (N) ›“ rozbalí ostatné. **Charakter miesta**, **Veľkosť miesta** (Malé / Stredné / Veľké).
- Zapnutý neutrálny čip = biely s tmavým textom, vypnutý `#2A2838`.
- **Počet pri každom čipe** (malý odznak vpravo v čipe): koľko výsledkov by bolo pri aktuálnom dni/období, Všetko | Obľúbené a ostatných zapnutých filtroch, ak by sa pridal tento čip. Na mape = počet **miest** s akciou, v Akciách = počet **akcií**. **Čip s 0 je stlmený, ale dá sa zapnúť** (filter sa pri zmene dňa zachováva a v iný deň môže mať výsledky).
- **Filter sa zachováva** pri zmene dňa/obdobia a pri prepínaní medzi Mapou a Akciami (jeden spoločný filter). **Nikdy sa sám nevypína.**
- **Prázdny výsledok** (napr. zapnuté `latin` a zajtra žiadne): mapa/zoznam ukáže nenápadnú kartu nad spodnou lištou: „Pre tento filter zajtra nič.“ a dve tlačidlá: **„Najbližšie: Pi 14. 11. ›“** (prepne na najbližší deň s výsledkom, ak je v rozsahu dát) a **„Zrušiť filter“**.
- **Zapnutý filter je vidieť len odznakom s počtom** zapnutých štítkov na tlačidle Filter (Matej 2026-11-10; riadok štítkov pod lištou nie je).
- **Zapnutý štítok s 0 výsledkami ostáva zapnutý** (napr. `latin` po prepnutí na zajtra): v paneli je biely (zapnutý) s počtom 0 a stlmený, ťukom sa dá vypnúť. Filter ho nikdy sám neodstráni.
- **Typ akcie je predvolene celý zapnutý** (Matej 2026-11-10): všetky 4 typy plné. Používateľ typy **vypína**, ak chce zúžiť (napr. len DJ = vypne ostatné). Posledný zapnutý typ sa vypnúť nedá (nikdy nie je vypnuté všetko). Ostatné skupiny (žáner, charakter, veľkosť) sú predvolene vypnuté a **zapínajú sa**.
- **Kombinovanie:** v rámci skupiny = **ALEBO** (techno alebo post-punk), medzi skupinami = **A** (zapnuté typy a zvolené žánre a zvolený charakter). Príklad: všetky typy + techno + post-punk = všetky techno a post-punk akcie (koncerty aj DJ); vypnutý koncert a kultúra + techno = len techno párty/DJ. Štítok s 0 preto nevyprázdni výsledok, ak sú v skupine aj iné zapnuté so zhodou. Počet pri čipe sa počíta podľa tohto pravidla.
- **Odznak na tlačidle Filter** = počet zapnutých štítkov (žáner, charakter, veľkosť) + 1, ak sú niektoré typy vypnuté. Predvolený stav (všetky typy, žiadne štítky) = bez odznaku. „Zrušiť všetko“ vráti predvolený stav.
- **Poradie čipov:** Typ akcie má pevné poradie (legenda). **Žáner a Charakter** zoradené podľa počtu výsledkov (najviac prvé, 0 na koniec). Poradie sa určí **pri otvorení panela** a počas klikania sa nemení (čipy neskáču pod prstom); zapnuté čipy ostávajú tam, kde sú. Do 12 viditeľných žánrov sa berú tie s najväčším počtom.
- Dole ružové tlačidlo **„Zobraziť N akcií“** (na mape „Zobraziť N miest“). Počet aktívnych filtrov ako odznak na tlačidle Filter v lište.

## 8. Čo nie je nakreslené (navrhni v rovnakom štýle a ukáž Matejovi)
Výber dňa a kalendár (urobené v 028/029 bez kresby), Môj účet / zoznam Idem, onboarding, prázdne stavy (žiadne akcie v deň, žiadne obľúbené), načítavanie a offline.
