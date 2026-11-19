# 079: Onboarding, preferencie, nové Pre teba, Akcie ako prvá záložka

## Zadanie

**Schválené Matejom 2026-11-19 13:50–14:44.** Mení len appku (`web/`) → **pipeline nespúšťaj**, over len nasadenie `deploy-app` (`CLAUDE.md`). Čo nie je jasné alebo sa nedá spraviť podľa `design.md`, spýtaj sa (nevymýšľaj UI).

**Čítaj:** `docs/design.md` časť 1 (farby, lišta, **nový riadok o poradí záložiek**), časť 4 (lišta Akcií, čip Pre teba, **blok „Zmena 2026-11-19 … nové pravidlo Pre teba“**), časť 7b (Filter, karta typov), **časť 7c (celá – onboarding)**; `web/src/core/search.ts` (`isForYou`), `web/src/core/filter.ts` (`filterTypeOf`, `umbrellasOf`, `eventUmbrellas`, podtypy kultúry – `grep -n "CULTURE_SUBTYPES\|subtype"`), `web/src/core/store.ts` (kľúče lokálneho úložiska), `web/src/components/BottomNav.tsx`, `web/src/App.tsx` (predvolená záložka), `web/src/pages/MyAccountPage.tsx`, `web/src/i18n/*.ts` (texty karty typov z 077/078). Ostatné len podľa potreby (`grep -n`).

### 1. Preferencie a nové pravidlo Pre teba
- Preferencie v lokálnom úložisku cez `store.ts` (nový kľúč, napr. `preferences`: typy, podtypy kultúry, žánre). **Obľúbené miesta ostávajú v doterajšom `favorites`** (srdiečko v onboardingu = to isté srdiečko ako v appke).
- `isForYou` podľa `design.md` 4 (blok 2026-11-19):
  - vybraté typy existujú a typ akcie (`filterTypeOf`) medzi nimi nie je → **nie**;
  - koncert/DJ/párty → obľúbené miesto **alebo** zastrešujúci žáner akcie (`eventUmbrellas`) medzi obľúbenými žánrami;
  - kultúra → podtyp akcie medzi vybratými podtypmi; kultúra vybratá bez podtypu → kultúrna akcia v obľúbenom mieste;
  - **bez vybratých typov** (preskočené) → obľúbené miesto alebo zhoda žánru, akýkoľvek typ (pre doterajších používateľov = správanie ako dnes);
  - žiadne preferencie → nič.
- Všade, kde sa `isForYou` používa (odznak na obrázku, čip Pre teba, počet „· 3 pre teba“, panel na mape), rovnaké pravidlo. Testy na všetky vetvy (aj workshop v obľúbenom mieste bez kultúry → nie; DJ + techno v neobľúbenom mieste → áno; len typy bez miest a žánrov → nič z hudby).

### 2. Onboarding (`design.md` 7c)
- Zobrazí sa **len pri novej inštalácii**: žiadny príznak dokončenia a zároveň žiadny z doterajších kľúčov stavu (`favorites`, `going`, `filter`, `eventsPeriod`, `eventsFilters`, `language`…). Existujúci používateľ (Matej) ho neuvidí. Po dokončení alebo preskočení sa uloží príznak; viac sa neukáže. Testovací prepínač `?dbg=onboarding` ho ukáže vždy (ako `?dbg=update`).
- Kroky: uvítanie → miesta → typy → žánre (len pri vybratom koncerte/DJ/párty) → koniec → **Akcie, obdobie Dnes**.
- Ikony typov skutočné (`typeIconSvg`), zoznam miest ako riadky v Miestach (kompaktnejšie, ~40 px; obrázok miesta, ak ho má), hľadanie bez diakritiky ako v Miestach. Tlačidlá na konci = **skutočné komponenty** čipu Pre teba a tlačidla Filtra (len zobrazenie, bez funkcie); ukážky zoznamov abstraktné (farebné riadky typov).
- Žánre: zastrešujúce hudobné žánre s aspoň jednou akciou v `events.json` (bez podtypov kultúry), podľa počtu akcií; limit 5.
- Animácie: rozbalenie kultúry ~250 ms, prechod krokov ~200 ms, `prefers-reduced-motion` bez animácií; nesmú spomaliť appku.

