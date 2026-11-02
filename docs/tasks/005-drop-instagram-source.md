# 005: Instagram vypustený ako zdroj dát

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02. Začni až po úlohe 004. Len dokumentácia a `venues.json`, žiadna zmena pipeline.

Rozhodnutie Mateja 2026-11-02: Instagram nebude zdrojom dát ani vo v2. Program berieme len z webov podnikov. Dôvod: Graph API je zložité na nastavenie (Meta developer účet, business účty podnikov, extrakcia z postov cez LLM) a takmer každý podnik má web s programom. Instagram ostáva len ako odkaz v profile podniku (rýchle overenie zmien na poslednú chvíľu). Pôvodný nápad sa nemaže, ostáva v backlogu ako zamietnutý nápad.

1. `docs/decisions.md`: nový riadok 2026-11-02, ktorý nahrádza riadky z 2026-10-29 o Instagrame vo v2 (pri nich dopíš „(nahradené 2026-11-02)“, nemaž ich).
2. `docs/project.md`: odstráň sľub „pokrytie malých podnikov len na Instagrame príde vo v2“ a „Instagram až vo v2“; v backlogu presuň Instagram do novej podsekcie „Zamietnuté nápady“ s dátumom a dôvodom. Podniky, ktoré program zverejňujú len na Instagrame, majú v appke profil bez akcií.
3. `docs/data-model.md`: „V2 pribudne `instagram`“ a „vrátane Instagramu vo v2“ nahraď všeobecnou vetou (nový typ zdroja = nový adaptér). Pole podniku `instagram` (handle) ostáva.
4. `CLAUDE.md`: „No Instagram in v1“ → Instagram nie je zdroj dát, len odkaz v profile podniku.
5. `data/venues.json`: doplň chýbajúce IG handle podľa auditu: MeetFactory `meetfactory`, Kasárna Karlín `kasarna_karlin`, Čitárna Unijazz `citarna_unijazz`. Nič iné nedomýšľaj.

## Report
