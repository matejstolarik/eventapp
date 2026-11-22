# 087: Pre teba ako zhoda (dva stupne) + zoradenie „Najlepšia zhoda“

## Zadanie

**Schválené Matejom 2026-11-21 12:26–12:37.** Mení len appku (`web/`) → **pipeline nespúšťaj**, over len `deploy-app`. ~~Spustiť po 086~~ **Spúšťa sa pred 086** (zmena 12:58, Matej: 086 čaká na denný beh ~14:00; obe menia appku, idú za sebou, nie naraz – 086 nadviaže na zmeny z 087 v `search.ts`). Čo nie je jasné, spýtaj sa (nevymýšľaj UI).

**Čítaj:** `docs/design.md` 4 (čip Pre teba, odznak na obrázku, zoradenie, počet) a blok „Zmena 2026-11-19 … nové pravidlo Pre teba“; `docs/ai-rules.md` C1 (žánre zoradené od hlavného); `web/src/core/search.ts` (`isForYou`, `ForYouPrefs`), `web/src/core/filter.ts` (`filterTypeOf`, `eventUmbrellas`, `cultureSubtype`), `web/src/core/period.ts` (`sortEvents`, `SortMode`), `web/src/components/EventRow.tsx` (`EventImage43`, odznak ✦), `web/src/components/EventPanel.tsx`, `web/src/pages/EventsPage.tsx`, `web/src/i18n/*.ts`. `docs/decisions.md` – `grep -n` „pre teba najprv“, „Pre teba“.

### 1. Skóre zhody 0–100 (nahrádza áno/nie z 079; nová funkcia v `search.ts`, `isForYou` = skóre ≥ 40)
- **Typ je brána:** ak má používateľ vybraté typy a typ akcie (`filterTypeOf`) medzi nimi nie je → **0**.
- ~~Žánre 0–80 bodov – pomer s váhami podľa poradia~~ **(zrušené 12:51, Matej: poradie žánrov nie je poradie dôležitosti – AI ho v praxi preberá z poradia v popise – nemôžeme na ňom stavať).**
- **Žánre bez poradia (model D, Matej 12:51):** každý žáner akcie sa prevedie na zastrešujúce (`eventUmbrellas` / hierarchia) a je „zhodný“, ak niektoré zo zastrešujúcich je v obľúbených žánroch. **Ak je zhodný aspoň jeden → 50 bodov + 30 × (počet zhodných žánrov akcie ÷ počet všetkých žánrov akcie)**; žiadny zhodný → 0 žánrových bodov (akcia môže mať body len za miesto). Poradie žánrov sa **nepoužíva**.
  - Príklady (testy): `[rock]`, obľúbený rock → 80; `[rock, hip-hop]`, obľúbený hip-hop → 65; `[rock, hip-hop]`, obe → 80; Divo Institute `[blues, rock, techno, post-punk, shoegaze, experimental]`: obľúbené alternative+punk → 60, alternative+punk+rock → 65, punk → 55; s obľúbeným Paláca Akropolis +20 → 80 / 85 / 75.
  - **Akcia bez žánrov** → 40.
  - **Používateľ nemá obľúbené žánre** → 40 pri sediacom type.
  - **Kultúra:** podtyp akcie medzi vybratými podtypmi → 80; kultúra vybratá bez podtypov → 40; podtyp nesedí → 0 (brána).
- **Obľúbené miesto +20.**
- **Bez vybratých typov** (preskočené): brána neplatí, výpočet rovnaký (žánre + miesto).
- **Bez miest aj bez žánrov, len typy** (Matej 12:26): sediaci typ → 40 (✦), aby používateľ, ktorý vybral len typy, nemal prázdne Pre teba.
- **Bez akýchkoľvek preferencií** → 0 (správa „Nastav si…“ z 080 ostáva).
- Strop 100.

### 2. Dva stupne (nie percentá – Matej)
- **✦✦ „Presne pre teba“:** skóre ≥ 75. **✦ „Mohlo by ťa baviť“:** 40–74. Pod 40 nič.
- Odznak na obrázku (Akcie, karta na mape, program miesta – všade, kde je dnes ✦): pri ✦✦ **dve iskry vedľa seba v tom istom štýle a mieste** ako dnešný odznak (bez textu, bez pozadia, s obrysom). Texty „Presne pre teba“ / „Mohlo by ťa baviť“ sa v UI nezobrazujú (len interne a v teste).
- Počet „· N pre teba“ = ✦ aj ✦✦ spolu.

