# 038: Diagnostika čierneho scrollu v Miestach (prepínače cez URL)

## Zadanie

**Čítaj:** `web/src/App.tsx` (časť s `mapMountedRef` a vykreslením záložiek), `web/src/pages/PlacesPage.tsx`, `web/src/components/BottomNav.tsx`. Nič iné.

Matej (Android, Samsung, nainštalovaná PWA): v Miestach je po scrolle spodná časť obrazovky čierna (vodorovná hranica cez celú šírku, aj text a srdiečka) a obsah sa dokreslí po 0,5–1 s. Ide o nestíhanie kreslenia dlaždíc (checkerboarding), nie o rozloženie. Náhľady 160 px z 036 nepomohli (overené 2026-11-15, beh #21). Hlavný chat príčinu z kódu neurčí. Úloha nemá nič opravovať, len pridať dočasné prepínače, ktoré Matej vyskúša v telefóne.

Prepínač = parameter v URL pred `#`, napr. `https://matejstolarik.github.io/eventapp/?dbg=nomap#/miesta`. Čítaj ho raz pri štarte (`new URLSearchParams(location.search).get('dbg')`), hodnoty môžu byť spojené čiarkou (`?dbg=nomap,noimg`). Bez parametra sa appka správa presne ako dnes.

- `nomap` – `MapPage` sa vôbec nenamontuje (záložka Mapa ukáže prázdnu plochu s textom „dbg: nomap“). Overí, či kreslenie brzdí skrytá mapa (WebGL).
- `noimg` – v zozname Miest žiadne `<img>`, vždy ikona typu.
- `layer` – scroll kontajner `PlacesPage` dostane `transform: translateZ(0)` a `will-change: scroll-position`; každý riadok `contain: layout paint`.
- `nonav` – `BottomNav` sa nevykreslí (overí, či plávajúca lišta nad zoznamom nespôsobuje prekresľovanie).
- `clip` – obsahový kontajner v `App.tsx` (`flex: 1, position: relative`) dostane späť `overflow: hidden`, ktoré úloha 033 odstránila (`e68664c`). Matej datuje začiatok problému približne do tohto obdobia.
- `static` – `PlacesPage` sa vykreslí ako bežný blok bez `position: absolute` (scroll kontajner `height: 100%` vnútri rodiča s `overflow-y: auto`), aby sa vylúčil problém s absolútne umiestneným scrollerom.

Ak je aktívny akýkoľvek prepínač, v pravom hornom rohu Miest malý text `dbg: <hodnoty>` (12 px, `#7A78A0`), aby Matej videl, že sa načítal.

### Overenie
- `npm test`, `npm run build`, číslo nasadenia.
- V reporte hotové odkazy na všetky prepínače (jednotlivo a `nomap,noimg`), na kopírovanie do telefónu.
- Žiadne snímky.
- Do `docs/decisions.md` nič; prepínače sa po diagnostike odstránia v ďalšej úlohe.

## Report
