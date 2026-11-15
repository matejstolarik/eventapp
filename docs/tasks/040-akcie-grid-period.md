# 040: Akcie, časť 1 – mriežka, obdobie, zoradenie (+ štýl výberu dňa na mape)

## Zadanie

**Čítaj:** `design.md` časť 1, **časť 4 celá** a v časti 2 riadok „Štýl panelu“ (výber dňa); snímky `docs/design/screens/10-akcie-mriezka.png`, `11-akcie-obdobie.png` a HTML `docs/design/html/10-akcie-mriezka.html`, `11-akcie-obdobie.html` (presné rozmery, farby, písma – prevezmi hodnoty odtiaľ). V kóde: `web/src/App.tsx` (záložka `events`, dnes `ComingSoon`), `components/DaySelector.tsx`, `core/day.ts`, `core/visible.ts`, `core/eventType.ts`, `core/store.ts`, `map/useUserLocation.ts` (len kde sa ukladá poloha). `decisions.md`: `grep -n "5:00\|V noci" docs/decisions.md`.

Akcie sa robia v dvoch úlohách, aby boli malé. **Táto úloha:** obrazovka s mriežkou, výber obdobia, zoradenie, prázdny stav a nový štýl výberu dňa na mape. **Úloha 041 (ďalšia):** hľadanie, Pre teba, Nové. V tejto úlohe preto čipy Pre teba, Nové, lupu ani Filter **nezobrazuj** (prídu v 041, resp. s Filtrom), lišta má zatiaľ len tlačidlo obdobia.

### 1. Logika v `core/` (čisté funkcie, testy)
- **Obdobia:** `today`, `tomorrow`, `weekend`, `next7`, `next30`, `anytime`, `custom {from, to}` → rozsah dátumov (Praha, hranica dňa 5:00 cez existujúce `getToday`). Víkend = pi–ne; po–št najbližší víkend, pi–ne od dneška do nedele. 7/30 dní posuvne od dneška vrátane. Kedykoľvek = od dneška bez konca.
- **Akcie pre obdobie:** zrušené a skončené preč (rovnaké pravidlá ako `visible.ts` pre bežný deň; nočný režim mapy sa tu nepoužíva – v Akciách platí len hranica 5:00).
- **Zoradenie:** `date` (dátum, potom čas začiatku; bez času na koniec dňa) a `distance` (od poslednej známej polohy, vzdialenosť miesta; pri rovnakej vzdialenosti dátum).
- **Text dátumu na karte:** „Dnes“, „Zajtra“, inak krátky deň + dátum podľa jazyka („Pi 20. 11.“ / „Pá 20. 11.“ / „Fri 20 Nov“) – použi existujúce formátovanie z `i18n`, ak je.
- **Text tlačidla:** „Dnes“, „Zajtra“, „Víkend“, „7 dní“, „30 dní“, „Kedykoľvek“, vlastný „20.–24. 11.“ (CZ/SK/EN v `i18n`).
- Testy na všetky obdobia (vrátane pondelka, piatku, nedele, 1:30 v noci), zoradenie, texty.

### 2. Obrazovka Akcie
Podľa `design.md` 4 a snímky `10` (bez Pre teba, Nové, lupy a Filtra):
- hlavička „Akcie“, biele tlačidlo obdobia, riadok s počtom („12 akcií“) a „Zoradiť: dátum ▾“;
- **mriežka 3 stĺpce bez nadpisov dní**, karta presne podľa `design.md` 4 (náhľad `image_thumb`, bez neho plocha vo farbe typu s ikonou; dátum · čas; názov max. 2 riadky; miesto; štítky v jednom riadku s miznutím na pravom okraji – typ, žánre, potom charakter miesta ako obrys);
- ťuk na kartu → stránka akcie (rovnako ako odinakiaľ);
- **zoradenie:** malá ponuka pod „Zoradiť“ (dátum / vzdialenosť); vzdialenosť len ak je známa poloha (inak sa nezobrazí). Poslednú známu polohu z mapy sprístupni cez malý zdieľaný úložný bod (napr. v `core/store.ts` alebo kontext), nie novým zisťovaním polohy – Akcie o polohu nežiadajú;
- **prázdny stav** podľa `design.md` 4 (bez tlačidla „Zrušiť filtre“, filtre ešte nie sú);
- **predvolene Dnes**, posledné obdobie sa pamätá lokálne (`store.ts`); vlastný interval sa po reštarte nepamätá (vráti sa Dnes).
- Mriežka musí scrollovať plynulo: `<img>` s `width`/`height`, `decoding="async"`, `loading="lazy"` od 4. radu ďalej; žiadne plné `image_url` v mriežke.

### 3. Panel obdobia + mapa (spoločný komponent)
- Panel zdola podľa snímky `11`: nadpis „Obdobie“, Kedykoľvek s ikonou nekonečna a „všetky akcie“, deliaca čiara, Dnes / Zajtra / Tento víkend / Najbližších 7 dní / Najbližších 30 dní s rozsahom vpravo, „Iný dátum“ s ikonou kalendára → kalendár ako na mape s **výberom intervalu** (1. ťuk začiatok, 2. koniec, dvakrát ten istý deň = jeden deň; potvrdenie výberu druhým ťukom).
- **Mapa:** výber dňa (`DaySelector`) dostane rovnaký štýl (`design.md` 2, „Štýl panelu“): nadpis „Deň“, biela pilulka pri vybranom, sivý údaj vpravo („do 5:00“ pri V noci, dátum pri Dnes/Zajtra), „Iný dátum“ s ikonou kalendára. Obsah a správanie mapy sa nemenia.
- Urob z toho jeden komponent panelu (položky a režim kalendára ako parametre), použitý na oboch obrazovkách.

### Testy
- Vitest: funkcie z bodu 1.
- Existujúce testy mapy musia prejsť bez zmeny.

### Overenie
- `npm test`, `npm run build`, číslo nasadenia.
- Snímky Playwright (syntetické `events.json` OK, zmrazený čas nedeľa 15. 11. 18:00) do `docs/tasks/040/`: `01-akcie-dnes.jpg`, `02-akcie-obdobie.jpg` (otvorený panel), `03-akcie-kalendar-interval.jpg` (vybraný interval), `04-mapa-vyber-dna.jpg`, `05-akcie-prazdne.jpg`.

## Report
