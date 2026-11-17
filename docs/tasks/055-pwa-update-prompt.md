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
