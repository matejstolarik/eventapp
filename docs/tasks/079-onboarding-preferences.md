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

## Report

**2026-11-19**, commit `50697f2` (appka, testy, Playwright skript, snímky, decisions), report v nasledujúcom commite. Mení len appku → pipeline sa nespúšťal. Nasadenie **Deploy web app #53** (run 44540332396): **success**, `50697f2`; na Pages je nový balík `assets/index-CNatd6u0.js` (obsahuje „Kam dnes večer“, `onboardingPending`, `preferencie`).

### Hotové
1. **Preferencie a nové pravidlo Pre teba.** Kľúč `preferences` v localStorage (`store.ts`: `{types, subtypes, genres}`, najviac 5 žánrov, neplatné hodnoty sa zahodia); obľúbené miesta ostávajú v `favorites` (srdiečko v onboardingu a v preferenciách volá to isté `toggleFavorite`). `isForYou(event, prefs)` v `core/search.ts` presne podľa design.md 4 (blok 2026-11-19): typ mimo vybratých → nie; hudba → obľúbené miesto alebo zastrešujúci žáner (`eventUmbrellas`); kultúra → podtyp medzi vybratými, bez podtypov → kultúra v obľúbenom mieste; bez typov → obľúbené miesto alebo žáner, akýkoľvek typ; bez preferencií → nič. Rovnaké pravidlo všade: odznak na obrázku a čip Pre teba v Akciách, počet „· N pre teba“, „Najbližšie“ pri prázdnom filtri, panel akcie na mape (`useForYouPrefs` – zmena srdiečka alebo preferencií sa prejaví hneď aj v otvorených Akciách).
2. **Onboarding** (`pages/OnboardingPage.tsx`, výbery v `components/PrefPickers.tsx`): uvítanie (4 kruhy s ikonami typov `typeIconSvg`) → miesta (bodky postupu, Preskočiť, biele hľadanie bez diakritiky, riadky 44 px s obrázkom miesta a srdiečkom) → typy (karty s vysvetlením, kultúra bez textu sa rozbalí na čipy podtypov 250 ms) → žánre (len pri koncerte/DJ/párty; „n/5“ sivé/ružové; po 5 ostatné stlmené) → koniec (skutočný `ForYouChip` a `FilterButton` bez funkcie, abstraktné riadky typov) → Akcie, obdobie Dnes. Prechod krokov 200 ms do strany, `prefers-reduced-motion` bez animácií; onboarding je jediné, čo sa počas neho vykresľuje (mapa a Akcie sa pripoja až po ňom). Späť = predošlý krok, na uvítaní potvrdenie preskočenia; Preskočiť v krokoch 2–4 bez otázky; po potvrdení preskočenia toast (ťuk → Tvoje preferencie). Zobrazí sa len pri novej inštalácii (žiadny `onboardingDone` a žiadny z kľúčov `favorites`, `going`, `filter`, `eventsPeriod`, `eventsFilters`, `language`, `eventsLastFetched`, `preferences`), `?dbg=onboarding` vždy. Texty presne podľa zadania (sk, cs, en).
3. **Nový text DJ** v `filter.typeHelp.dj` (sk, cs, en) – karta typov vo Filtri aj onboarding.
4. **Môj účet → Tvoje preferencie** (riadok hore na Môj účet, prekryv `#/preferencie`): miesta, typy s kultúrou, žánre pod sebou, ukladá sa hneď. **Pre teba bez preferencií:** čip sa nezapne, nad lištou karta `#2A2838` s textom a ružovým „Nastaviť“ → Tvoje preferencie.
5. **Akcie prvá záložka:** lišta Akcie, Mapa, Miesta, Môj účet (`TAB_ORDER`), štart v Akciách (prázdny hash), mapa `#/mapa`. Odkazy `#/akcia/…`, `#/miesto/…`, `#/akcie`, `#/miesta`, `#/ucet` fungujú ako doteraz; mapa ostáva po prvom otvorení pripojená (stav pri prepínaní záložiek), ťuk na aktívnu záložku = navrch, filter a obdobie sa pamätajú ako doteraz. **Poloha:** doteraz sa systémová žiadosť pri štarte nepýtala (len tlačidlom), preto doplnené: pri prvom otvorení mapy, ak je povolenie v stave `prompt`.

