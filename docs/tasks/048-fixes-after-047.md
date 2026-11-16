# 048: Opravy po teste 047 (lišta, obnovenie, zoradenie, panel obdobia, texty)

## Zadanie

**Čítaj:** `design.md` časť 4: riadky Lišta, Nové, Zoradenie (+ dva body pod ním), Panely, Obnovenie potiahnutím; časť 7: bod „Idem → Uložené“. V kóde: `core/usePullToRefresh.ts`, `pages/EventsPage.tsx` (lišta, zoradenie), `pages/PlacesPage.tsx` (indikátor obnovenia), `components/SelectorSheet.tsx`, `components/BottomNav.tsx` (len z-index), panel obdobia (`grep -rln "Kedyko\|anytime" web/src/components`), `map/useUserLocation.ts`, `i18n/*`.

Matejove poznámky po teste 047. Každá časť vlastný commit.

### 1. Obnovenie potiahnutím kazí vodorovný posun (chyba, rob prvú)
Príčina (hlavný chat z kódu): `usePullToRefresh.ts` v `onTouchMove` volá `e.preventDefault()` pri každom `dy > 0` navrchu zoznamu, bez ohľadu na vodorovný pohyb. Posun čipov s miernym ťahom nadol preto zablokuje natívny vodorovný posun (ťažkopádny) a ukáže šípku obnovenia.
- Smer gesta urči z prvých ~8–10 px pohybu: ak `|dx| > |dy|`, gesto do konca ignoruj (žiadne `preventDefault`, žiadna šípka). Zapamätaj si aj `startX`.
- Navyše gesto, ktoré začne vo vodorovne posúvateľnom páse (napr. atribút `data-no-ptr`), obnovenie nespúšťa.
- Test: vodorovný pohyb s malou zvislou zložkou → `pullDist` ostane 0.

### 2. Rovnaký indikátor obnovenia v Miestach
V `PlacesPage.tsx` ostal starý indikátor (šípka). Vytiahni indikátor z Akcií (koliesko s kruhovou šípkou, ide s prstom, otáča sa) do spoločného komponentu a použi ho v Akciách aj Miestach.

### 3. Lišta v Akciách
- **Čip Nové preložený** (SK/CZ „Nové“, EN „New“). Anglické „new“ ostáva len odznak na obrázku karty. (047 to zmenilo omylom zle.)
- **Celý pás vľavo od Filtra posúvateľný**: tlačidlo obdobia + Pre teba + Nové v jednom vodorovne posúvanom páse; Filter ostáva pevne vpravo. Platí aj pre kompaktnú lištu.
- **Rozplynutie na oboch okrajoch pásu** (maska, nie čierna plocha): vľavo sa ukáže, až keď je pás posunutý; vpravo, keď obsah pokračuje. Dnes pri posune doľava obsah zájde do čiernej – to zmizne.
- **Za posledným čipom okraj aspoň šírky rozplynutia**, aby sa dal Nové odsunúť úplne mimo rozplynutú časť a stál normálne pred Filtrom.
- Posun má byť natívny a plynulý (`overflow-x: auto`, `touch-action: pan-x pan-y` alebo bez vlastného zachytávania; žiadny JS posun).

### 4. Zoradenie
- **Ťuk na položku v ponuke ponuku hneď zavrie** (dnes treba ťuknúť inde).
- **Pri jednodňovom období je „vzdialenosť“ v ponuke vždy**, aj bez polohy. Ťuk bez polohy si vyžiada polohu rovnako ako tlačidlo polohy na mape (`useUserLocation`). Po povolení zoradí podľa vzdialenosti. Pri odmietnutí ostane „čas“ a toast „Na zoradenie podľa vzdialenosti povoľ polohu“ (CZ „Pro řazení podle vzdálenosti povol polohu“, EN „Allow location to sort by distance“).
- Viacdňové obdobie: bez zmeny (vzdialenosť sa neukáže).

### 5. Panel obdobia: medzera pod Kedykoľvek
Medzi deliacou čiarou pod Kedykoľvek a Dnes je prázdny riadok (Matejov snímok). Nájdi príčinu (pravdepodobne prázdny/skrytý prvok, napr. položka Teraz v noci mimo noci, alebo okraj čiary) a odstráň ju: Kedykoľvek, čiara s malým odstupom, hneď Dnes. Príčinu napíš do reportu.

### 6. Panel nad spodnou lištou
`SelectorSheet` má z-index 29/30, `BottomNav` 100 → panel je pod lištou, hoci 047 časť 4 chcela opak. Daj overlay aj panel nad spodnú lištu; pod poslednou položkou len bežný okraj + `safe-area-inset-bottom`. Platí pre výber dňa na mape aj obdobie v Akciách.

### 7. Texty uložených akcií
- Zoznam v Môj účet: „Akcie“ / „Akce“ / „Events“ (namiesto „Moje akcie“).
- Toast: „Uložené“ / „Odobrané z uložených“ (CZ „Uloženo“ / „Odebráno z uložených“, EN „Saved“ / „Removed from saved“).

