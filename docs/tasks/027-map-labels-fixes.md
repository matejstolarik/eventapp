# 027: Mená pod pinmi, nový vybraný pin, kompas, opravy po teste v telefóne

## Zadanie
Zadal: hlavný chat, 2026-11-10. Po úlohe 026.

Matej testoval 026 v telefóne. Šípky presúvajú mapu, čo je dobré. Zvyšok nižšie. Predloha je aktualizovaná: `docs/design.md` časť 2 (mená pod pinmi, vybraný pin = zväčšenie + žiara, animácie, kompas) a nové snímky **`01-mapa-piny-mena.png`**, **`02-mapa-vybrany-pin-ziara.png`** (+ HTML). Pilulka vybraného pinu z 026 sa ruší.

### 1. Chyby z testu
1. **Šípky ‹ › nemenia vybraný pin.** Mapa sa presunie, ale starý pin ostane vybraný a nový sa nevyberie. Šípka musí zmeniť výber rovnako ako ťuknutie (vrátane animácie).
2. **Vybraný pin musí byť vždy navrchu.** Dnes ho prekrýva susedný pin (Čitárna pod Archou+). Rieš `z-index` prvku značky MapLibre (rodič `.maplibregl-marker`), nie len vnútorného prvku.
3. **Animácia aj pri zrušení výberu** (zmenšenie, zmiznutie žiary), nielen pri výbere.
4. **Horná lišta je rozbitá.** Musí byť presne podľa predlohy (`design.md` časť 2, `01-mapa-piny-mena.png`):
   - mriežka na celú šírku, všetky prvky výška 44,
   - Dnes biele,
   - Všetko | Obľúbené v tmavom kontajneri `#23232F` s rovnako širokými polovicami,
   - Filter ružový kruh `#FF4D8D`.

   Filter zatiaľ nemá panel, ale musí vyzerať ako v predlohe (nie stlmený). Po ťuknutí ukáže krátku informáciu „Filter pripravujeme“.
5. **Ikony metra a budov chýbajú, namiesto nich sú len názvy budov.** Zobraz ikony zo sprite štýlu pre stanice metra, vlakové stanice, divadlá, múzeá a pamiatky (podľa `design.md`). Názvy budov bez ikony odstráň. Ak sprite potrebné ikony nemá, napíš ktoré a navrhni inú voľnú sadu (Maki, Temaki), neskladaj vlastné.

### 2. Mená pod pinmi a nový vybraný pin
- **Meno miesta pod každým pinom** od priblíženia ~13, štýl a priority podľa `design.md`. Pri kolízii mien sa skryje meno s nižšou prioritou, **pin nikdy**.
- **Vybraný pin:**
  - zväčší sa 1,22× od hrotu a dostane jemnú žiaru vo farbe typu,
  - meno je biele a tučné,
  - bez pilulky, bez bieleho obrysu, bez bodky,
  - presne podľa `02-mapa-vybrany-pin-ziara.html`.
- Animácie podľa `design.md` (220 ms oboma smermi, `prefers-reduced-motion`).

### 3. Kompas
Keď je mapa otočená (`bearing ≠ 0`), vpravo pod hornou lištou sa ukáže kompas podľa predlohy. Ťuk vráti mapu na sever (plynulo) a kompas zmizne.

### 4. Čo ostáva z 026
Ostáva:
- piny, odznaky, pulz,
- karta (len štítky akcie, šípky západ/východ, potiahnutie medzi akciami miesta),
- prvé ťuknutie necentruje,
- Späť zavrie kartu,
- mapa ovládateľná pri otvorenej karte,
- štýl mapy.

Nič z toho nesmie prestať fungovať.

### 5. Overenie
- **Pred pushom `npm run build`. Po pushi over úspešné nasadenie** (číslo behu do reportu).
- **Snímky 390 × 844, jazyk `sk`, reálne dáta** do `docs/tasks/027/`:
  - centrum s menami pod pinmi,
  - vybraný pin + karta,
  - stav **po stlačení ›** (iný pin vybraný, iná karta; musí sa líšiť od predošlej snímky),
  - ulica s ikonami metra a divadla/múzea,
  - otočená mapa s kompasom,
  - horná lišta zblízka vedľa výrezu z `01-mapa-piny-mena.png`.
- Test dotykov (`hasTouch`) a snímky animácie sú vítané. Ak ich nespravíš, napíš to rovno do „Otvorené“, bez výhovoriek.
- Report: tabuľka rozdielov oproti `01-mapa-piny-mena.png` a `02-mapa-vybrany-pin-ziara.png`.

## Report
