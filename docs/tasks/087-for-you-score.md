# 087: Pre teba ako zhoda (dva stupne) + zoradenie „Najlepšia zhoda“

## Zadanie

**Schválené Matejom 2026-11-21 12:26–12:37.** Mení len appku (`web/`) → **pipeline nespúšťaj**, over len `deploy-app`. **Spustiť po 086** (obe menia appku). Čo nie je jasné, spýtaj sa (nevymýšľaj UI).

**Čítaj:** `docs/design.md` 4 (čip Pre teba, odznak na obrázku, zoradenie, počet) a blok „Zmena 2026-11-19 … nové pravidlo Pre teba“; `docs/ai-rules.md` C1 (žánre zoradené od hlavného); `web/src/core/search.ts` (`isForYou`, `ForYouPrefs`), `web/src/core/filter.ts` (`filterTypeOf`, `eventUmbrellas`, `cultureSubtype`), `web/src/core/period.ts` (`sortEvents`, `SortMode`), `web/src/components/EventRow.tsx` (`EventImage43`, odznak ✦), `web/src/components/EventPanel.tsx`, `web/src/pages/EventsPage.tsx`, `web/src/i18n/*.ts`. `docs/decisions.md` – `grep -n` „pre teba najprv“, „Pre teba“.

### 1. Skóre zhody 0–100 (nahrádza áno/nie z 079; nová funkcia v `search.ts`, `isForYou` = skóre ≥ 40)
- **Typ je brána:** ak má používateľ vybraté typy a typ akcie (`filterTypeOf`) medzi nimi nie je → **0**.
- **Žánre 0–80 bodov – pomer, nie súčet:** žánre akcie sú zoradené od hlavného (ai-rules C1); váha podľa poradia 1, ½, ¼, ⅛… Každý žáner akcie sa prevedie na zastrešujúce (`eventUmbrellas` / hierarchia) a je „zhodný“, ak niektoré zo zastrešujúcich je v obľúbených žánroch. Žánrová zhoda = (súčet váh zhodných žánrov) / (súčet váh všetkých žánrov akcie). Body = 80 × zhoda.
  - Príklady (testy): `[rock]`, obľúbený rock → 80; `[rock, hip-hop]`, obľúbený hip-hop → 80 × 0,5/1,5 = 27; `[hip-hop, rock]`, obľúbený hip-hop → 53; `[rock, hip-hop]`, obe obľúbené → 80.
  - **Akcia bez žánrov** → 40 (polovica), aby nespadla na dno len preto, že AI nenašla žáner.
  - **Používateľ nemá obľúbené žánre** → 40 (polovica) pri sediacom type.
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
- `npm test -- --reporter=dot` (príklady z časti 1, brána typu, bez žánrov, len typy, kultúra, stupne, prepínanie zoradenia pri čipe), `npm run build`, `deploy-app` (číslo behu).
- Z aktuálneho `events.json` (lokálne, príkaz uveď) pri modelových preferenciách (DJ + Koncert; techno, punk, rock; obľúbené Fuchs2 a Cross Club): koľko akcií ✦✦, ✦, nič – spolu a pre obdobie Dnes; 10 akcií s najvyšším skóre (názov, miesto, žánre, skóre).
- Snímky JPEG 390 × 844 do `docs/tasks/087/`: `events-for-you-best-match.jpg` (čip zapnutý, zoradenie Najlepšia zhoda, viditeľné ✦✦ aj ✦), `sort-menu-for-you.jpg` (ponuka zoradenia pri zapnutom čipe).