### 3. Čip vs. zoradenie (Matej 12:35–12:37)
- **Čip „Pre teba“** len filtruje: ukáže akcie so skóre ≥ 40 (✦ aj ✦✦).
- **Nové zoradenie „Najlepšia zhoda“** (cs „Nejlepší shoda“, en „Best match“): podľa skóre zostupne, pri rovnosti dátum/čas. **Ponuka zoradenia ho obsahuje len pri zapnutom čipe Pre teba** (Matej: bez Pre teba ho nedávať).
- **Zapnutie čipu** prepne zoradenie na Najlepšiu zhodu. **Vypnutie čipu** vráti zoradenie, ktoré bolo pred zapnutím, ak ho používateľ medzitým ručne nezmenil na iné ako Najlepšia zhoda; ak bolo práve Najlepšia zhoda, vráti predošlé.
- Pamätanie zoradenia ako doteraz.
- Nahrádza rozhodnutie 2026-11-15 „pre teba najprv nie“ (vtedy áno/nie = duplicita s prepínačom; teraz stupnica) – zapíš do `docs/decisions.md`.

### 4. Ostatné
- Mapa nemá zoradenie – len odznak ✦/✦✦ v karte/paneli.
- Logika v `core/` (čisté funkcie), UI len zobrazuje.
- `docs/design.md` 4: doplň blok „Zmena 2026-11-21 (087)“ (skóre, stupne, odznak ✦✦, zoradenie Najlepšia zhoda len pri čipe, prepínanie).

## Overenie a report
- `npm test -- --reporter=dot` (príklady z časti 1 – model D, brána typu, bez žánrov, len typy, kultúra, stupne, prepínanie zoradenia pri čipe), `npm run build`, `deploy-app` (číslo behu).
- Z aktuálneho `events.json` (lokálne, príkaz uveď) pri modelových preferenciách (DJ + Koncert; techno, punk, rock; obľúbené Fuchs2 a Cross Club): koľko akcií ✦✦, ✦, nič – spolu a pre obdobie Dnes; 10 akcií s najvyšším skóre (názov, miesto, žánre, skóre).
- Snímky JPEG 390 × 844 do `docs/tasks/087/`: `events-for-you-best-match.jpg` (čip zapnutý, zoradenie Najlepšia zhoda, viditeľné ✦✦ aj ✦), `sort-menu-for-you.jpg` (ponuka zoradenia pri zapnutom čipe).

## Report

**2026-11-22, commit 8354988** (práca), report v nasledujúcom commite. **Hotovo.**

### Čo je hotové
- `web/src/core/search.ts`: `forYouScore(event, prefs)` 0–100 (brána typu, žánre bez poradia – model D, kultúra 80/40/0, obľúbené miesto +20, strop 100), `forYouTier` (2 = ✦✦ ≥ 75, 1 = ✦ 40–74, 0), interné názvy `FOR_YOU_TIER_NAME`; `isForYou` = skóre ≥ 40.
- `web/src/core/period.ts`: `SortMode` + `'match'`, `sortEvents(..., scoreOf)` – skóre zostupne, pri rovnosti dátum/čas; čistá funkcia `sortAfterForYouToggle` (zapnutie → najlepšia zhoda + zapamätá predošlé; vypnutie → vráti predošlé, ak je stále najlepšia zhoda, inak ostane ručná voľba).
- `EventRow.tsx` (`EventImage43`): `forYou` = stupeň 0/1/2; pri ✦✦ dve rovnaké iskry vedľa seba na tom istom mieste (atribút `data-foryou-tier`). Akcie aj karta na mape (`EventPanel`). Program miesta ✦ nemá ani dnes – bez zmeny.
- `EventsPage.tsx`: položka „najlepšia zhoda“ v ponuke Zoradiť len pri zapnutom čipe; ťuk na čip prepína zoradenie; „Zrušiť filtre“ vypína čip rovnakou cestou. Počet „· N pre teba“ = ✦ + ✦✦ (cez `isForYou`). i18n: sk „najlepšia zhoda“, cs „nejlepší shoda“, en „best match“.
- `docs/design.md` 4: blok „Zmena 2026-11-21 (Matej, úloha 087)“. `docs/decisions.md`: nový riadok 2026-11-22 (nahrádza „pre teba najprv nie“ z 2026-11-15).

