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
- **Onboarding, krok Typy:** bez vybratého typu sa **nedá pokračovať ani preskočiť** – „Ďalej“ sa zatrasie (ako v 080) a **„Preskočiť“ sa v tomto kroku nezobrazuje**. Preskočiť celý onboarding na uvítaní (s potvrdením) ostáva možné – potom nemá preferencie vôbec a platí správa z 080.
- **Preferencie akcií:** posledný vybratý typ sa nedá zrušiť – ťuk naň sa zatrasie, výber ostane. Kultúra so všetkými podtypmi zrušenými = kultúra ostáva vybratá bez podtypov (bez zmeny).
- `docs/design.md` 7c: doplň blok „Zmena 2026-11-22 (091)“.

## Overenie a report
- `npm test -- --reporter=dot` (časti 1–3), `npm run build`, `deploy-app` (číslo behu).
- Počty z aktuálneho `events.json` (príkaz z 087) pre: (a) koncert + DJ, obľúbené Fuchs2 a Cross, bez žánrov; (b) koncert + DJ, bez miest a žánrov – pred a po zmene.
- Snímka `docs/tasks/091/for-you-types-only.jpg` (prázdny stav pri „len typy“).