### Rozhodnutia (samostatne, zapísané v `docs/decisions.md`)
- Routing: prázdny hash = Akcie, mapa `#/mapa`, starý `#/` teraz otvorí Akcie; preferencie ako prekryv s vlastným hashom (systémové Späť funguje).
- `onboardingPending`: appka pri prvom spustení hneď zapíše `filter` a `eventsLastFetched`; bez tohto príznaku by sa onboarding po zavretí appky uprostred už neukázal.
- Vypnutie kultúry zmaže vybraté podtypy (zbalia sa).
- Vybratý čip podtypu a žánru = ružový (7c: ružová na výber).
- V Tvoje preferencie sa žánre ukazujú aj bez vybratých typov (pravidlo bez typov žáner berie) – inak by si doterajší používateľ bez typov nemohol pridať žánre.
- Uložené zapnuté Pre teba bez preferencií sa vypne; starý prázdny stav „Pridaj si obľúbené miesta…“ sa ruší (nahradila ho karta Nastaviť).
- Toast po preskočení 5 s; karta Pre teba má aj krížik ako karta aktualizácie.
- Poloha po povolení presunie mapu len do 2 km od aktívneho miesta (rovnaké pravidlo ako doteraz pri povolenej polohe).

### Overenie
- `npm test -- --reporter=dot` (z `web/`): **16 súborov, 261 testov passed** – `isForYou` všetky vetvy (workshop v obľúbenom mieste bez kultúry → nie; DJ + techno v neobľúbenom mieste → áno; len typy bez miest a žánrov → nič z hudby; kultúra s podtypmi/bez; bez typov; bez preferencií), podmienka onboardingu (nová inštalácia, `onboardingDone`, každý doterajší kľúč, nedokončený), limit 5 žánrov, poradie záložiek, routing (`parseHash`, `tabOfRoute`). `npm run build` OK.
- Playwright `tests/playwright/screenshots-079.spec.ts` (z `web/` s `NODE_PATH=web/node_modules`, dáta z Pages, čas 19. 11. 19:00): **3 passed** – celý onboarding až po Akcie (aktívna záložka Akcie), preskočenie s potvrdením a toastom, nová inštalácia onboarding ukáže / používateľ s `favorites` nie.
- Snímky v `docs/tasks/079/`: `onb-1-welcome.jpg`, `onb-2-places.jpg` (2 srdiečka: Bike Jesus, Čitárna Unijazz), `onb-3-types.jpg` (koncert, DJ, kultúra + film, talk), `onb-4-genres.jpg` (techno, drum-and-bass, punk = 3/5), `onb-5-done.jpg`, `onb-skip-confirm.jpg`, `account-preferences.jpg`, `events-for-you.jpg`. Uložené preferencie zo snímok: `docs/tasks/079/prefs.json`.

### Čísla Pre teba (lokálne, `events.json` z Pages `generated_at` 2026-11-19T14:26:10, 371 akcií)
Príkaz (z `web/`): `npx vite-node scripts/for-you-count.ts <events.json> bike-jesus,citarna-unijazz dj,concert "" techno,drum-and-bass,punk [2026-11-19]`

| Preferencie | Všetky akcie: nové / staré pravidlo | Dnes 19. 11. (11 akcií): nové / staré |
|---|---|---|
| DJ + koncert, techno + drum-and-bass + punk, 2 miesta (zadanie) | **91 / 42** | **3 / 2** |
| ako na snímkach (+ kultúra s film, talk) | **111 / 42** | **5 / 2** |

Staré pravidlo = len 2 obľúbené miesta.

### Otvorené
- Snímky som podľa pravidiel neprezeral – posúdenie vzhľadu (najmä obrazovka Hotovo s abstraktnými ukážkami a uvítanie) je na Matejovi.
- Ako sa správa systémová žiadosť o polohu na skutočnom telefóne (PWA), som neoveroval; v Playwright sa poloha nepýta.