### Rozhodnuté samostatne (detail v decisions.md 2026-11-22)
1. Neutrálnych 40 (akcia bez žánrov / používateľ bez žánrov) len pri pozitívne sediacom type; **bez vybratých typov len v obľúbenom mieste** – inak by používateľ bez typov mal ✦ na každej akcii bez žánrov; používateľ len s obľúbenými miestami má ✦ v nich ako doteraz. Zadanie to pre prípad bez typov priamo nehovorí („výpočet rovnaký“) – ak chceš 40 pre každú akciu bez žánrov aj bez typov, je to jeden riadok v `forYouScore`.
2. Do počtu žánrov akcie len hudobné žánre (kultúrne `horror` a pod. nie).
3. Uložené zapnuté Pre teba pri štarte → zoradenie najlepšia zhoda (predošlé = dátum); vrátená vzdialenosť pri viacdňovom období → dátum.
4. Položka ponuky malými písmenami ako ostatné (073).

### Overenie
- `npm test -- --reporter=dot`: **18 súborov, 294 testov passed** (nové: príklady z časti 1 vrátane Divo 60/65/55 a 80/85/75, brána typu, bez žánrov, len typy, kultúra, bez typov, strop, stupne, prepínanie zoradenia, zoradenie podľa skóre).
- `npm run build`: OK.
- `deploy-app`: beh **45019390300** (commit 8354988) – success; nasadený `assets/index-DGSlFtUn.js` obsahuje „najlepšia zhoda“ a `data-foryou-tier`.
- Pipeline sa nespúšťal (mení sa len appka).

### Čísla (modelové preferencie: DJ + koncert; techno, punk, rock; obľúbené Fuchs2 a Cross Club)
`events.json` z Pages (`generated_at` 2026-11-22T12:28:14+01:00, denný beh 45016644298), stiahnutý do `site/events.json`. Príkaz (z `web/`): `npx vite-node scripts/for-you-stats.ts ../site/events.json` (spustené 2026-11-22 12:46).
- Kedykoľvek (688 nadchádzajúcich): **✦✦ 50, ✦ 139, nič 499**.
- Dnes (10 akcií, zvyšné už skončili): **✦✦ 0, ✦ 2, nič 8**.
- Top 10 (skóre | dátum | názov | miesto | žánre):
  - 85 | 2026-11-28 | HARD RAVE & PSYTRANCE | Cross Club | hard-techno, psytrance
  - 85 | 2026-11-28 | Nina Farrina INVITES Henning Baer ☆ Adamatron ☆ 3ever | Fuchs2 | techno, house
  - 85 | 2026-12-03 | F2 LIVE: Dušan Vlk / Asthmaboy Again | Fuchs2 | hip-hop, punk
  - 85 | 2026-12-31 | FLOA: Bert and Friends ★ Madhouse Express ★ Anna Vaverková | Fuchs2 | indie, post-punk
  - 85 | 2026-12-31 | deBasement | Fuchs2 | electronic, punk
  - 85 | 2027-03-20 | RFP CONCERTS & HEARTNOIZE present Fat Dog | Fuchs2 | punk, electronic
  - 80 | 2026-11-24 | THE.SWITCH + KONTUA | Futurum Music Bar | rock
  - 80 | 2026-11-29 | Čechomor Kooperativa tour – Proměny po 25. letech | O2 universum | rock
  - 80 | 2026-11-29 | NERVY | ROXY | rock, pop-punk
  - 80 | 2026-11-29 | Zebrahead / US, special guest: Punk Rock Factory / UK | Lucerna Music Bar | pop-punk, rock

### Snímky
`docs/tasks/087/events-for-you-best-match.jpg`, `docs/tasks/087/sort-menu-for-you.jpg` (390 × 844, JPEG 80; `tests/playwright/screenshots-087.spec.ts`, z `web/` s `NODE_PATH=web/node_modules`). Modelové preferencie, `events.json` z Pages zúžený na 2026-11-28 (vlastné obdobie sa neukladá, preto Kedykoľvek nad jedným dňom: 2 × ✦✦, 2 × ✦), čip zapnutý ťukom. Skript overuje, že zoradenie je „najlepšia zhoda“ a viditeľný je odznak ✦✦ aj ✦. Na 3. pokus (prvé dva zlyhali na chybách skriptu – klik na skrytý čip, neuložené vlastné obdobie). Neprezeral som ich.

### Otvorené
- Bod 1 z rozhodnutí (neutrálnych 40 bez vybratých typov) – potvrď alebo zmeň.
