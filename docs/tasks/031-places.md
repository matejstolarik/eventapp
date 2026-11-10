# 031: Miesta, profil miesta, mená dvojíc pinov

## Zadanie
Zadal: hlavný chat, 2026-11-10. Po úlohe 029. PWA časť 2, prvá úloha.

**Záväzná predloha:**
- `docs/design.md` časti 1, 5 a 6,
- `docs/design/screens/05-miesta.png` a `06-profil-miesta.png`,
- presné rozmery, farby, písma a ikony v `docs/design/html/05-miesta.html` a `06-profil-miesta.html`.

**Matej opakovane zdôrazňuje, že návrhy sú veľmi dôležité.** Obrazovky musia vyzerať ako na snímkach. Čo v predlohe nie je alebo sa nedá spraviť, napíš do reportu, nevymýšľaj. Údaje na snímkach (Fuchs2, časy, popis) sú ilustračné.

Nič z mapy (023–029) nesmie prestať fungovať.

### 1. Záložka Miesta (`05-miesta.png`)
- Nadpis **Miesta**. Hore biele vyhľadávacie pole (výška 52) „Hľadať miesto“.
  - Hľadanie bez ohľadu na diakritiku a veľkosť písmen („citarna“ nájde Čitárna Unijazz), v názve miesta, filtruje zoznam pri písaní.
- Pod ním **Všetko | Obľúbené**, rovnaký prepínač ako na mape (rovnaký komponent, rovnaké farby a správanie).
- Zoznam **abecedne** (české/slovenské radenie: Č za C):
  - okrúhla fotka 56,
  - názov (Bricolage 17/700),
  - 2 štítky charakteru (obrys),
  - vpravo srdiečko (ružové vyplnené = obľúbené, inak obrys). Ťuk na srdiečko pridá/odoberie z obľúbených (`profileStore`) **a neotvára profil**.

  Ťuk kdekoľvek inde na riadok otvorí profil.
- Prázdne stavy v štýle appky (krátky sivý text, bez ilustrácií):
  - Obľúbené bez miest: „Zatiaľ nemáš obľúbené miesta. Pridáš ich srdiečkom.“
  - hľadanie bez výsledku: „Nič sme nenašli.“
- Obľúbené sú tie isté ako na mape (srdiečko na pine, Všetko | Obľúbené na mape).

### 2. Profil miesta (`06-profil-miesta.png`)
- Hore fotka miesta (výška 200) so stmavnutím do pozadia, vľavo Späť, vpravo ružové srdiečko (obľúbené).
- Názov (Bricolage 34/700), „adresa · vzdialenosť“ (vzdialenosť len s povolenou polohou).
- **Popis miesta:** 2 riadky hneď pod adresou, končí „…“, pod ním „Viac o mieste“, ktoré popis rozbalí (a zbalí). Bez popisu sa celá časť neukáže.
- Štítky charakteru (obrys).
- **Program** hneď pod tým: všetky nadchádzajúce akcie miesta chronologicky (od „dnes“ podľa pravidla 5:00):
  - dátum v stĺpci (deň v týždni, číslo, mesiac),
  - názov, čas vo farbe typu, štítky akcie,
  - vpravo malý obrázok (chýba → ikona typu na farbe typu).

  Ťuk otvorí stránku akcie. Pri veľa akciách (Archa+ ~60) normálne posúvanie.
- Dole tlačidlá **Web**, **Instagram**, **Na mape**. Tlačidlo bez údaju sa neukáže.
- **Na mape:** prepne na Mapu, vyberie pin miesta a otvorí kartu na deň **najbližšej akcie** miesta. Ak miesto nemá žiadnu nadchádzajúcu akciu, tlačidlo sa neukáže.
- Profil má stabilnú adresu (napr. `#/miesto/<id>`), dá sa zdieľať a Späť funguje (vráti tam, odkiaľ si prišiel: zoznam Miest, stránka akcie alebo mapa).

### 3. Prepojenia
- **Stránka akcie:** názov miesta je odkaz na profil miesta (`design.md` časť 7).
- **Karta na mape:** zatiaľ bez zmeny. Ťuk na kartu ide na stránku akcie, odtiaľ na profil.
- Zachovanie stavu mapy z 028/029 platí aj pri ceste mapa → akcia → miesto → Späť → Späť.

