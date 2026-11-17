# 055: Upozornenie na novú verziu appky s tlačidlom Aktualizovať

## Zadanie

**Čítaj:** `docs/design.md` časť 1 (farby) a bod „Aktualizácia appky“ v časti 1 (pridaný touto úlohou nižšie – doplň ho tam); kód `web/vite.config.ts` (VitePWA), `web/src/main.tsx` / `App.tsx` (kde sa registruje service worker), existujúci toast (`grep -rn "toast" web/src`).

Problém (Matej): pri novej verzii musí zmazať dáta appky. Príčina (hlavný chat): `registerType: 'autoUpdate'` hľadá novú verziu len pri načítaní stránky; nainštalovaná PWA ostáva v pamäti a znova sa nenačíta, nový service worker čaká na zatvorenie všetkých okien.

### 1. Kontrola a prompt
- VitePWA `registerType: 'prompt'` + `useRegisterSW` z `virtual:pwa-register/react` (alebo ekvivalent).
- Kontrola novej verzie (`registration.update()`): pri štarte, pri návrate do appky (`visibilitychange` → visible) a každú hodinu.
- Keď je nová verzia (`needRefresh`): **karta nad spodnou lištou** (nad obsahom, pod panelmi zdola): tmavá karta ako toast, text „Je dostupná nová verzia“ (CZ „Je dostupná nová verze“, EN „A new version is available“), vpravo ružové tlačidlo „Aktualizovať“ (CZ „Aktualizovat“, EN „Update“), malý krížik na zavretie. Ťuk na tlačidlo → `updateServiceWorker(true)` → appka sa obnoví v novej verzii (stav ako po novom otvorení).
- Zavretá karta sa znova ukáže pri ďalšom návrate do appky, kým sa neaktualizuje.
- `events.json` ostáva `NetworkFirst` (bez zmeny).
- Do `docs/design.md` časť 1 pridaj bod „Aktualizácia appky“ s týmto popisom.

### 2. Overenie
- `npm test` (`--reporter=dot`), build OK, deploy.
- Postup overenia v reporte: nasaď verziu A, otvor ju (Playwright alebo ručne), nasaď verziu B (napr. zmena čísla verzie v Môj účet, ak tam je, inak len build), návrat do appky → karta sa ukáže → Aktualizovať → beží B. Ak sa to v Playwright spraviť nedá, popíš, čo má Matej vyskúšať na telefóne.
- Screenshot `docs/tasks/055/karta-nova-verzia.jpg` (390 × 844), ak sa kartu podarí vyvolať (napr. testovací prepínač `?dbg=update`); po 2 pokusoch vynechať.

## Report

**Dátum:** 2026-11-17. **Commity:** `441d29c` (funkcia, test, screenshot, docs), merge `2582e73`; report v nasledujúcom commite.

### Hotovo
- `web/vite.config.ts`: `registerType: 'prompt'` (bolo `autoUpdate`). `events.json` ostáva `NetworkFirst` bez zmeny.
- Nový `web/src/components/UpdatePrompt.tsx` (`useRegisterSW` z `virtual:pwa-register/react`): `registration.update()` pri štarte, pri `visibilitychange` → visible a každú hodinu; pred kontrolou sa overí, že je online a `sw.js` vracia 200 (inak sa kontrola preskočí, žiadna chyba).
- Karta nad spodnou lištou (12 px nad lištou, 16 px od okrajov), tmavá ako toast (`#2A2838`), text sk/cs/en, ružové tlačidlo Aktualizovať → `updateServiceWorker(true)`, sivý krížik. Zavretá karta sa ukáže znova pri ďalšom `visibilitychange` → visible.
- Prepínač `?dbg=update` kartu ukáže bez novej verzie.
- `docs/design.md` časť 1: nový bod „Aktualizácia appky“. `docs/decisions.md`: nový riadok 2026-11-17.

### Rozhodnutia (samostatne)
- **Vrstvy:** tlačidlá mapy (Moja poloha, `zIndex` 20, bottom 132) prekrývali krížik karty (prvý beh testu to odhalil). Karta má `zIndex` 40 (nad obsahom a ovládaním mapy, pod lištou 100 a panelmi zdola 101+). Panel akcie na mape (`zIndex` 20) je na rovnakom mieste ako karta, preto sa karta pri otvorenom paneli skryje (nová voliteľná prop `onPanelOpenChange` v `MapPage`) – tým platí „pod panelmi zdola“.
- Na stránke akcie/miesta (overlay bez lišty) sa karta neukazuje; ukáže sa po návrate na záložku.

### Overenie
- `npm test -- --reporter=dot`: 191/191 passed. `npm run build` OK.
- Playwright `tests/playwright/update-055.spec.ts` proti produkčnému buildu (`npx vite preview --port 4173`, skutočný service worker; spúšťanie: `NODE_PATH=web/node_modules npx playwright test ../tests/playwright/update-055.spec.ts` z `web/`): verzia A otvorená a ovládaná SW → „nasadenie“ B (marker `<meta name="test-build" content="B">` v `index.html` + nová revízia v `sw.js`) → `visibilitychange` → karta sa ukáže → krížik ju skryje → ďalší návrat ju ukáže → Aktualizovať → stránka sa znovu načíta a beží B (marker prítomný, karta preč). **1 passed (5.6 s).** `dist/` sa po teste vráti do pôvodného stavu.
- Screenshot `docs/tasks/055/karta-nova-verzia.jpg` (390 × 844) zo skutočného stavu `needRefresh` (nie cez `?dbg`), na 1. pokus.
- Deploy: GitHub Actions „Deploy web app“ run 44075817326 úspešný. https://matejstolarik.github.io/eventapp/ → `assets/index-DJYtwFDI.js` obsahuje „Je dostupná nová verzia“; https://matejstolarik.github.io/eventapp/sw.js má `SKIP_WAITING` handler a žiadne bezpodmienečné `skipWaiting()` (= režim prompt).
- Čísla dát: úloha nemení pipeline. `python -c "import json;d=json.load(open('site/events.json',encoding='utf-8'));print(len(d['events']),len(d['venues']),d['generated_at'])"` → 374 akcií, 11 podnikov, `2026-11-16T15:34:59+01:00` (lokálna kópia posledného behu).

### Na telefóne (Matej)
- **Jednorazovo:** na telefóne beží ešte stará verzia s `autoUpdate`. Na prechod na túto verziu stačí appku úplne zavrieť (aj z prehľadu otvorených appiek) a otvoriť znova – dáta mazať netreba. Od ďalšej verzie by mala chodiť karta.
- Test: pri ďalšom nasadení webu (push do `web/`) appku nechaj otvorenú na pozadí, po dokončení deployu sa do nej vráť → karta „Je dostupná nová verzia“ → Aktualizovať → appka sa obnoví.

### Otvorené
- Na skutočnom telefóne (Android/iOS) neoverené; iOS spúšťa `visibilitychange` pri návrate z pozadia, ale správanie SW v nainštalovanej PWA na iOS treba vyskúšať.
