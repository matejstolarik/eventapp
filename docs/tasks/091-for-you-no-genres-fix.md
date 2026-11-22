# 091: Pre teba bez obľúbených žánrov, aspoň jeden typ povinný

## Zadanie

**Schválené Matejom 2026-11-22 13:15–13:18** (po teste 087). Mení len appku (`web/`) → **pipeline nespúšťaj**, over len `deploy-app`. Môže bežať súbežne s 089 (089 appku nemení). Čo nie je jasné, spýtaj sa.

**Čítaj:** report **087**, `web/src/core/search.ts` (`forYouScore`, `hasAnyPrefs`), `web/src/core/preferences.ts` (`forYouNeedsSetup`), `web/src/pages/OnboardingPage.tsx`, `web/src/components/PrefPickers.tsx`, `web/src/pages/PreferencesPage.tsx`, `web/src/components/SetupPromptCard.tsx` (alebo prázdny stav Pre teba z 080), `web/src/i18n/*.ts`, `docs/design.md` 4 a 7c (bloky 079, 080, 087).

### Problém (Matej)
Bez obľúbených žánrov dostala každá akcia sediaceho typu neutrálnych 40 bodov → ✦ „skoro všetko“.

### 1. Skóre (zmena v `forYouScore`)
- **Používateľ nemá obľúbené žánre → žánrová časť 20** (nie 40). Typ sám teda na ✦ nestačí; ✦ = sediaci typ + obľúbené miesto (20 + 20 = 40).
- **Len typy, bez obľúbených miest aj žánrov → skóre 0** (žiadne ✦; ruší sa výnimka „sediaci typ stačí na ✦“ z 087 / Matej 2026-11-21 12:26).
- Akcia bez žánrov (používateľ žánre má) ostáva 40 (bez zmeny).
- Bez vybratých typov (len starší používatelia spred 079 – po časti 2 to nový používateľ nemá): bez zmeny oproti 087.
- Testy: typy + miesta bez žánrov → ✦ len v obľúbených miestach; len typy → 0; typy + žánre ako v 087.

### 2. Prázdne Pre teba pri „len typy“
- Zapnutý čip Pre teba a používateľ má vybraté len typy (žiadne obľúbené miesto ani žáner) → rovnaký prázdny stav ako pri chýbajúcich preferenciách (080), s textom:
  - sk: „Pridaj obľúbené žánre alebo miesta a označíme ti akcie, ktoré ťa budú baviť ✦“
  - cs: „Přidej oblíbené žánry nebo místa a označíme ti akce, které tě budou bavit ✦“
  - en: „Add favourite genres or places and we'll mark events you'll enjoy ✦“
  - tlačidlo **Nastaviť / Nastavit / Set up** → Preferencie akcií.
- Pri úplne chýbajúcich preferenciách ostáva text z 080.

### 3. Aspoň jeden typ je povinný (Matej: typ je základ)
- **Onboarding, krok Typy:** bez vybratého typu sa **nedá pokračovať ani preskočiť** – „Ďalej“ sa zatrasie (ako v 080) a **„Preskočiť“ sa v tomto kroku nezobrazuje**. Preskočiť **celý** onboarding na uvítaní (s potvrdením) ostáva možné – potom nemá preferencie vôbec (ani typy) a platí správa z 080. (Matej 13:23 potvrdil toto znenie z 13:18; úprava zo 13:20 – „Preskočiť“ v kroku Typy preskočí celý onboarding – bola nedorozumenie a **neplatí**.)
- **Preferencie akcií:** keď už má používateľ aspoň jeden typ, **nemôže mať 0 typov** – posledný vybratý typ sa nedá zrušiť, ťuk naň sa zatrasie, výber ostane (Matej 13:20). Kultúra so všetkými podtypmi zrušenými = kultúra ostáva vybratá bez podtypov (bez zmeny).
- `docs/design.md` 7c: doplň blok „Zmena 2026-11-22 (091)“.

## Overenie a report
- `npm test -- --reporter=dot` (časti 1–3), `npm run build`, `deploy-app` (číslo behu).
- Počty z aktuálneho `events.json` (príkaz z 087) pre: (a) koncert + DJ, obľúbené Fuchs2 a Cross, bez žánrov; (b) koncert + DJ, bez miest a žánrov – pred a po zmene.
- Snímka `docs/tasks/091/for-you-types-only.jpg` (prázdny stav pri „len typy“).

## Report

**2026-11-22, commit e74e0c8** (práca), report v nasledujúcom commite. **Hotovo.**