**Texty (presne):**
| Kde | sk | cs | en |
|---|---|---|---|
| Uvítanie nadpis | Kam dnes večer? | Kam dnes večer? | Where to tonight? |
| Uvítanie text | Vyber miesta, akcie a hudbu, ktoré ťa bavia. Akcie, ktoré by sa ti mohli páčiť, potom označíme ✦ | Vyber místa, akce a hudbu, které tě baví. Akce, které by se ti mohly líbit, pak označíme ✦ | Pick the places, events and music you're into. We'll then mark events you might like with ✦ |
| Tlačidlá | Začať · Ďalej · Preskočiť | Začít · Další · Přeskočit | Get started · Next · Skip |
| Miesta | Kam rád/a chodíš? / Vyber svoje obľúbené miesta. | Kam rád/a chodíš? / Vyber svá oblíbená místa. | What are your favourite places? / Pick your favourite places. |
| Typy | Čo ťa baví? / Môžeš vybrať viac možností. | Co tě baví? / Můžeš vybrat více možností. | What are you into? / You can pick more than one. |
| Žánre | Čo najradšej počúvaš? / Vyber najviac 5 možností. | Co nejradši posloucháš? / Vyber nejvýš 5 možností. | What are your favourite music genres? / Pick up to 5. |
| Koniec nadpis | Hotovo | Hotovo | All set |
| Koniec Pre teba | Akcie, ktoré by ťa mohli baviť, nájdeš pod ✦ Pre teba. | Akce, které by tě mohly bavit, najdeš pod ✦ Pro tebe. | You'll find events you might like under ✦ For you. |
| Koniec Filter | Vo Filtri si vyberieš len to, na čo máš chuť práve teraz. | Ve Filtru si vybereš jen to, na co máš chuť právě teď. | In Filter, you pick just what you're in the mood for right now. |
| Koniec účet | Svoj výber môžeš kedykoľvek zmeniť v Môj účet. | Svůj výběr můžeš kdykoli změnit v Můj účet. | You can change your picks anytime in My account. |
| Koniec tlačidlo | Ukáž mi akcie | Ukaž mi akce | Show me events |
| Potvrdenie preskočenia – nadpis | Preskočiť nastavenie? | Přeskočit nastavení? | Skip setup? |
| – text | Vďaka nemu ti označíme akcie, ktoré by ťa mohli baviť. | Díky němu ti označíme akce, které by tě mohly bavit. | It lets us mark events you might like. |
| – tlačidlá | Nastaviť (ružové) · Preskočiť | Nastavit · Přeskočit | Set up · Skip |
| Toast po preskočení | Nastaviť to môžeš kedykoľvek v Môj účet → Tvoje preferencie. | Nastavit to můžeš kdykoli v Můj účet → Tvoje preference. | You can set this up anytime in My account → Your preferences. |
| Môj účet riadok/nadpis | Tvoje preferencie | Tvoje preference | Your preferences |
| Pre teba bez preferencií | Nastav si, čo ťa baví, a označíme ti akcie ✦ · Nastaviť | Nastav si, co tě baví, a označíme ti akce ✦ · Nastavit | Set what you're into and we'll mark events for you ✦ · Set up |

### 3. Nový text DJ (karta typov vo Filtri **aj** onboarding; nahrádza text z 078)
| sk | cs | en |
|---|---|---|
| DJ púšťa a mixuje skladby. Patrí sem rave, techno, drum and bass nights, sound systems a podobne. | DJ pouští a mixuje skladby. Patří sem rave, techno, drum and bass nights, sound systems a podobně. | A DJ plays and mixes tracks. This includes raves, techno, drum and bass nights, sound systems and similar. |

Koncert, Párty, veta dole bez zmeny. V onboardingu sa veta dole ani zoznam podtypov kultúry ako text neukazujú (kultúra má rozbaľovacie čipy).

### 4. Môj účet → Tvoje preferencie, Pre teba bez preferencií
- Podľa `design.md` 7c. Zmena srdiečka v preferenciách = zmena obľúbených miest v celej appke.

### 5. Akcie ako prvá záložka
- Poradie v lište **Akcie, Mapa, Miesta, Môj účet**; appka sa pri spustení otvorí v Akciách (`design.md` 1). **Nič iné sa nesmie pokaziť:** odkazy na akcie a miesta, stav mapy pri prepínaní záložiek, pamätanie obdobia a filtra, ťuk na aktívnu záložku = navrch, tlačidlo Späť.
- Poloha: pri prvom otvorení mapy systémová žiadosť, ak ešte nebola povolená ani odmietnutá (ak to už tak funguje, bez zmeny).

## Overenie a report
- `npm test -- --reporter=dot` (testy `isForYou` všetkých vetiev, podmienka zobrazenia onboardingu, limit 5, poradie záložiek), `npm run build`; nasadenie `deploy-app` (číslo behu). Dáta sa nemenia, čísla z `events.json` netreba.
- Snímky JPEG 390 × 844 (Playwright z `tests/playwright/`, `?dbg=onboarding`) do `docs/tasks/079/`: `onb-1-welcome.jpg`, `onb-2-places.jpg` (2 srdiečka vybraté), `onb-3-types.jpg` (kultúra rozbalená, 2 podtypy), `onb-4-genres.jpg` (3/5), `onb-5-done.jpg`, `onb-skip-confirm.jpg`, `account-preferences.jpg`, `events-for-you.jpg` (Akcie po onboardingu so zapnutým Pre teba).
- V reporte: koľko akcií je pre teba pri preferenciách zo snímok (DJ + koncert, techno + drum-and-bass + punk, 2 miesta) vs. podľa starého pravidla (len 2 miesta) – výpočet z aktuálneho `events.json` lokálne, príkaz uveď.
