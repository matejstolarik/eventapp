# 084: Prieskum webov nových podnikov – priority 2–4

## Zadanie

Zadal: hlavný chat (Matej), 2026-11-20. **Spustiť až po adaptéroch podnikov priority 1 z úlohy 083** (Matej: rozdeliť kvôli kreditom). Len prieskum, rovnaké pravidlá a metóda ako `083-venue-survey-v1-expansion.md` (prečítaj jej zadanie a report – body 1–14, Excel, fixtures do `tests/fixtures/survey2/`). Pipeline sa nespúšťa.

### Priorita 2 – plná hĺbka (body 1–14)
- **Twist Bar** – https://twistbar.co/music (v 008: program cez JavaScript, statické HTML prázdne). Zisti, či web nenačítava program z nejakého JSON/API (sieťové požiadavky stránky, napr. Playwright `page.on('response')`, alebo zdroj JS) – ak áno, je to „rýchle“. Inak odhadni, čo by stálo vykresľovanie prehliadačom v GitHub Actions (čas behu, závislosti). Matej: „chcem, ale nie cez mŕtvoly“. Neimplementuj.
- **Kino Aero** – kinoaero.cz (v 008 JSON-LD, 32 akcií/týždeň). Zmeraj: koľko premietaní denne a za 180 dní, koľko unikátnych filmov, či sa dajú rozlíšiť špeciálne akcie (premiéry, diskusie, festivaly, koncerty) od bežných premietaní. Matej sa bojí zahltenia – rozhodne podľa čísel. V Exceli hárok **Kino Aero** – premietania za deň.

### Priorita 3 – skrátene (len body 1, 2, 6, 7, 8, 11, 12; bez detailov akcií a bez fixtures)
Rock Café, Jazz Dock, Reduta Jazz Club, ~~Café V Lese, Klub 007 Strahov~~, Ankali, Mecca, Malostranská beseda, Chapeau Rouge, Vagon. (**Café V Lese a 007 Strahov presunuté do úlohy 088** – Matej 2026-11-22.)

### Priorita 4 – len zistiť (body 1, 2, 7, 8)
Rudolfinum, Obecní dům – Smetanova síň (klasická hudba – Matej rozhodne, či do appky patrí).

## Report
- Tabuľka a Excel `docs/tasks/084/venue-survey-p2-p4.xlsx` v rovnakom formáte ako 083 (hárok Podniky + Kino Aero).
- Odporúčané poradie pridávania v dávkach, riziká, nový typ zdroja (prehliadač pre Twist) len popísať s odhadom nákladov.
