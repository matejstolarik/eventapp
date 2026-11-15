# 041: Akcie, časť 2 – hľadanie, Pre teba, Nové (+ oprava ikony v mriežke)

## Zadanie

**Čítaj:** `design.md` časť 4 (hlavička, hľadanie, Pre teba, Nové, karta, prázdny stav); snímky `docs/design/screens/10-akcie-mriezka.png`, `12-akcie-hladanie.png` a HTML `docs/design/html/10-akcie-mriezka.html`, `12-akcie-hladanie.html` (rozmery a farby odtiaľ). V kóde: `web/src/pages/EventsPage.tsx`, `core/period.ts`, `core/store.ts` (obľúbené miesta / `profileStore`), `core/eventType.ts`, `map/markers.ts` (len objekt s ikonami typov, r. 6–12), `i18n/*` (sekcia `events`).

### 0. Oprava z 040: ikona typu v mriežke je neviditeľná
Príčina (hlavný chat z kódu): `TypeIcon` v `EventsPage.tsx` kreslí ikonu farbou `EVENT_TYPE_COLOR`, teda rovnakou farbou ako pozadie plochy, preto je na snímke `040/01` len prázdna farebná plocha. Navyše ikony sú vlastné (párty = hviezda, nie pohár).
- Použi ikony z `map/markers.ts` (mikrofón, pohár, gramofón, masky). Vyčleň ich do zdieľaného modulu (napr. `core/typeIcons.ts`), aby ich používala mapa aj Akcie; mapa sa vizuálne nemení.
- Farba ikony na ploche = tmavá dvojica typu (`EVENT_TYPE_DARK`), veľkosť ~40 px, v strede plochy.
- Rovnakú náhradu skontroluj v `EventPanel`, `MyAccountPage` a programe `VenuePage`; ak tam je rovnaká chyba, oprav tiež.

### 1. Hľadanie
Podľa `design.md` 4 a snímky `12`:
- okrúhla lupa 44 px vpravo od nadpisu; ťuk → biele pole sa roztiahne od lupy doľava cez nadpis (200 ms, šírka + priehľadnosť nadpisu), lupa → krížik, klávesnica sa otvorí hneď; zavretie rovnakou animáciou naspäť. **Obsah pod hlavičkou sa nesmie posunúť** (pole je v hlavičke na mieste nadpisu, rovnaká výška 44 px).
- hľadá sa priebežne pri písaní (s malým oneskorením ~150 ms) v: názve akcie, mene miesta, štítkoch akcie (formáty, žánre) a štítkoch charakteru miesta. Bez diakritiky a bez ohľadu na veľkosť písmen („cross“ nájde „Cross Club“, „cajovna“ nájde „Čajovňa“).
- pri otvorení hľadania sa obdobie prepne na **Kedykoľvek** (tlačidlo to ukáže); po zavretí sa vráti predošlé obdobie a text sa vymaže. Zmena obdobia počas hľadania je povolená a platí, kým je hľadanie otvorené.
- Pre teba a Nové platia aj pri hľadaní.
- prázdny výsledok: „Nič sme nenašli.“ (CZ/EN v `i18n`).

### 2. Pre teba a Nové
- Čipy **Pre teba** (ikona iskier, nie srdiečko) a **Nové** za tlačidlom obdobia podľa snímky `10` (40 px; vypnuté `#23232F`/`#B9B6CC`, zapnuté `#FF4D8D`/`#1A0710`). Miesto pre Filter vpravo zatiaľ ostáva prázdne (Filter príde samostatne). Ak sa čipy nezmestia, pás sa posúva vodorovne a na okraji sa stráca – len keď pretekajú.
- **Pre teba** = akcia v obľúbenom mieste (preferencie žánrov zatiaľ nie sú; logiku daj do jednej funkcie v `core`, aby sa neskôr dala rozšíriť o preferencie). Vypnuté: všetky akcie, pri akciách pre teba odznak **pre teba** vľavo hore na obrázku. Zapnuté: len akcie pre teba.
- **Nové** = `first_seen` za posledných 7 dní (vrátane dneška). Odznak **nové** vpravo hore na obrázku vždy; zapnutý čip ukáže len nové.
- Riadok s počtom: „12 akcií · 3 pre teba“ (vypnuté Pre teba), „9 akcií pre teba“ (zapnuté). Ak obľúbené miesta nie sú žiadne, časť „· N pre teba“ sa nezobrazí a ťuk na Pre teba ukáže prázdny stav s textom „Pridaj si obľúbené miesta v záložke Miesta.“
- Stav Pre teba a Nové sa pamätá lokálne (`store.ts`).
- Prázdny stav pri zapnutom Pre teba/Nové: tlačidlo „Zrušiť filtre“ (vypne oba čipy).

### Testy
- Vitest: normalizácia textu bez diakritiky, zhoda hľadania (názov, miesto, štítky), Pre teba, Nové (hranica 7 dní), počty.

### Overenie
- `npm test`, `npm run build`, číslo nasadenia.
- Snímky Playwright (syntetické dáta, aspoň 2 obľúbené miesta, akcie bez obrázka aj s obrázkom, zmrazený čas nedeľa 15. 11. 18:00) do `docs/tasks/041/`: `01-akcie-odznaky.jpg` (vypnuté čipy, viditeľné odznaky a ikony v plochách), `02-akcie-pre-teba.jpg`, `03-hladanie.jpg` (napísané „techno“), `04-hladanie-nic.jpg`.

## Report
