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
**Správanie:** ťuk na „Na mape“ v detaile akcie prepne na Mapu, ale **mapa sa nevycentruje** na podnik. Výsledok ako po ťuku na pin (vybraný pin, otvorený panel podniku), ale **mapa sa vycentruje na podnik vždy** (`easeTo` s paddingom ako pri pine), lebo prichádzame z detailu akcie a mapa môže byť kdekoľvek. **Ťuk na pin ostáva bez zmeny** – ten posúva mapu len vtedy, keď je pin zakrytý alebo pri okraji (Matej: tak je to správne).
**Kód:** `EventPage.tsx` `handleGoToMap` → `usePendingSelect` (`MapPage.tsx` ~r. 101) → `markerSync.ts` „Handle external Na mape navigation“ (~r. 194, `easeTo`). Príčinu nepoznám – hypotézy na overenie: `easeTo` beží, kým je mapa ešte skrytá alebo pred `resize()` v efekte `isVisible` (posun sa stratí); pin podniku v tej chvíli ešte neexistuje (iný vybraný deň), takže sa vetva nespustí; alebo `easeTo` prebije animácia pádu pinov (081). Najprv reprodukuj (Playwright: detail akcie → Na mape → stred mapy vs. súradnice podniku), príčinu napíš do reportu, potom oprav.
- Test: po „Na mape“ je podnik v strede viditeľnej časti mapy (nad panelom) aj vtedy, keď bola mapa predtým posunutá inam a keď je akcia v inom dni než vybratý deň.

## Overenie a report
- Testy (`pytest -q`, `npm test -- --reporter=dot`), `npm run build`.
- **Jeden beh pipeline** na konci; z jeho výstupu: počet podnikov s `descriptions` (má byť 26) a že žiadny podnik nemá `description` / `description_url`. Príkaz uveď.
- `deploy-app` success; v nasadenej appke over popis aspoň pri 2 podnikoch v CZ a EN (stačí grep v nasadenom JSON / bundli).
- Snímka: `docs/tasks/092/venue-description.jpg` – profil Cross Club so zobrazeným popisom (390 × 844, JPEG 80, Playwright skript z `tests/playwright/`).
- Čísla Pre teba pred/po pre preferencie: typ kultúra (bez podtypov) + 2 obľúbené miesta, bez žánrov (✦✦ / ✦ / nič, ✦ mimo obľúbených miest).
- `## Report` podľa `CLAUDE.md`.

## Report

**2026-11-23**, commity: `e22a2aa` (práca), report + snímka v ďalšom commite. Beh pipeline **45172645181** (success, `events.json` `generated_at` 2026-11-23T13:32:04+01:00), deploy appky **45172630374** (success).

### Hotovo
1. **Dátový model:** `descriptions {cs, sk, en}` + `description_sources` pri podniku; `description` / `description_url` zrušené z dát, typov (`web/src/core/types.ts`) aj testov. Grep `description_url` v `pipeline/ web/src tests/` = 0 nálezov. `docs/data-model.md` doplnený vrátane pravidiel písania; riadok v `decisions.md`.
2. **Dáta:** texty a zdroje z `docs/tasks/092/venue-descriptions.json` prenesené doslova do `data/venues.json` (26/26; test `test_venues_have_own_descriptions` porovnáva zhodu znak po znaku). Pipeline podniky kopíruje celé (`dict(v)`), nové polia prešli do `events.json`.
3. **Appka:** `VenuePage` zobrazí `descriptions[jazyk]`, inak `descriptions.cs`; vzhľad a rozbaľovanie sekcie bez zmeny.
4. **Pre teba:** kultúra bez podtypov = 20 (bolo 40); test v `search.test.ts`, blok v `design.md` 7c.
5. **Výpadok zdroja:** nový `pipeline/source_outage.py`. Zdroj zlyhal = chyba, alebo 0 akcií a predtým akcie mal / už zlyhával (`pipeline_state.json` → `failing_sources`). Jeho budúce akcie z predchádzajúceho `events.json` ostanú bez zmeny, s `source_last_ok` (= `last_seen`, ponechaná akcia si hodnotu drží). Podnik dostane `source_failing: true`; appka ho skryje v zozname Miesta, keď nemá budúcu akciu (`web/src/core/hiddenVenue.ts`). Na mape nemá pin aj tak, lebo pin je len pri akcii. Preferencie a obľúbené ostávajú nedotknuté. Súhrn behu má pri zdroji `kept`, alert `source:<venue>/<label>` ostáva, do textu alertu pribudol počet ponechaných akcií. Testy na fixture (`tests/test_source_outage_092.py`): chyba → budúce ostanú, minulé odpadnú; 0 akcií po sekcii (MeetFactory divadlo); zdroj bez budúcich akcií → podnik `source_failing`; zdroj sa vráti → stav sa vyčistí.
6. **Čierna mapa – príčina overená:** strata kontextu cez `WEBGL_lose_context` v Chromiu. Pred opravou: po `restoreContext()` bol canvas úplne čierny (podiel nečiernych pixelov 1 → 0), bez obnovy sa mapa nezotavila vôbec. MapLibre po obnove síce nastaví nový painter, ale dlaždice, písma a obrázky boli objekty strateného kontextu. (Obsluha `webglcontextlost/restored` v `MapPage.tsx` existovala, robila len `triggerRepaint`.) **Oprava:** pri `webglcontextrestored`, a pri návrate (`visibilitychange`), keď je kontext stále stratený (po 600 ms čakania na obnovu), sa mapa vytvorí znovu s rovnakým stredom, zoomom a natočením. Existujúce piny a bodka polohy sa presunú na novú mapu, takže nevznikne nová animácia pinov. Deň, filter a panel sú React stav a ostanú.
7. **„Na mape“ – príčina:** reprodukované len vtedy, keď mapa od štartu appky nebola zobrazená a akcia je v inom dni (pin nevybratý, podnik na y = 734 namiesto 352). Po zobrazení skrytej mapy sa začnú načítavať dlaždice, `map.loaded()` je vtedy `false` a efekt so zmenou dňa preskočil aktualizáciu pinov. Pin podniku teda nevznikol a vetva s `easeTo` sa nespustila (ďalšia aktualizácia prišla až po 60 s). **Oprava:** aktualizácie pinov sa riadia príznakom z udalosti `load` (`mapReadyRef`), nie `map.loaded()`. Efekt `resize()` po zobrazení teraz beží pred efektom „Na mape“, takže sa centruje už na skutočnú veľkosť mapy. Ťuk na pin je bez zmeny.

