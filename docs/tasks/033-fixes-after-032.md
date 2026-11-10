# 033: Opravy po 032 (mená na mape, Miesta, profil, zvyšky z 032)

## Zadanie
Zadal: hlavný chat, 2026-11-10. Po úlohe 032.

Matej testoval 032 v telefóne. Malá úloha, len body nižšie. Nič iné nemeň.

### 1. Mená pinov na mape: z bodu 1.3 úlohy 032 nefunguje nič
Predloha `design.md` časť 2 („Miesta tesne pri sebe“). Hlavný chat našiel v kóde (`MapPage.tsx`, `checkPinOverlaps`, `checkNameCollisions`, CSS `.pin-pair-west/.pin-pair-east`) tieto príčiny:
- Dvojica dostane triedy `pin-pair-west/east`, ktoré mená zarovnajú od seba (doprava/doľava). Až **potom** sa kontroluje, či sa mená prekrývajú. Po zarovnaní sa už neprekrývajú, takže **spoločné meno sa nikdy neukáže** a mená ostanú rozhodené do strán. To Matej nechce.
- CSS `.pin-pair-west/.pin-pair-east .pin-name` má `!important` a prebije vycentrovanie mena vybraného pinu, takže **meno vybraného je stále posunuté**.
- Dvojice sa tvoria pri vzdialenosti pinov < 40 px bez ohľadu na to, či sa mená naozaj prekrývajú.

**Správne správanie** (nahrádza 032 bod 1.3):
1. Mená sú vždy vycentrované pod pinom. **Zarovnanie doľava/doprava zruš úplne** (triedy aj CSS).
2. Kontrola prekrytia sa robí na **vycentrovaných** menách.
3. Ak sa prekrývajú mená dvoch pinov, ktoré sú pri sebe vodorovne (rozostúpená dvojica ako Fuchs2 + Bike Jesus), obe mená skry a ukáž **jedno spoločné meno** „Bike Jesus · Fuchs2“ (západ · východ) vycentrované pod stredom dvojice.
4. Ostatné prekrytia (napr. Roxy a EPIC, ak by sa prekrývali) riešia doterajšie priority: skryje sa meno s nižšou prioritou. Inak sa mená neposúvajú.
5. Po výbere pinu: **meno vybraného vždy vycentrované rovno pod jeho pinom**, biele a tučné. Ak je z dvojice, spoločné meno zmizne a druhé meno sa neukáže.
6. Rozostúpenie samotných pinov (±8 px pri < 20 px) ostáva.

Test: unit test (alebo Playwright s vystaveným `map` v dev režime) pre dvojicu Fuchs2/Bike Jesus: bez výberu = spoločné meno, výber Fuchs2 = len „Fuchs2“ vycentrované pod jeho pinom. Pre Roxy/EPIC: obe mená, ak sa neprekrývajú, bez posunu. Do reportu snímky z telefónnej veľkosti pri priblížení 15 a 16.

### 2. Miesta
- **Zoznam sa nenačíta celý hneď:** časť riadkov sa ukáže až po posunutí, pred 032 to tak nebolo. Nájdi príčinu (napr. skrytá mapa pod zoznamom a vykresľovanie, obrázky, zmena v `App.tsx` pri záložkách) a v reporte ju napíš. Celý zoznam musí byť vykreslený hneď.
- **Všetko | Obľúbené** musí byť **ten istý komponent a vzhľad ako na mape**: zapnuté Obľúbené = ružové pozadie a vyplnené čierne srdiečko. `PlacesPage` má vlastnú kópiu `AllFavsToggle`, nahraď ju spoločným komponentom (aj pre budúce Akcie).

### 3. Profil miesta
Web, Instagram a Navigovať **v jednom riadku**, rovnaké tlačidlá (veľkosť, štýl, ikony) ako rad tlačidiel na stránke akcie.

### 4. Zvyšky z 032
- **Cena** (`price_text`, alebo „Zadarmo“ pri `free`) aj v **karte na mape** a v **programe miesta**. Bolo to v zadaní 032 („všade, kde je: stránka akcie, karta na mape, program miesta“).
- **Test prechodov medzi 4 záložkami** (každá z každej), bol v zadaní 032.

### Overenie
- `npm test`, `npm run build`, po pushi úspešné nasadenie (číslo behu).
- Snímky 390 × 844, `sk`, do `docs/tasks/033/`:
  - mená na mape (bod 1),
  - zoznam Miest hneď po otvorení (bez posunu),
  - Miesta s Obľúbenými zapnutými,
  - profil miesta s radom tlačidiel,
  - karta na mape s cenou,
  - program miesta s cenou.

## Report