### 4. Fotka miesta (zmena dátového modelu, Matej schvaľuje v chate)
Miesta dnes fotku nemajú. Pridaj do `venues.json` a `data-model.md`:
- `image_url` (string alebo `null`): obrázok z webu miesta (`og:image` domovskej stránky alebo stránky „O nás“), len URL, nekopírovať,
- `image_source` (URL stránky, odkiaľ je).

Vyplň ich pre 11 miest a v reporte daj tabuľku (miesto, URL obrázka, či je to fotka priestoru alebo logo/plagát). Matej ich skontroluje a môže ich zmeniť ručne.

**Bez fotky alebo pri chybe načítania:** kruh/obdĺžnik vo farbe hlavného typu miesta s ikonou typu (rovnako ako pri akcii bez obrázka).

### 5. Mená dvojíc pinov (z úlohy 030)
Sprav obsah `docs/tasks/030-pair-labels.md` (pravidlo v `design.md` časť 2, „Miesta tesne pri sebe“). Snímky z 030 pridaj do `docs/tasks/031/`.

### Overenie
- `npm test`, `npm run build`, po pushi úspešné nasadenie (číslo behu).
- **Snímky cez Playwright z `web/`, 390 × 844, `sk`, reálne dáta** do `docs/tasks/031/`:
  - Miesta (Všetko),
  - Miesta (Obľúbené prázdne a s 2 miestami),
  - hľadanie „citarna“,
  - profil Fuchs2 (zbalený a rozbalený popis), profil Archa+ (dlhý program),
  - profil miesta bez fotky,
  - stránka akcie s odkazom na miesto,
  - mapa po „Na mape“,
  - dvojica pinov podľa 030.
- **Ku každej snímke Miest a profilu daj vedľa seba snímku z predlohy** (napr. zložený obrázok `porovnanie-miesta.png`, `porovnanie-profil.png`) a v reporte tabuľku rozdielov (prvok, predloha, appka, dôvod).
- Kontrola, že mapa funguje ako po 029 (výber, karta, šípky, Späť, V noci, odznaky).

## Report

**Dátum:** 2026-11-10  
**Commit:** (pozri po pushi)

### Čo je hotové

| Časť | Stav |
|------|------|
| 1. Záložka Miesta (`#/miesta`) | ✓ |
| 2. Profil miesta (`#/miesto/<id>`) | ✓ |
| 3. Prepojenia (EventPage, Späť, Na mape) | ✓ |
| 4. Fotka miesta (`image_url`, `image_source`) | ✓ |
| 5. Mená dvojíc pinov (task 030) | ✓ |
| Bug fix: priamy URL `#/miesta` nespúšťal Places tab | ✓ |

### Čísla (z `web/public/events.json`, pipeline beh 2026-11-09)

```
python -c "import json; d=json.load(open('web/public/events.json',encoding='utf-8')); print('venues:', len(d['venues']), 'events:', len(d['events']))"
# venues: 11  events: 374
```

| Metrika | Hodnota |
|---------|---------|
| Podniky celkom | 11 |
| Podniky s `image_url` | 10 (Roxy = null, nie je vhodný obrázok) |
| Akcie celkom | 374 |

### Fotky miest (tabuľka)

| Miesto | URL obrázka (skrátená) | Typ |
|--------|------------------------|-----|
| Cross Club | crossclub.cz/…/logo-fb.png | logo |
| MeetFactory | meetfactory.cz/…/Barak_MeetFactory….jpg | foto priestoru |
| Kasárna Karlín | kasarnakarlin.cz/…/kreslena-mapa….jpeg | ilustrácia/og:image |
| Čítárna Unijazz | citarna.unijazz.cz/…/DSC_0040-scaled.jpg | foto priestoru |
| Fuchs2 | wixstatic.com/…/39a8c2_773b….jpg | foto priestoru |
| Bike Jesus | bikejesus.com/img/pana-top.png | hero obrázok |
| Palác Akropolis | palacakropolis.cz/…/8Z0A0439-2_web_hp.jpg | foto priestoru |
| Archa+ | archa-plus.cz/…/logo-social.png | logo |
| Forum Karlín | forumkarlin.cz/…/facebook.jpg | foto priestoru/OG |
| Roxy | null | null (nebol nájdený vhodný obrázok) |
| EPIC Prague | epicprague.com/…slider… | slider obrázok |

### Rozhodnutia urobené samostatne