### Čo je hotové
1. **Skóre** (`web/src/core/search.ts`): nová `hasOnlyTypes(p)` (typ vybratý, žiadne obľúbené miesto ani žáner) → `forYouScore` = 0. S vybratými typmi a bez obľúbených žánrov je žánrová časť **20** (✦ len so sediacim typom v obľúbenom mieste: 20 + 20). Akcia bez žánrov pri používateľovi so žánrami ostáva 40; bez vybratých typov bez zmeny oproti 087.
2. **Prázdne Pre teba pri „len typy“**: `forYouNeedsSetup` vracia `'none' | 'typesOnly' | null`; `EventsPage` ukáže tú istú kartu (080) s novým textom `prefs.forYouTypesOnly` (sk/cs/en zo zadania), tlačidlo Nastaviť → Preferencie akcií. Bez preferencií ostáva text 080.
3. **Aspoň jeden typ**: onboarding – v kroku Typy sa „Preskočiť“ nezobrazuje, „Ďalej“ bez typu sa zatrasie (080, bez zmeny); preskočenie celého onboardingu na uvítaní ostáva. Preferencie akcií – `TypesPicker keepOne`: posledný vybratý typ sa nedá zrušiť (`canToggleTypeOff`), ťuk zatrasie kartou (~300 ms + vibrácia), výber ostane. Kultúra so zrušenými podtypmi ostáva vybratá (bez zmeny).
4. `docs/design.md` 7c: blok „Zmena 2026-11-22 (Matej, úloha 091)“. `docs/decisions.md`: nový riadok 2026-11-22.

### Rozhodnuté samostatne (detail v decisions.md 2026-11-22)
1. Podtypy kultúry sa počítajú k typom → aj kultúra s podtypmi má pri „len typy“ skóre 0 (inak by ✦ nesedel s prázdnym stavom).
2. Kultúrna časť skóre (podtyp 80, kultúra bez podtypov 40) bez zmeny – zadanie mení len žánrovú časť. Dôsledok: typ kultúra bez podtypov + obľúbené miesto → kultúrne akcie majú ✦ aj mimo obľúbených miest. Ak to má byť ako pri hudbe (20), je to jeden riadok.
3. Pri poslednom type sa trasie karta toho typu (rovnaká animácia ako Ďalej v onboardingu). V onboardingu sa typy dajú odznačiť na 0 (Ďalej sa potom zatrasie).

### Overenie
- `npm test -- --reporter=dot`: **18 súborov, 296 testov passed** (nové: typy + miesta bez žánrov → ✦ len v obľúbených miestach; len typy → 0 vrátane kultúry s podtypmi; typy + žánre ako v 087; `forYouNeedsSetup` 'typesOnly'; posledný typ sa nedá zrušiť).
- `npm run build`: OK.
- `deploy-app`: beh **45029498250** (commit e74e0c8) – success; nasadený `assets/index-CXm2mBJP.js` obsahuje „Pridaj obľúbené žánre alebo miesta“.
- Playwright `tests/playwright/screenshots-091.spec.ts` (2 testy passed, lokálny dev server, `events.json` z Pages): karta „len typy“ s novým textom; v Preferenciách po zrušení DJ sa koncert nedá zrušiť (`data-shake=1`, uložené `types: ["concert"]`); v onboardingu krok Typy bez „Preskočiť“, Ďalej bez typu sa trasie.
- Pipeline sa nespúšťal (mení sa len appka).

### Čísla
`events.json` z Pages (`generated_at` 2026-11-22T14:16:04+01:00), stiahnutý do `site/events.json`, Kedykoľvek = 838 nadchádzajúcich. Príkaz (z `web/`, 2026-11-22 14:47): `npx vite-node scripts/for-you-091.ts ../site/events.json` (po); pred = rovnaký príkaz s druhým argumentom = kópia `search.ts` z 8354988 (`git show 8354988:web/src/core/search.ts > src/core/search_087tmp.ts`, potom zmazaná).

| Preferencie | Pred (087) ✦✦ / ✦ / nič | Po (091) ✦✦ / ✦ / nič |
|---|---|---|
| (a) koncert + DJ, obľúbené Fuchs2 a Cross, bez žánrov | 0 / 560 / 278 (✦ mimo obľúbených miest 529) | 0 / **31** / 807 (✦ mimo obľúbených miest **0**) |
| (b) koncert + DJ, bez miest a žánrov | 0 / 560 / 278 | 0 / **0** / 838 |

### Snímky
`docs/tasks/091/for-you-types-only.jpg` (390 × 844, JPEG 80; `tests/playwright/screenshots-091.spec.ts`, z `web/` s `NODE_PATH=web/node_modules`), na 1. pokus. Neprezeral som ju.

### Otvorené
- Bod 2 z rozhodnutí (kultúra bez podtypov + obľúbené miesto = ✦ všade) – potvrď alebo zmeň.
