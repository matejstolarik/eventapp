# 092: Popisy podnikov (CZ/SK/EN), kultúra v Pre teba, akcie pri výpadku zdroja, čierna mapa, „Na mape“

## Zadanie

**Schválené Matejom 2026-11-23 11:59, 12:36 a 12:47** (zmena dátového modelu podniku aj ponechanie akcií pri výpadku: áno). Mení dáta aj appku → na konci **jeden beh pipeline** a over `deploy-app`. Čo nie je jasné, spýtaj sa.

**Čítaj:** `docs/data-model.md` (podnik: `description`, `description_url`), `docs/tasks/092/venue-descriptions.json`, `web/src/pages/VenuePage.tsx` (popis podniku, okolo r. 198), `web/src/core/search.ts` (`forYouScore`, kultúrna časť), `docs/design.md` 1 a sekcia profilu podniku. V pipeline najprv `grep -rn "description_url\|venue.*description" pipeline/ web/src` – zisti, kade ide popis podniku do appky.

### Prečo
Dnes má popis 7 podnikov a je **doslova skopírovaný z ich webov** (`data-model.md`: „z webu podniku“) – iba česky a právne rizikové (kopírovanie textu, `claude/legal.md`). Hlavný chat s Matejom napísal pre všetkých 26 podnikov **vlastné popisy** z faktov viacerých zdrojov, v troch jazykoch.

### 1. Dátový model podniku (zmena schválená)
- **Nové:** `descriptions: { "cs", "sk", "en" }` – vlastný popis podniku, 3–4 vety, čistý text; `cs` hlavný, `sk` a `en` preklady. Chýba = podnik popis nemá.
- **Nové:** `description_sources: [URL, …]` – stránky, z ktorých pochádzajú fakty (podklad na kontrolu, v appke sa nezobrazuje).
- **Zrušené:** `description` a `description_url` (skopírované texty). Odstráň ich zo všetkých podnikov aj z kódu, ktorý ich číta; nič iné na nich nesmie stáť (over grepom).
- Zapíš do `docs/data-model.md` vrátane **pravidiel písania** (ďalšie podniky podľa nich píše hlavný chat, nie pipeline ani AI):
  - vlastnými slovami, len fakty zo zdrojov (aj recenzie, ak sa zhodujú), nikdy vety zo zdroja;
  - žiadne názory a dojmy („pôsobí ako opustená chata“, „bludisko“), žiadne nepodložené superlatívy;
  - podnik **neznevažovať** („menšie / menej známe kapely“ → „kapely z nezávislej scény“);
  - žiadne interné detaily, ktoré návštevníkovi nič nepovedia (názvy miestností, domáci poriadok, štatistiky, technika sály);
  - žiadne odhady publika („chodia sem hlavne…“), žiadne promo a prázdne záverečné vety („nenáročné miesto“, „oplatí sa rezervovať“);
  - vymenovanie nekončí slabšou položkou; bez otváracích hodín, cien a adresy (sú inde v profile).
- Riadok do `docs/decisions.md` (2026-11-23, Matej).

### 2. Dáta
Prenes **doslova** texty a zdroje z `docs/tasks/092/venue-descriptions.json` (kľúč = `id` podniku, všetkých 26) do `data/venues.json` ako `descriptions` a `description_sources`. Nič neprepisuj ani neskracuj. Ak pipeline kopíruje podniky ďalej (napr. do výstupu pre appku), musia tam prejsť nové polia.

### 3. Appka
- Profil podniku zobrazí `descriptions[jazyk appky]`, inak `descriptions.cs`. Bez popisu sa sekcia nezobrazí (ako dnes).
- **Vzhľad a správanie sekcie popisu bez zmeny** (rozbaľovanie atď. podľa `design.md`). Nový UI prvok nepridávaj.

### 4. Oprava Pre teba – kultúra (Matej 2026-11-22 16:27, otvorený bod z 091)
V `forYouScore`: typ **kultúra bez vybratých podtypov** dáva kultúrnej časti **20** (dnes 40), rovnako ako hudba bez obľúbených žánrov. Dôvod: s obľúbeným miestom mala inak ✦ každá kultúrna akcia. Podtyp kultúry (80) bez zmeny. Doplň test a blok do `docs/design.md` 7c.

