# 025: Podklad mapy v troch variantoch, spojnice, štítky v karte, autorstvo

## Zadanie
Zadal: hlavný chat, 2026-11-09. Po úlohe 024.

Matej v telefóne po 024: mapa je stále „strašne čierna, nič na nej nevidno, len Vltavu“. Na snímkach z 024 nie sú žiadne popisy (štvrte, ulice, metro). Tentoraz si Matej vyberie podklad podľa oka priamo v telefóne. Predloha: `docs/design.md` (upravená 2026-11-09: štítky v karte, spojnice, autorstvo).

### 1. Prečo chýbajú popisy (najprv zistiť)
Zisti a v reporte potvrď, prečo sa nezobrazujú žiadne textové popisy. Možné príčiny:
- vlastný štýl nemá `glyphs` (písma pre texty, OpenFreeMap ich poskytuje),
- vrstvy symbolov majú zlé `source-layer` alebo filtre podľa schémy dlaždíc OpenFreeMap (OpenMapTiles, nie Protomaps),
- `minzoom`.

Over schému dlaždíc, ktoré OpenFreeMap naozaj poskytuje (vrstvy `place`, `transportation_name`, `water_name`, `poi` / `transit` a pod.).

### 2. Tri varianty podkladu, prepínateľné v telefóne
Sprav tri štýly a prepínač cez adresu: `…/eventapp/?map=a`, `?map=b`, `?map=c` (výber sa zapamätá v `localStorage`, aby Matej mohol appku nainštalovanú používať s vybraným variantom). Predvolený je `a`. Prepínač je dočasný, po výbere sa nechá len vybraný.

Vo všetkých troch variantoch:
- **Popisy:**
  - štvrte (Karlín, Holešovice, Žižkov, Smíchov…) od priblíženia ~11,
  - hlavné ulice od ~13, ostatné ulice od ~15,
  - Vltava a ostrovy,
  - **stanice metra so značkou metra a názvom od ~12**.

  Písmo čitateľné, text s tmavým obrysom.
- **Ulice jasne viditeľné** aj pri pohľade na celé centrum (hlavné ťahy hrubšie a svetlejšie ako vedľajšie).
- Bez obchodov, reštaurácií a ostatných bodov záujmu.
- **Značky akcií ostanú na podklade najvýraznejšie.** Over to na snímke so značkami.

Orientačné palety (dolaď pre čitateľnosť a výsledné hodnoty uveď v reporte):

| | A · tmavá čitateľná | B · tmavomodrá (ako tmavý režim navigácií) | C · svetlejšia sivá |
|---|---|---|---|
| zem | `#1E1E2A` | `#1B2230` | `#2A2A36` |
| voda | `#1D3352` | `#0E1828` (tmavšia ako zem) | `#22406A` |
| parky | `#1C2E24` | `#1A2A2A` | `#26392C` |
| budovy | `#252532` | `#222B3A` | `#32323F` |
| vedľajšie ulice | `#34344A` | `#2D3A4F` | `#45455A` |
| hlavné ulice | `#4A4A66` | `#3F5070` | `#5C5C78` |
| najväčšie cesty | `#5E5E7E` | `#526688` | `#727294` |
| text | `#B4B0CC` | `#A4B3CC` | `#D0CCE2` |

### 3. Spojnica posunutej pilulky (`design.md` časť 2)
Keď sa pilulka kvôli prekrytiu posunie, nakresli tenkú čiaru (2 px, farba typu) od pilulky k bodke (8 px, farba typu, tmavý okraj) na skutočnom mieste.

### 4. Štítky v karte akcie (`design.md` časť 3)
- 1. riadok: štítky akcie (formáty vo farbe typu, potom žánre).
- 2. riadok: štítky miesta (charakter, obrys).
- Každý riadok je vodorovne posúvateľný a pri pravom okraji sa štítky rozplynú do priehľadnosti. Karta má stálu výšku.
- Rovnako na stránke akcie: štítky akcie a štítky miesta v dvoch oddelených riadkoch (tam môžu byť zalomené, nie posúvateľné).

### 4b. Správanie mapy pri otvorenej karte (Matej 2026-11-09, doplnené pred odovzdaním)
Dnes, keď sa po ťuknutí na pilulku otvorí karta, mapa „zamrzne“: nedá sa posúvať, priblíženie dvoma prstami zväčšuje celú appku (stránku) namiesto mapy a na iné miesto sa dá prepnúť až po zavretí karty, čo navyše vráti mapu do pôvodnej polohy. Matej chce, aby **všetko ostalo tak, ako je, a len sa zobrazila karta**:
- Pri otvorenej karte sa mapa dá ďalej **posúvať a približovať** (žiadna vrstva cez mapu, ktorá zachytáva dotyky; karta zachytáva dotyky len na svojej ploche).
- **Priblíženie dvoma prstami nikdy nezväčšuje celú appku**, ani pri otvorenej karte, ani inde (viewport a `touch-action` nastav tak, aby sa stránka nezväčšovala; priblíženie patrí len mape a plagátu na celú obrazovku).
- **Ťuknutie na inú pilulku pri otvorenej karte rovno prepne kartu** na to miesto.
- Otvorenie ani zatvorenie karty **nemení polohu ani priblíženie mapy** (žiadne automatické presúvanie a vracanie mapy). Ak je vybraná pilulka pod kartou, mapa sa môže jemne posunúť, aby bola vidieť, ale pri zatvorení sa nevracia.
- **Tlačidlo Späť** (systémové na Androide, gesto späť, tlačidlo Späť v prehliadači) kartu zavrie a ostane na mape. Na stránke akcie Späť vráti na mapu s otvorenou kartou v rovnakom stave. (Otvorenie karty pridá záznam do histórie.)
- Ťuknutie na prázdne miesto mapy kartu zavrie (ako doteraz).
- Over v Playwright s dotykovou emuláciou (otvorená karta → posun mapy → ťuk na inú pilulku → Späť) a daj do reportu výsledok.

### 5. Autorstvo mapy
Licencia OpenStreetMap/OpenFreeMap vyžaduje autorstvo, **odstrániť sa nesmie**. Zobraz ho ako malú ikonku „i“ (kompaktné autorstvo MapLibre), ktorá sa rozbalí po ťuknutí. Umiestni ju tak, aby neprekrývala značky ani tlačidlá (napr. vpravo hore pod lištou alebo vľavo nad spodnou lištou).

### 6. Overenie (v 023 aj 024 chýbalo, tentoraz povinné)
- **Snímky:** pre každý variant mapa pri troch priblíženiach (celá Praha, centrum so značkami, ulica). Plus karta akcie so štítkami v dvoch riadkoch a spojnica pri prekrytí. Všetko v slovenčine (nastav jazyk prehliadača `sk`), do `docs/tasks/025/`.
- **Inštalácia:** výstup kontroly manifestu (napr. Lighthouse PWA alebo kontrola v Chromium: `name`, ikony 192/512, `display: standalone`, `start_url`, service worker zaregistrovaný).
- **Offline:** Playwright `context.setOffline(true)` → appka sa načíta s poslednými dátami a ukáže informáciu, z kedy sú. Daj snímku.
- **Odkaz na akciu:** otvorenie `#/akcia/<id>` v novej karte → stránka akcie. Neexistujúce id → „Akcia už prebehla“. Daj snímky.
- Ak niečo overiť nejde, napíš presne prečo. Nepíš „hotovo“ bez dôkazu.

### Report navyše
- Príčina chýbajúcich popisov (potvrdená).
- Odkazy na tri varianty pre Mateja (`?map=a|b|c`) a krátky opis, čím sa líšia.

## Report
