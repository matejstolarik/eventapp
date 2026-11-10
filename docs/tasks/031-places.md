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