### 5. Výpadok zdroja – nechať posledné známe akcie (Matej 2026-11-23 12:47, zmena schválená)
**Problém:** Klub 007 vracia od 22. 11. (beh 090) GitHubu `403` → 0 akcií → podnik je v appke prázdny, hoci akcie z predchádzajúceho behu máme (alert #8).
- Keď zdroj **zlyhá** (chyba sťahovania alebo 0 akcií, hoci v predchádzajúcom behu akcie mal), pipeline nechá v `events.json` **všetky budúce akcie tohto zdroja, ktoré máme** – z predchádzajúceho publikovaného `events.json` (`previous_events`), ktorý obsahuje celý známy program zdroja vrátane akcií ponechaných v skorších behoch počas toho istého výpadku (Matej: „všetko, čo sme nazbierali“, nie len posledné stiahnutie). Pri viacdňovom výpadku sa teda nič nestratí, akcie sa prenášajú z behu na beh. Obsah akcií bez zmeny. **Bez časového limitu** – akcie odpadávajú samy, keď prebehnú. Nič nedomýšľaj (ani nové akcie, ani opravy).
- Pri ponechanej akcii zaznamenaj, kedy bol zdroj naposledy úspešný (napr. `stale_since` / `last_ok`; názov a umiestnenie navrhni podľa `data-model.md` a zapíš tam). **V appke bez značky.**
- Keď zlyhávajúcemu zdroju už **nezostane žiadna budúca akcia**, podnik sa v appke **nezobrazuje** (zoznam Miesta, mapa, výber obľúbených v preferenciách ho môže ponechať – ak by skrytie rozbilo uložené obľúbené, spýtaj sa). Platí len pre podnik so zlyhávajúcim zdrojom, nie pre podnik, ktorý len nemá program. Keď zdroj znova funguje, všetko sa vráti samo.
- Alert (`source:<venue>/<label>`) ostáva ako dnes; v súhrne behu počet ponechaných akcií na zdroj.
- Over na fixture: zdroj s chybou → akcie z predchádzajúceho behu ostanú; minulé odpadnú; zdroj bez akcií a bez budúcich → podnik skrytý. Riadok do `docs/decisions.md`.
- Ak 007 v behu na konci úlohy stále vracia 403, v reporte uveď, koľko jeho akcií sa takto zachovalo. **Spôsob sťahovania 007 nemeň** (pravidlo `CLAUDE.md`).

### 6. Čierna mapa po návrate do appky (Matej 2026-11-23, chyba)
**Správanie:** appka ostane otvorená na Mape, Matej sa prepne do inej appky (appku nezavrie) a vráti sa napr. po 2 hodinách → **mapa je úplne čierna, piny sú na mieste**. Nesmie sa to stávať.
**Hypotéza (neoverená):** mobilný prehliadač pri dlhom pobyte na pozadí zahodí WebGL kontext mapy (`webglcontextlost`) a MapLibre ho po návrate neobnoví; piny sú HTML značky, preto ostanú. V `web/src/` dnes nie je žiadna obsluha `webglcontextlost` / `webglcontextrestored` (grep), `MapPage.tsx` pri návrate volá len `resize()`.
- Najprv **over príčinu** (dá sa vyvolať stratu kontextu cez rozšírenie `WEBGL_lose_context` v Playwright/Chromium) a napíš ju do reportu.
- Oprava: po návrate (`visibilitychange` → visible) a pri `webglcontextrestored` mapa musí byť znova vykreslená; ak sa kontext neobnoví, mapu znovu vytvor so zachovaním stredu, zoomu, vybraného dňa, filtra a otvoreného panelu. Bez viditeľného blikania navyše a bez zmeny dizajnu.
- Test (Playwright): stratený a obnovený kontext → canvas mapy nie je čierny (napr. vzorka pixelov), piny a panel ostanú.

### 7. „Na mape“ z detailu akcie nevycentruje mapu (Matej 2026-11-23, chyba)
**Správanie:** ťuk na „Na mape“ v detaile akcie prepne na Mapu, ale **mapa sa nevycentruje** na podnik. Má to fungovať rovnako ako ťuk na pin: vybraný pin, otvorený panel podniku, mapa posunutá na podnik (`easeTo` s rovnakým paddingom ako pri pine).
**Kód:** `EventPage.tsx` `handleGoToMap` → `usePendingSelect` (`MapPage.tsx` ~r. 101) → `markerSync.ts` „Handle external Na mape navigation“ (~r. 194, `easeTo`). Príčinu nepoznám – hypotézy na overenie: `easeTo` beží, kým je mapa ešte skrytá alebo pred `resize()` v efekte `isVisible` (posun sa stratí); pin podniku v tej chvíli ešte neexistuje (iný vybraný deň), takže sa vetva nespustí; alebo `easeTo` prebije animácia pádu pinov (081). Najprv reprodukuj (Playwright: detail akcie → Na mape → stred mapy vs. súradnice podniku), príčinu napíš do reportu, potom oprav.
- Test: po „Na mape“ je podnik v strede viditeľnej časti mapy (nad panelom) aj vtedy, keď bola mapa predtým posunutá inam a keď je akcia v inom dni než vybratý deň.

## Overenie a report
- Testy (`pytest -q`, `npm test -- --reporter=dot`), `npm run build`.
- **Jeden beh pipeline** na konci; z jeho výstupu: počet podnikov s `descriptions` (má byť 26) a že žiadny podnik nemá `description` / `description_url`. Príkaz uveď.
- `deploy-app` success; v nasadenej appke over popis aspoň pri 2 podnikoch v CZ a EN (stačí grep v nasadenom JSON / bundli).
- Snímka: `docs/tasks/092/venue-description.jpg` – profil Cross Club so zobrazeným popisom (390 × 844, JPEG 80, Playwright skript z `tests/playwright/`).
- Čísla Pre teba pred/po pre preferencie: typ kultúra (bez podtypov) + 2 obľúbené miesta, bez žánrov (✦✦ / ✦ / nič, ✦ mimo obľúbených miest).
- `## Report` podľa `CLAUDE.md`.
