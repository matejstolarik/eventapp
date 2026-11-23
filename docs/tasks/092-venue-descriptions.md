# 092: Popisy podnikov (vlastný text, CZ/SK/EN) + oprava kultúry v Pre teba

## Zadanie

**Schválené Matejom 2026-11-23 11:59 a 12:36** (zmena dátového modelu podniku: áno). Mení dáta aj appku → na konci **jeden beh pipeline** a over `deploy-app`. Čo nie je jasné, spýtaj sa.

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

## Overenie a report
- Testy (`pytest -q`, `npm test -- --reporter=dot`), `npm run build`.
- **Jeden beh pipeline** na konci; z jeho výstupu: počet podnikov s `descriptions` (má byť 26) a že žiadny podnik nemá `description` / `description_url`. Príkaz uveď.
- `deploy-app` success; v nasadenej appke over popis aspoň pri 2 podnikoch v CZ a EN (stačí grep v nasadenom JSON / bundli).
- Snímka: `docs/tasks/092/venue-description.jpg` – profil Cross Club so zobrazeným popisom (390 × 844, JPEG 80, Playwright skript z `tests/playwright/`).
- Čísla Pre teba pred/po pre preferencie: typ kultúra (bez podtypov) + 2 obľúbené miesta, bez žánrov (✦✦ / ✦ / nič, ✦ mimo obľúbených miest).
- `## Report` podľa `CLAUDE.md`.