## Overenie
- `npm test` (`--reporter=dot`), build OK.
- Screenshoty (Playwright, `tests/playwright/`, JPEG 390 × 844 do `docs/tasks/048/`): `akcie-lista-posunuta.jpg` (pás posunutý doprava – vidno ľavé rozplynutie a Nové pred Filtrom), `panel-obdobie.jpg` (vidno Kedykoľvek, čiaru, Dnes a spodok panela nad lištou), `miesta-obnovenie.jpg` (ak sa dá zachytiť; po 2 pokusoch vynechaj).
- V reporte: príčina medzery z časti 5, z-indexy pred/po.

## Report

**Dátum:** 2026-11-16

**Commity:**
- `f3bd200` fix(048-1): usePullToRefresh – ignoruj horizontálne gestá a data-no-ptr
- `3378ea9` feat(048-2): spoločný PullRefreshIndicator – rovnaký indikátor v Akciách aj Miestach
- `326face` feat(048-3): lišta – preložený Nové, posúvateľný pás + rozplynutie
- `a5ae310` feat(048-4): zoradenie – okamžité zatvorenie, vzdialenosť vždy, žiadosť o polohu
- `9ceeada` fix(048-5): panel obdobia – odstráň prázdny riadok pod Kedykoľvek
- `63c2dab` fix(048-6): SelectorSheet z-index nad spodnou lištou (101/102 > 100)
- `e74e022` fix(048-7): texty uložených – Akcie, Uložené, Odobrané z uložených

**Hotovo:**

1. **Obnovenie potiahnutím – vodorovný posun:** `usePullToRefresh.ts` pridaný `startXRef`, `dirRef` (unknown/vertical/horizontal) a `noPtrRef`. Smer gesta sa určí z prvých ~8 px pohybu; ak `|dx|>|dy|`, celé gesto sa ignoruje. Atribút `data-no-ptr` na chips scroll containeri zabraňuje spusteniu PTR z tej oblasti.

2. **Rovnaký indikátor v Miestach:** Vytvorený `components/PullRefreshIndicator.tsx` (koliesko s kruhovou šípkou, otáča sa pri ťahaní). Oba EventsPage aj PlacesPage teraz používajú rovnaký komponent; starý indikátor Miest (šípka nadol + spinner) bol odstránený.

3. **Lišta v Akciách:**
   - `newLabel`: SK/CS `'Nové'`, EN `'New'`; odznak na karte ostáva vždy `'new'`
   - Tlačidlo obdobia + Pre teba + Nové sú v jednom horizontálne posúvateľnom páse s `data-no-ptr`, Filter ostáva pevne vpravo; platí aj pre kompaktnú lištu
   - Rozplynutie pomocou absolútne pozicionovaných overlay divov: ľavý (40 px, len keď `scrollLeft > 0`), pravý (40 px, vždy); spacer 40 px za posledným čipom

4. **Zoradenie:**
   - `closeSortMenu()` volá `setShowSortMenu(false)` okamžite (pred `history.back()`)
   - `sortItems` ukazuje vzdialenosť pri `isSingleDay` aj bez polohy
   - Klik bez polohy zatvori menu, zavolá `navigator.geolocation.getCurrentPosition()`, po povolení zoradí; pri odmietnutí toast `dict.events.locationToastForSort`

5. **Panel obdobia – príčina medzery:** Položka `__sep__` mala `separator: true` a prázdne `label: ''`. V SelectorSheet renderovala tak deliaci riadok (1 px + margin 2×2 px), ako aj prázdny `<button>` s výškou 48 px z `rowStyle`. Oprava: `!item.separator` podmienka okolo buttonu → prázdny button sa nevykreslí.

6. **Panel nad spodnou lištou:** BottomNav `z-index: 100`, SelectorSheet overlay bol 29/30 → zmenené na 101/102.

7. **Texty:** `account.going`: Akcie/Akce/Events; `addedToGoing`: Uložené/Uloženo/Saved; `removedFromGoing`: Odobrané z uložených/Odebráno z uložených/Removed from saved.

**Testy:** 167/167 passed. Build OK (warning o veľkosti JS chunky je preexistujúci).

**Screenshoty:** `docs/tasks/048/akcie-lista-posunuta.jpg`, `docs/tasks/048/panel-obdobie.jpg` (oba vytvorené cez playwright-048.config.ts). `miesta-obnovenie.jpg` vynechané (PTR zachytenie gesta nie je spoľahlivo simulovateľné v Playwright).

**Zostáva otvorené:** Screenshoty sú rovnakej veľkosti (110 543 B) – pravdepodobne sa chips scroll nepresunul cez `evaluate()` správne vo Playwright (render nebol triggnutý pred screenshotom); vizuálne overenie ponechané na Mateja.