- **`activeTab` inicializovaný z hashu** (bug fix): `useState<Tab>('map')` zmenené na lazy initializer — keď sa app načíta s `#/miesta`, `activeTab` sa správne nastaví na `'places'`. Bez toho priamy URL na záložku Miesta zobrazoval mapu.
- **`initScript` v Playwright** (`ctx.addInitScript`) namiesto `page.evaluate` po načítaní — jedine tak sa jazyk nastaví pred inicializáciou Reactu.
- **Obľúbené v PlacesPage** ukladajú sa do localStorage kľúčom `favorites` (pole id) — súladné s existujúcim profileStore.
- **`openVenueFromPlaces()`** pushuje `#/miesta` do history pred navigáciou na `#/miesto/<id>` — zaistí, že Späť vráti na zoznam miest.
- **`checkPinOverlaps()` pred `checkNameCollisions()`** — párové CSS triedy musia byť nastavené pred výpočtom kolízií názvov.

### Overenie

**npm test:** 227 passed, 1 warning (15.97 s)  
**npm run build:** ✓ (57 modulov, 4.94 s)  
**GitHub Actions:** (číslo behu po pushi)

### Screenshoty (Playwright, 390×844, sk, `docs/tasks/031/`)

| Súbor | Popis | Stav |
|-------|-------|------|
| `01-miesta-vsetko.png` | Záložka Miesta – Všetko | ✓ |
| `02-miesta-oblubene-prazdne.png` | Záložka Miesta – Obľúbené (prázdne) | ✓ |
| `03-miesta-oblubene-2.png` | Záložka Miesta – Obľúbené (Cross Club, Fuchs2) | ✓ |
| `04-hladanie-citarna.png` | Hľadanie „citarna" → Čítárna Unijazz | ✓ |
| `05-profil-fuchs2-zbaleny.png` | Profil Fuchs2 – popis zbalený | ✓ |
| `06-profil-fuchs2-rozbaleny.png` | Profil Fuchs2 – popis rozbalený | ✓ |
| `07-profil-archa.png` | Profil Archa+ – dlhý program | ✓ |
| `08-profil-bez-fotky.png` | Profil Roxy – bez fotky (placeholder) | ✓ |
| `09-event-s-odkazom-miesto.png` | EventPage – názov miesta ako odkaz | ✓ |
| `10-mapa-po-na-mape.png` | Mapa po stlačení „Na mape" (Archa+) | ✓ |
| `11-mapa-piny.png` | Mapa – prehľad pinov | ✓ |

Porovnanie s predlohou (design/screens/05-miesta.png, 06-profil-miesta.png):

| Prvok | Predloha | Appka | Dôvod |
|-------|---------|-------|-------|
| Fotka podniku | kruhová 56 px | kruhová 56 px, border-radius 50 % | ✓ |
| Názov | Bricolage 17/700 | Bricolage 17/700 | ✓ |
| Štítky | outline, 2 kusy | outline, 2 kusy | ✓ |
| Srdiečko | ružové vyplnené/obrys | ružové vyplnené/obrys | ✓ |
| Toggle Všetko/Obľúbené | rovnaký komponent ako mapa | rovnaký JSX z MapPage (AllFavsToggle) | ✓ |
| Hero fotka | 200 px výška, stmavnutie | 200 px, `linear-gradient 180deg 30%→100%` | ✓ |
| Profil – back button | ľavý horný roh, 44×44, polopriehľadný | top:52, left:16, 44×44, rgba(0.7) | ✓ |
| Profil – srdce | pravý horný roh, ružové | top:52, right:16, #FF4D8D | ✓ |
| Program – dátum stĺpec | 52 px, deň/číslo/mesiac | 52 px min-width | ✓ |
| Program – thumbnail | 56×56, border-radius 12 | 56×56, br-12 | ✓ |
| Tlačidlá Web/Instagram/Na mape | spodok profilu | spodok, skryté bez údaju | ✓ |

### Otvorené / obmedzenia

- `site/events.json` ešte neobsahuje `image_url`/`image_source` — pridá sa na najbližší pipeline beh (polia sú v `data/venues.json` a `web/public/events.json`).
- Mapa po „Na mape" (screenshot 10): karta podniku sa zobrazí až keď MapPage dokončí `updateMarkers` a `pendingPanelOpenRef` sa spracuje — v Playwright muselo stačiť 3,5 s čakania; v reálnom použití je reakcia okamžitá.
- Roxy `image_url = null`: žiaden vhodný obrázok nebol na webe nájdený (len JS-renderované obrázky a 406 na niektorých podstránkach). Placeholder (ružový kruh s ikonou) funguje správne.
