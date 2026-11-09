# 024: Opravy mapy a dokončenie overenia z 023

## Zadanie
Zadal: hlavný chat, 2026-11-09. Po úlohe 023.

Matej skúsil appku v telefóne. Hlavný chat ju otestoval lokálne. Mapa má dve vážne chyby a je ťažko čitateľná. Táto úloha ich opraví a dokončí overenie, ktoré v 023 chýbalo. Predloha ostáva `docs/design.md` a `docs/design/`.

### 1. Kritická chyba: značky sa po ťuknutí rozsypú
Po ťuknutí na značku sa všetky značky zoradia do pásov cez celú šírku hore na obrazovke (Matej v telefóne aj hlavný chat lokálne).
- Pravdepodobná príčina: `markers.ts` nastavuje `el.className = 'pill-marker'` (prípadne pri prekreslení výberu), čím zmaže triedy, ktoré MapLibre pridáva (`maplibregl-marker`, `-anchor-…`) a ktoré nesú absolútne umiestnenie. Over to.
- Oprava: triedy pridávať/odoberať (`classList`), alebo pri zmene výberu meniť len vnútro prvku. Značky sa pri zmene výberu nesmú vytvárať nanovo, ak to nie je nutné.
- Test (Playwright): ťuknutie na značku → všetky značky ostanú na svojich súradniciach (porovnaj pozície pred a po).

### 2. Značky sa nesmú zakrývať
Dnes sa nad seba posúvajú len miesta s úplne rovnakým bodom. EPIC zakrýva Archa+ aj Bike Jesus a Archa+ sa nedá ťuknúť. Predloha: **žiadna značka nesmie zmiznúť ani byť zakrytá.**
- Detekcia prekrytia podľa **skutočných obdĺžnikov pilulek na obrazovke** (po každom posune/priblížení), nie podľa zhodných súradníc.
- Prekrývajúce sa pilulky sa posunú nad seba (stĺpec), každá ukazuje na svoj bod. Pri veľkom zhluku (napr. centrum pri oddialení) to rieši prechod na body.
- Každá značka musí byť ťuknuteľná (test: pri dnešných reálnych dátach sa dá ťuknúť na každú).

### 3. Mapa je „celá čierna, divná a neprehľadná“ (Matej)
Príčina je čiastočne v predlohe: farby z návrhu (pozadie `#14141D`, cesty `#22222E`) boli pre abstraktnú kresbu, na skutočnej mape majú príliš malý kontrast. Navyše prefarbenie cez nahrádzanie hex hodnôt v štýle *liberty* zasiahne len časť vrstiev (liberty používa aj iné zápisy farieb). A odstránenie popisov vzalo aj názvy ulíc a štvrtí, bez ktorých sa v meste nedá orientovať.
- **Postav vlastný štýl** nad vektorovým zdrojom OpenFreeMap (vlastný zoznam vrstiev s explicitnými farbami), nie nahrádzanie farieb v cudzom štýle. Zachovaj autorstvo.
- Cieľ: **tmavá, ale čitateľná mapa.** Orientačné hodnoty (môžeš ich doladiť, ak treba pre čitateľnosť, a v reporte uveď výsledné):

| Vrstva | Farba |
|---|---|
| pozadie / zem | `#191923` |
| budovy (od priblíženia ~15) | `#21212D` |
| parky, zeleň | `#1B2A22` |
| voda (Vltava!) | `#1D3352`, dobre viditeľná |
| vedľajšie ulice | `#2C2C3B` |
| hlavné ulice | `#3D3D52` |
| najväčšie cesty | `#4A4A63` |
| železnica | `#33334A` prerušovane |

- **Popisy, ktoré ostanú** (text `#8E8AA6`, obrys `#111118`, písmo Outfit alebo štandardné písmo štýlu):
  - názvy štvrtí (Karlín, Holešovice, Žižkov…),
  - názvy hlavných ulíc a ulíc od priblíženia ~15,
  - Vltava a ostrovy (Štvanice),
  - **stanice metra** (malá značka + názov, dôležité na orientáciu v Prahe).
- Preč ostáva: obchody, reštaurácie, ostatné body záujmu, hranice, výškopis.
- Značky akcií musia byť na podklade jasne najvýraznejšie.
- Snímky mapy pri troch priblíženiach (celá Praha, centrum, ulica) daj do `docs/tasks/024/`.

### 4. Prstenec prebiehajúcej akcie
Podľa `01-mapa.html` (trieda `.live`): tmavá medzera 4 px, farebný prstenec 4 px (spolu 8 px) a pulzujúca žiara, ktorá ide z 8 px na 24 px a zmizne. Dnes je prstenec hrubší a žiara širšia. Zosúlaď s predlohou.

### 5. Z 023 nesplnené
- **Neexistujúca akcia:** text „Akcia už prebehla“ (CZ „Akce už proběhla“, EN „This event has ended“) s odkazom na mapu, podľa zadania 023.
- **Snímky a porovnanie s predlohou:** Playwright, 390 × 844, z nasadenej appky s reálnymi dátami (ak to prostredie nedovolí, lokálne s `events.json` stiahnutým z Pages):
  - mapa,
  - mapa s kartou,
  - karta s viacerými akciami,
  - stránka akcie s obrázkom a bez obrázka,
  - výber dňa,
  - Môj účet.

  Do `docs/tasks/024/`. V reporte **tabuľka rozdielov oproti `docs/design/screens/`** (prvok, predloha, appka, dôvod).
- **Overenie:** platný manifest a inštalácia, offline (vypnúť sieť → posledné dáta + informácia), otvorenie odkazu `#/akcia/<id>` priamo.

### Report navyše
- Príčina chyby 1 (potvrdená, nie domnienka).
- Výsledná paleta štýlu mapy.
- Čo z predlohy sa nepodarilo dodržať a prečo.

## Report
