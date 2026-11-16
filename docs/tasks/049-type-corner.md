# 049: Typ akcie ako farebný roh namiesto štítku typu

## Zadanie

**Čítaj:** `design.md` časť 4, odsek Mriežka (bod „Typ akcie = farebný trojuholník…“); časť 3 (riadok štítkov v karte), časť 6 (Program), časť 7 (druhý bod). V kóde: `core/eventType.ts`, miesta, kde sa vykresľujú štítky akcie a obrázok akcie: `pages/EventsPage.tsx` (karta), `components/EventPanel.tsx` (karta na mape), `pages/VenuePage.tsx` (program), `pages/EventPage.tsx` (veľký obrázok, štítky).

Robí sa po 048 (rovnaké súbory, nekonfliktuj).

### 1. Štítok typu preč
- Zo štítkov akcie vynechaj formáty, ktoré určujú farbu typu: `party`, `dj`, `concert`, `music`. Podtypy kultúry (`theatre`, `dance`, `talk`, `comedy`, `film`, `opening`, `workshop`, `quiz`) ostávajú ako bežné neutrálne štítky, na prvom mieste pred žánrami.
- Jedna funkcia v `core/` (napr. `displayTags(event)`), použitá všade (Akcie, karta na mape, program miesta, stránka akcie). Test.
- Plnofarebný štítok typu zo 047 v karte Akcií zruš; všetky štítky rovnaké tmavé.

### 2. Farebný trojuholník
- Pravouhlý trojuholník v ľavom hornom rohu obrázka akcie, farba `EVENT_TYPE_COLOR`, orezaný zaoblením obrázka (`overflow:hidden`). Veľkosť ~19 % šírky obrázka: mriežka ~22 px, stránka akcie ~56 px, malé obrázky (program miesta, karta na mape 88 px) úmerne, min. 14 px.
- Odznak „pre teba“ a tlačidlo Späť ostanú na svojom mieste **nad** trojuholníkom (vyšší z-index).
- Akcia bez obrázka (plocha vo farbe typu s ikonou) trojuholník nemá.
- Jeden malý komponent (napr. `TypeCorner`), použitý na všetkých obrázkoch akcií.

### 3. Nemeniť
Farebný čas v programe miesta, piny na mape, čipy typu vo filtri (legenda), farby typov.

## Overenie
- `npm test` (`--reporter=dot`), build OK.
- Screenshoty (Playwright, `tests/playwright/`, JPEG 390 × 844 do `docs/tasks/049/`): `akcie-mriezka.jpg` (aspoň jedna akcia s obrázkom a „pre teba“), `stranka-akcie.jpg` (akcia s obrázkom). Fixtúry musia mať aspoň pár akcií s obrázkom (dnes majú fixtúry len plochy bez obrázka – doplň testovací obrázok do fixtúr, nie do dát).