### Rozhodnuté samostatne
- Názvy polí: `source_last_ok` (akcia) a `source_failing` (podnik, len `events.json`), stav `failing_sources`. Dôvod: podľa vzoru `first_loaded` / `venue_first_loaded`.
- Akcia sa so zdrojom páruje podľa `type` (+ `section`) v jej `sources`, lebo akcie nemajú URL konfigurácie zdroja. Ponechané akcie sa pridávajú až po `run_checks`, takže neprechádzajú AI ani úpravami (obsah bez zmeny); preskočí sa akcia s rovnakým `id`, akú už v behu máme.
- Iba pre testy: `window.__map` v dev režime a `data-testid="event-panel"` (bez vizuálnej zmeny).

### Čísla (beh 45172645181)
Príkaz: stiahnuť `https://matejstolarik.github.io/eventapp/events.json` do `site/events.json`, potom Python: počet `venues` s `descriptions`, s kľúčom `description` / `description_url`, `source_failing`, akcie so `source_last_ok`.
- Podniky: 26, s `descriptions` **26**, s `description` **0**, s `description_url` **0**. Akcií 865.
- `source_failing`: žiadny podnik, ponechaných akcií 0. **Klub 007 v tomto behu znova odpovedal: 34 akcií** (bez 403). Zachovanie akcií sa preto v ostrom behu neprejavilo, overené je len na fixture.
- Pre teba, typ kultúra bez podtypov + obľúbené MeetFactory a Archa+, bez žánrov (859 nadchádzajúcich). Príkaz (z `web/`): `npx vite-node scripts/for-you-092.ts ../site/events.json [modul]`, kde modul „pred“ je `git show 6bb56e9:web/src/core/search.ts` uložený v `src/core/`:
  - pred: ✦✦ 0 / ✦ 215 / nič 644, ✦ mimo obľúbených miest **161**
  - po: ✦✦ 0 / ✦ 54 / nič 805, ✦ mimo obľúbených miest **0**

### Overenie
- `pytest -q`: 740 passed, 4 skipped. `npm test -- --reporter=dot`: 300 passed. `npm run build` OK.
- Playwright `tests/playwright/map-092.spec.ts` (z `web/`, `NODE_PATH=web/node_modules`, dáta z Pages): **8 passed**. Kontext stratený a obnovený / neobnovený → canvas nie je čierny (podiel 1), stred a zoom bez zmeny, piny sú tie isté prvky, vybraný pin aj panel ostali. „Na mape“ z mapy, z Akcií po posunutí mapy a zo studeného štartu, v ten istý aj v iný deň → podnik je v strede viditeľnej časti (195, 352 ± 8 px), pin je vybratý a panel otvorený. Pred opravou zlyhali 3 z týchto testov.
- Nasadené: `events.json` z Pages, Cross Club cs „Klub v Holešovicích kousek od nádraží…“, en „A club in Holešovice near the station…“; MeetFactory cs „Mezinárodní centrum současného umění, které v roce 2001…“, en „An international centre for contemporary art founded in 2001…“. Bundle `assets/index-Cku43xAi.js` obsahuje čítanie `descriptions[lang] || descriptions.cs` aj `source_failing`.
- Snímka `docs/tasks/092/venue-description.jpg` (Cross Club, sk, 390 × 844, `tests/playwright/screenshots-092.spec.ts`, 1 passed). Neprezeral som ju.

### Otvorené
- Ponechanie akcií pri výpadku nebolo vyskúšané na ostrom výpadku, lebo 007 dnes funguje. Ukáže sa pri najbližšom zlyhaní zdroja v súhrne behu (`kept`).
- Oprava čiernej mapy je overená na simulovanej strate kontextu v Chromiu, nie na skutočnom telefóne po dlhom pobyte na pozadí.
