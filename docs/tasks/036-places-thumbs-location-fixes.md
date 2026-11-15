# 036: Náhľady obrázkov miest, rýchla poloha, opravy po 035

## Zadanie

**Čítaj:** `design.md` 1 + 5; `docs/data-model.md` len časť o venue v `events.json` (`grep -n "image_url" docs/data-model.md`); `web/src/pages/PlacesPage.tsx` (komponent obrázka hore v súbore); v `web/src/pages/MapPage.tsx` `updateMarkers` (vetvy `leaving` a odstraňovanie pinov), nočný `useEffect` (~r. 300–330), `handleLocationClick` a úvodný pohľad s `getCurrentPosition` (~r. 730); `pipeline/main.py` (kde sa zapisuje `events.json`); `.github/workflows/daily.yml`.

Úloha je malá, štyri samostatné časti. Rob ich v tomto poradí, každú s vlastným commitom.

### 1. Chyba z 035: pin sa po rýchlom návrate stratí
Príčina (hlavný chat z kódu): pri odchode pinu sa spustí `setTimeout(cleanup, 250)` a `animationend` → `marker.remove()`. Keď sa miesto vráti počas miznutia, vetva `leaving` pin vráti do `markersRef`, ale časovač ani poslucháč nezruší. Po 250 ms sa marker odstráni z mapy, hoci je vo `markersRef`, a pin chýba, kým sa niečo nezmení (rýchle Obľúbené zap/vyp, rýchle prepnutie dňa a späť).
- Ulož do záznamu odchádzajúceho pinu id časovača a funkciu `cleanup`; pri návrate časovač zruš a `cleanup` deaktivuj (napr. príznak `cancelled`).
- Návrat má byť plynulý z aktuálneho stavu (podľa 035 F), nie skok: napr. trieda s `transition` na `opacity`/`transform` namiesto zrušenia animácie, alebo `getAnimations()` + `reverse()`. Vyber jednoduchšie riešenie, ktoré funguje v Chrome na Androide.
- Test (vitest, čistá logika ak sa dá vyčleniť; inak Playwright): odchod → návrat do 100 ms → po 400 ms je pin na mape.

### 2. Zastaraný deň po návrate z pozadia
Nočný `useEffect` rieši polnoc a 5:00, ale nie prípad, keď appka ostane na pozadí cez 5:00 bez noci medzi tým (napr. zatvorená o 23:00, otvorená o 9:00 ďalší deň: `wasNight` aj `isNight` sú false, nič sa neprepne). Potom ostane vybraný včerajší dátum. Pri `visibilitychange`/`focus`: ak je vybraný dátum (nie `NIGHT_DAY`) skorší ako `getToday(now)`, nastav `isNightTime(now) ? NIGHT_DAY : getToday(now)`. Test na čistú funkciu „aký deň po návrate“.

### 3. Náhľady obrázkov miest (Matej súhlasil 2026-11-15)
Príčina čiernych/odrezaných riadkov v Miestach pri scrolle (hypotéza, neoverená v telefóne): obrázky miest sú v plnej veľkosti (napr. Čitárna `…-scaled.jpg` ~2560 px, Kasárna `kreslena-mapa…jpeg`) a telefón ich pri scrolle zmenšuje na 48 px. Oprava v pipeline:
- Nový krok po zápise venues: pre každé miesto s `image_url` stiahni obrázok (rovnaký User-Agent a slušnosť ako ostatné sťahovanie, timeout, max. 1 request na miesto), zmenši na štvorec 160 × 160 px (`cover`, stred), ulož ako JPEG kvalita 80 do `site/img/venues/<venue_id>.jpg`. Pridaj `Pillow` do `requirements.txt`.
- Sťahuj len pri zmene: priečinok náhľadov v `actions/cache`, kľúč = hash zoznamu `venue_id + image_url`. Pri zmene URL jedného miesta sa stiahne len to miesto (súbor s hashom URL vedľa náhľadu stačí).
- Chyba pri sťahovaní alebo nečitateľný obrázok: warning v logu, miesto bez náhľadu, pipeline beží ďalej.
- V `events.json` pri venue nové pole `image_thumb` (relatívna cesta `img/venues/<id>.jpg` alebo `null`). Zapíš do `data-model.md` (Matej odsúhlasil).
- `PlacesPage`: použije `image_thumb`, ak nie je, ikonu typu ako dnes (`image_url` v zozname už nie). `<img>` s `width`/`height` atribútmi a `decoding="async"`.
- Iné obrazovky nemeň (obrázky akcií sú samostatná vec, backlog).

### 4. Rýchla poloha (Matej 2026-11-15)
Príčina: `handleLocationClick` volá `getCurrentPosition` bez `maximumAge`, takže každé ťuknutie čaká na úplne novú polohu; poloha sa medzi ťuknutiami nesleduje.
- Po prvom úspešnom zameraní (ťuknutím alebo úvodným pohľadom) spusti `watchPosition` (`enableHighAccuracy: true`, `maximumAge: 10000`) a priebežne aktualizuj `userLocation` (bodka sa hýbe).
- Sledovanie beží len keď `isVisible && document.visibilityState === 'visible'`; inak `clearWatch`. Mapa ostáva namontovaná ako dnes, stav mapy sa nemení. Pri návrate sa sledovanie znova zapne.
- Ťuknutie na tlačidlo: ak je známa posledná poloha, `flyTo` okamžite na ňu (bez čakania a bez točiaceho sa načítania); inak ako dnes, ale `getCurrentPosition` s `maximumAge: 60000`.
- Appka o polohu sama nežiada: sledovanie sa nikdy nespustí bez predošlého udeleného povolenia.

### Overenie
- `npm test`, `npm run build` vo `web/`, `pytest -q`; číslo nasadenia (beh Actions) a číslo denného behu, ktorý vyrobil náhľady (spusti ručne).
- V reporte: zoznam vyrobených náhľadov s veľkosťou súborov (z logu behu), druhý beh potvrdí, že sa nič nesťahovalo (log).
- Snímka `docs/tasks/036/01-miesta.jpg` (zoznam Miest s náhľadmi, Playwright, syntetické dáta OK).
- Žiadne ďalšie snímky; časť 1, 2 a 4 overí Matej v telefóne.

## Report
