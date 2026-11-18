# 071: Ikony podtypov kultúry, bez štítkov podtypov, ikona na karte mapy, štítky len po anglicky

## Zadanie

**Schválené Matejom 2026-11-18 20:12.** Len frontend (`web/`). **Pipeline nespúšťaj** (pravidlo v `CLAUDE.md`), over len nasadenie `deploy-app`. **Záväzné:** nič nevymýšľaj, drž štýl appky; mení sa **len** to, čo je nižšie. Čo nie je jasné, spýtaj sa.

**Čítaj:** `docs/design.md` časť 1 (Štítky, Ikony), časť 4 (bloky „Zmena 2026-11-18 20:12“ a „19:31“); report 070; `web/src/core/eventType.ts` (`CULTURE_FORMATS`, `EventIconKey`, `eventIconKey`, `eventTags`, `primaryTypeTag`), `web/src/map/markers.ts` (`ICON_SVG`, `typeIconSvg`), `EventTypeIcon` (veľká ikona pri akcii bez obrázka), `web/src/components/EventRow.tsx` (`TypeIconPill`), `EventPanel.tsx` (karta na mape), `pages/VenuePage.tsx` (program podniku), `web/src/i18n/*.ts` (`tags`, `tagLabel`).

### 1. Nové ikony podtypov kultúry
Pribudnú 4 kľúče ikon, všade, kde sa dnes ikona typu kreslí (piny na mape, `TypeIconPill`, veľká ikona pri akcii bez obrázka, všetko cez jedno miesto – `ICON_SVG` / `EventTypeIcon`). SVG v `viewBox 0 0 24 24`, `C` = farba ikony, `BG` = farba plochy pod ikonou (pin `EVENT_TYPE_COLOR`, pilulka farba pilulky, plocha bez obrázka jej farba).

- **`talk`** – dve bubliny (obrys ako ostatné, `stroke-width 2`, `round`):
  `<path d="M14 9a2 2 0 0 1-2 2H6l-4 4V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2z"/><path d="M18 9h2a2 2 0 0 1 2 2v11l-4-4h-6a2 2 0 0 1-2-2v-1"/>`
- **`quiz`** – žiarovka (obrys):
  `<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>`
- **`opening`** – obraz (obrys):
  `<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>`
- **`workshop`** – prekrížené kladivo a kľúč, **plná** ikona (ako tanec), variant „workshop B“, ktorý Matej vybral:
  ```
  <g fill="C">
    <g transform="rotate(-45 13.5 13.5)"><rect x="12" y="6" width="3" height="15" rx="1.5"/></g>
    <g transform="rotate(-45 6.3 6.3)"><rect x="1.8" y="4.3" width="9" height="4" rx="1"/></g>
  </g>
  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" fill="C" stroke="BG" stroke-width="1.6" stroke-linejoin="round"/>
  ```
  Kľúč má obrys vo farbe plochy pod ním (`BG`), aby bolo kríženie čitateľné. Kresba je ručná – **len** ju opticky zarovnaj (stred, veľkosť ako ostatné ikony), tvar nemeň.

**Výber ikony kultúry** (`eventIconKey`): ak je `primary_format` podtyp kultúry, rozhoduje on; inak prvý podľa poradia `film` → `stand-up` → `dance` → `talk` → `workshop` → `quiz` → `opening` → masky (`theatre`, `performance`, ostatné). Typ „other“ ostáva masky. (Poradie určil hlavný chat.)

### 2. Štítky podtypov kultúry sa v zoznamoch nezobrazujú
- V **riadku Akcií**, na **karte na mape** a v **programe podniku** sa nezobrazujú štítky `film`, `stand-up`, `dance`, `theatre`, `talk`, `workshop`, `quiz`, `opening` – typ nesie ikona. **`performance` ostáva** ako štítok (ikona masiek je divadlo).
- **Náhradný štítok s názvom typu** (dnes `eventTags` vráti `[typ]`, keď akcia nemá iný štítok) **sa ruší**: akcia bez štítkov má v riadku len pilulku s ikonou.
- **Stránka akcie bez zmeny** (plnofarebný prvý štítok typu, napr. `talk`, `film`, za ním ostatné štítky ako dnes). **Môj účet bez zmeny.**

### 3. Ikona typu aj na karte na mape
- `TypeIconPill` ako prvá pilulka v riadku štítkov karty, rovnako ako v Akciách (nahrádza „na karte na mape nie“ z 19:42). Ostatné na karte bez zmeny.

### 4. Štítky vždy po anglicky
- Pravidlo `design.md` časť 1: štítky po anglicky v každom jazyku appky. **Zmaž všetky preklady štítkov v `cs.ts` a `sk.ts`** (`tags`; dnes 30 kľúčov: `talk`, `physical-theatre`, filmové žánre, scénické žánre…). V `en.ts` ostanú len popisy bez pomlčky (`physical theatre`, `puppet theatre`, `short film`, `cult classic`…), **`talk & reading` → `talk`**. Platí všade, aj na stránke akcie.
- Prejdi `web/src` a over, že iný štítok akcie alebo podniku sa nikde inde nepreklada; nájdené vypíš v reporte.

## Overenie a report
- `npm test`, `npm run build`; číslo nasadenia (`deploy-app`).
- Snímky JPEG 390 × 844 do `docs/tasks/071/`: `akcie-dnes.jpg` (s kultúrnou akciou), `mapa-karta.jpg`, `program-podniku.jpg`, `detail-cs.jpg` (stránka kultúrnej akcie s appkou v češtine – štítky po anglicky), a `ikony-3x.png` – všetkých 11 ikon (concert, party, dj, film, stand-up, dance, masky, talk, workshop, quiz, opening) zväčšené 3× na pine a v pilulke.
- Report: čo hotové, zoznam zmazaných prekladov, otvorené body.
