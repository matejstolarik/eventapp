# 034: Mená pinov: spájať len pri značnom prekrytí, spoločné meno ako súčasť mapy

## Zadanie
Zadal: hlavný chat, 2026-11-10. Po úlohe 033.

**Čítaj:** `design.md` časť 2 (len odsek „Miesta tesne pri sebe“), `web/src/pages/MapPage.tsx`: CSS `.pin-name`, `.pin-combined-name`, `.map-zoom-13` (r. ~140–180), `checkNameCollisions` a `checkPinOverlaps` (r. ~500–660), vytváranie `combinedLabel` (r. ~684). Nič iné nečítaj ani nemeň.

Matej testoval 033 v telefóne. Mená nefungujú. Hlavný chat našiel príčiny v kóde:

1. **Spoločné meno je statický `div` v kontajneri mapy**, ktorý sa umiestni len pri `moveend`/`zoomend`. Počas posúvania mapy ostáva na mieste a nehýbe sa s pinmi.
2. **Pri oddialení nezmizne:** `checkNameCollisions` pri priblížení < 13 hneď skončí (`return`), takže `combinedLabel` ostane zobrazený. Ostatné mená skrýva CSS trieda `.map-zoom-13`, spoločné meno nie.
3. **Spája sa pri akomkoľvek dotyku:** test prekrytia berie aj 1 px prekryv obdĺžnikov. Dvojice sa tvoria pri vzdialenosti pinov < 40 px aj zvislo, preto sa Roxy a EPIC spoja do jedného mena, hoci nemajú.

### Správne správanie
1. **Spoločné meno sa správa ako ostatné mená:** hýbe sa s mapou plynulo (aj počas ťahania a približovania), pri priblížení < 13 zmizne rovnako ako ostatné mená.
   - Odporúčané riešenie: spoločné meno je samostatný `maplibregl.Marker` (element s textom, `anchor: 'top'`) na polovici súradníc dvojice, posunutý pod piny (`offset`), nie `div` umiestňovaný ručne. Viditeľnosť pri priblížení cez rovnakú triedu `.map-zoom-13` ako `.pin-name`. Ak zvolíš iné riešenie, musí spĺňať to isté.
2. **Spájať len pri značnom prekrytí** (v akomkoľvek smere). Obe mená vycentrované pod pinmi, porovnaj ich obdĺžniky. Spojiť len ak:
   - prekryv na šírku ≥ 30 % šírky kratšieho mena **a**
   - prekryv na výšku ≥ 50 % výšky mena.

   Inak sa nespájajú a **ostanú obe mená**. Mierny dotyk alebo malý prekryv je v poriadku. Hodnoty 30 % / 50 % daj ako konštanty na začiatok súboru, Matej ich môže chcieť doladiť.
3. **Spoločné meno** (Matej 2026-11-10, platí pre vodorovné aj zvislé dvojice):
   - poradie: piny skôr vedľa seba (`|dx| ≥ |dy|` na obrazovke) → západ · východ („Bike Jesus · Fuchs2“); piny skôr nad sebou → sever · juh („Roxy · EPIC“),
   - poloha: vodorovne v strede dvojice, zvislo pod spodným pinom (tam, kde by bolo meno spodného pinu).
   - Žiadne meno sa kvôli prekrytiu dvojice neskrýva. Skrývanie podľa priority ostáva len pre iné kolízie (napr. meno jedného miesta cez pin alebo meno tretieho miesta), ako doteraz.
4. Výber pinu z dvojice: spoločné meno zmizne, vybraný má svoje meno vycentrované pod pinom, meno druhého sa neukáže (ako v 033, nemeň).
5. Prepočet pri `zoomend`/`moveend` ostáva (rozhoduje len o tom, či spojiť). Polohu spoločného mena počas pohybu rieši marker, nie prepočet.
6. Rozostúpenie pinov (±8 px pri < 20 px) ostáva bez zmeny.

### Test
- Unit test čistej funkcie, ktorá z dvoch obdĺžnikov a polôh pinov rozhodne: spojiť / nechať obe / skryť nižšiu prioritu. Prípady: dotyk 1 px (obe), prekryv 20 % (obe), prekryv 60 % vedľa seba (spojiť, západ · východ), prekryv 60 % nad sebou (spojiť, sever · juh, pod spodným pinom).
- Fuchs2 a Bike Jesus majú akcie málokedy v rovnaký deň. Na ručnú kontrolu preto pridaj len v dev režime (`import.meta.env.DEV`) parameter `?debugPair=1`, ktorý ukáže všetky miesta bez ohľadu na deň. V produkcii nesmie nič meniť.

### Overenie
- `npm test`, `npm run build`, úspešné nasadenie (číslo behu).
- Snímky (skript, JPEG, 390 × 844, `sk`, `?debugPair=1`) do `docs/tasks/034/`: zoom 15 a 16 pri Fuchs2/Bike Jesus, zoom 15 pri Roxy/EPIC, zoom 12 (žiadne mená). Ak snímky mapy dvakrát zlyhajú, napíš to a pokračuj.

## Report
