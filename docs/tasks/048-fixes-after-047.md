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
