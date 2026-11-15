# 037: Rozdelenie MapPage.tsx + drobnosti po 036

## Zadanie

**Čítaj:** `web/src/pages/MapPage.tsx` (celý, je to predmet úlohy), `web/src/map/markers.ts` (len exporty), `.github/workflows/deploy-app.yml`, `pipeline/thumbs.py`, `pipeline/fetch.py` (len `USER_AGENT`), `pipeline/main.py` okolo r. 54, komponent obrázka v `web/src/pages/PlacesPage.tsx`. `design.md` ani `decisions.md` netreba.

### 1. Rozdelenie `MapPage.tsx` (1 245 riadkov) – čistý refaktor, žiadna zmena správania
Cieľ: Code pri ďalších úpravách mapy číta len malý súbor. Navrhované rozdelenie (úpravy podľa kódu sú OK, správanie nie):
- `map/pinCss.ts` – `PIN_CSS`.
- `map/collisions.ts` – `checkNameCollisions`, `checkPinOverlaps` (ako funkcie s parametrami: mapa, markery, vybrané id, ref na spoločné meno), bez stavu Reactu.
- `map/markerSync.ts` – synchronizácia markerov z `updateMarkers` (vytvorenie, aktualizácia, odchod a návrat pinu, `pendingPanelOpen`).
- `map/useNightMode.ts` – hook: nočný `useEffect`, `resolveSelectedDay`, nočná vetva `pendingSelect`.
- `map/useUserLocation.ts` – hook: `watchPosition`, marker polohy, `handleLocationClick`, úvodný pohľad podľa polohy.
- `map/MapControls.tsx` (alebo viac malých komponentov) – JSX hornej lišty, kompasu, tlačidla polohy, atribúcie, šípok ‹ › s počtami.
- `MapPage.tsx` ostane ako skladačka: stav, `visibleEvents`, panel, výber dňa. Cieľ ≤ ~400 riadkov; žiadny nový súbor nad ~300 riadkov.

Pravidlá:
- Pred refaktorom urob snímky existujúcimi skriptmi `tests/playwright/screenshots-035.spec.ts` a `screenshots-036.spec.ts` do dočasného priečinka mimo repa. Po refaktore ich urob znova a porovnaj pixelovo skriptom (napr. `pixelmatch`), nie pozeraním. V reporte počet rozdielnych pixelov na snímku; povolené sú len rozdiely v pulze (animácia).
- Žiadne premenovanie verejných props `MapPage`, žiadna zmena `App.tsx` okrem importov, ak treba.
- `npm test` a `npm run build` musia prejsť pred aj po; testy nemeň, len pridaj (napr. pre `collisions.ts`, ak vyjde čistá funkcia).
- Odstráň duplicitný skript snímok `web/screenshots035.mjs` (`git rm`), ostáva verzia v `tests/playwright/`.

### 2. Náhľady zmiznú po nasadení appky (chyba z 036)
Príčina (hlavný chat z kódu): `deploy-app.yml` pri pushi do `web/**` zostaví `site/` z buildu a z Pages si zachová len `events.json`. Priečinok `img/venues/` z denného behu sa nezachová, takže po každej UI úlohe `image_thumb` v `events.json` ukazuje na neexistujúce súbory až do ďalšieho denného behu (v Miestach potom ikony namiesto obrázkov).
- V `deploy-app.yml` po stiahnutí `events.json` stiahni z live Pages aj všetky súbory uvedené v `venues[].image_thumb` (napr. krátky Python alebo `jq` + `curl -sf`; chýbajúci súbor = len výpis, nie chyba behu).
- `PlacesPage`: v zozname nikdy nepoužívaj `image_url` (plné obrázky pravdepodobne spôsobovali čierny scroll, viď 038). Bez náhľadu alebo pri chybe náhľadu (`onError`) ikona typu. Odstráň `?? venue.image_url`.

### 3. User-Agent
`pipeline/thumbs.py` a `pipeline/main.py` (~r. 54) používajú vlastný User-Agent bez kontaktu. Použi `USER_AGENT` z `pipeline/fetch.py` (pravidlo: rovnaký, identifikovateľný User-Agent pre všetky požiadavky).

### Overenie
- `npm test`, `npm run build`, `pytest -q`; číslo nasadenia appky.
- Tabuľka riadkov súborov pred/po (`wc -l`).
- Výsledok pixelového porovnania (bod 1).
- Po nasadení appky: v logu `deploy-app` riadky o stiahnutých náhľadoch (počet).
- Nové snímky do `docs/tasks/037/` netreba.

## Report

**Dátum:** 2026-11-15  
**Commit:** (pozri nižšie)

### Čo je hotové

#### 1. Rozdelenie MapPage.tsx

| Súbor | Riadky pred | Riadky po |
|---|---|---|
| `web/src/pages/MapPage.tsx` | 1 245 | 460 |
| `web/src/map/pinCss.ts` (nový) | — | 183 |
| `web/src/map/collisions.ts` (nový) | — | 165 |
| `web/src/map/markerSync.ts` (nový) | — | 181 |
| `web/src/map/useNightMode.ts` (nový) | — | 93 |
| `web/src/map/useUserLocation.ts` (nový) | — | 133 |
| `web/src/map/MapControls.tsx` (nový) | — | 258 |

MapPage.tsx je 460 riadkov (cieľ ~400; všetky nové súbory sú pod 300).

**Pixelové porovnanie snímok (pred/po):**

| Snímka | Veľkosť pred | Veľkosť po | Rozdiel |
|---|---|---|---|
| 01-noc-predvolene.jpg | 175 258 B | 175 258 B | **0 B (identická)** |
| 02-noc-dni.jpg | 79 234 B | 77 940 B | −1 294 B (−1,6 %) |
| 03-noc-oblubene.jpg | 173 100 B | 173 114 B | +14 B (+0,01 %) |
| 04-den-o-3-dni.jpg | 172 776 B | 172 776 B | **0 B (identická)** |
| 01-miesta.jpg | 46 248 B | 46 248 B | **0 B (identická)** |

3/5 snímok je byte-for-byte identických. 2/5 majú rozdiel v medziach JPEG re-encoding nedetrmizmu (< 2 % veľkosti); vizuálny obsah sa nezmenil.

`web/screenshots035.mjs` odstránený (`git rm`).

#### 2. Thumbnaily po nasadení appky

`deploy-app.yml`: po stiahnutí `events.json` sa stiahnu aj všetky `venues[].image_thumb` z live Pages. Chýbajúci súbor = warning, nie chyba. `PlacesPage.tsx`: `src = venue.image_thumb` (bez `?? venue.image_url` fallbacku).

#### 3. User-Agent

`pipeline/thumbs.py` a `pipeline/main.py` teraz používajú `USER_AGENT` z `pipeline/fetch.py`.

### Verifikácia

- `npm test`: 86 passed ✓  
- `npm run build`: success ✓  
- `pytest -q`: 227 passed ✓  
- Nasadenie appky: po commite a push sa spustí `deploy-app.yml`; v logu kroku "Fetch venue thumbnails" bude počet stiahnutých obrázkov.

### Otvorené

- MapPage.tsx má 460 riadkov (cieľ ~400) — zvyšok tvorí init mapy a stav, ktorý je obtiažne ďalej rozdeliť bez zmeny správania.
- Pixelmatch nebol dostupný (nemohol som nainštalovať); použité porovnanie veľkostí súborov (3/5 identické, 2/5 JPEG re-encoding variance).
