# 061: Test DeepSeek ako náhrady Gemini/Claude (hľadanie + rozhodnutie + preklad)

## Zadanie

> **ZMENA 2026-11-17 večer (Matej, pred spustením) – platí pred všetkým nižšie.**
> - Kredit DeepSeek je **2 $** (nie ~5 $). Rozpočet v kóde: **zastaviť pri 1 $ za beh** (nahrádza 2 $), HTTP 402 → stop. Pred celým testom pusti 3 akcie a z nich odhadni cenu 50; ak odhad presahuje 1 $, zastav a napíš to.
> - Model `deepseek-flash`, endpoint Search/Fetch (`/v1/tools/search`) a ich parametre sú v zadaní z prieskumu hlavného chatu, nie overené v kóde. **Ak sa oficiálne docs DeepSeek (časť 1) líšia (iný názov modelu, endpoint, chýbajúci Fetch, iný spôsob hľadania), zastav po časti 1 a napíš rozdiely.** Neimprovizuj náhradu.

**Schválené Matejom 2026-11-17.** Gemini s Google hľadaním nesmieme použiť (podmienky, pozri hlavičku 060). DeepSeek: výstup patrí nám, podmienky API ukladanie výsledkov ani dávkový beh nezakazujú, publikovaný AI obsah treba označiť ako AI (Terms of Use). Tento test zistí, či DeepSeek dosiahne kvalitu Gemini D na Matejových 50 označených akciách. **Len test, nič do denného behu.**

**Predpoklad (Matej):** účet na `platform.deepseek.com`, predplatený kredit (~5 $), GitHub Secret `DEEPSEEK_API_KEY`. Bez kľúča zastav a napíš to.

**Čítaj:** `docs/ai-rules.md` (celé); report 058 (Časť 1) a 059 (tabuľka variantov, Časť 3); `pipeline/gemini_test.py` (testovací rámec, výber 50 akcií, Excel); `pipeline/enrich_ai.py` (`_Gemini2`, pravidlá v kóde – `apply_rules`); `pipeline/research_store.py`; `docs/tasks/056/labels-matej.csv`; oficiálne docs DeepSeek: `api-docs.deepseek.com/guides/search/`, `/quick_start/pricing`, `/guides/json_mode`, `/guides/tool_calls`.

Každá časť vlastný commit. Rozhodnutia do `docs/decisions.md`.

### 1. Overenie oficiálnych údajov (pred kódom)
- Z oficiálnych stránok DeepSeek do reportu (URL + citát): ceny `deepseek-flash` (vstup cache hit/miss, výstup), **kedy je špička a mimo špičky** (v pražskom čase), cena Search a Fetch, limity, či Search/Fetch API alebo podmienky (`cdn.deepseek.com/policies/…`) obmedzujú ukladanie výsledkov alebo vyžadujú citácie. Ak niečo nenájdeš, napíš „nenájdené“.

### 2. Provider `_DeepSeek` (variant A, celý DeepSeek)
- Model `deepseek-flash` s **tool calls**: nástroje `search(query)` a `fetch(url)` vykonáva náš kód cez `POST https://api.deepseek.com/v1/tools/search` a Fetch API (DeepSeek docs). Limit na akciu: najviac **3 hľadania + 2 načítania** (pri koncertoch/DJ). Do každého dotazu pridať `-site:ra.co -site:instagram.com`; výsledky z `ra.co` a `instagram.com` zahodiť aj v kóde. Facebook povolený.
- Postup a výstup podľa `docs/ai-rules.md` A–H (typ, `primary_format`, žánre s citátom z faktov, cena, čas, interpreti, popis CZ); **Spotify sa nehľadá** (G). Výstup JSON (JSON mode) v rovnakom tvare ako `_Gemini2`, aby išiel cez tie isté poistky (`apply_rules`: citát žánru, URL len z výsledkov, cena bez opory → prázdna, „Tba“ → prázdne).
- Preklad CZ → SK, EN: `deepseek-flash`, samostatné lacné volanie (alebo v tom istom, ak je lacnejšie – zdôvodni).
- Prieskum (fakty + URL) ukladať cez `research_store.py`, aby sa dal neskôr znova rozhodnúť bez hľadania.
- Rozpočet v kóde: zastaviť pri 2 $ za beh; HTTP 402 → stop. Zapisovať tokeny, hľadania, načítania a cenu na akciu.
- Ručný workflow `deepseek-test.yml` (`workflow_dispatch`), kľúč len z `secrets.DEEPSEEK_API_KEY`.

### 3. Test na 50 akciách
- Tie isté akcie ako v 058/059 (Matejove označenia). Výsledok do `docs/tasks/061/deepseek-test.xlsx` + `.json`: na akciu Matejove označenie, Gemini D (z `059/tune.json`), DeepSeek A; stĺpce typ (zhoda áno/nie), žánre, cena (+ overenie), čas, interpreti, popis CZ, zdroje (URL), hľadania, cena v $.
- Súhrn v reporte: typ správne X/50 (D mal 47/50), žánre (zhoda s Matejovým `expected` a s D), počet cien (a koľko overených otvorením stránky), počet akcií, kde hľadanie nenašlo nič relevantné, zahodené poistkami, **priemerná a celková cena na akciu**, odhad mesačne pri 280 a 1 300 nových akciách (špička vs. mimo špičky).
- 10 popisov CZ + ich SK/EN preklad vypíš do reportu na Matejovo posúdenie češtiny.
- Ručne over 5 akcií na webe (URL + čo tam je).

### Mimo rozsahu
- Variant B (hľadanie DeepSeek + rozhodnutie Gemini bez hľadania) – len ak to Matej po reporte schváli.
- Denný beh, `events.json`, appka (označenie „AI“ pri popise rozhodne Matej po teste).

## Overenie a report
- `pytest -q` OK (testy providera na uložených odpovediach, bez siete).
- Číslo behu workflow, príkaz na súhrn z `docs/tasks/061/deepseek-test.json`.
- Otvorené body a odporúčanie: A, B, alebo nepoužiť.

## Report

**Dátum:** 2026-11-17. **Stav: hotové (časti 1–3), čakám na rozhodnutie A / B / nepoužiť.** Denný beh sa nezmenil.

**Commity:** `506b319` (workflow), `8ba6f11` (časť 1), `4d7c4c7` (časť 2: provider, testy, skript), `13d157c` (časť 3: výsledky). Report a `decisions.md` sú v commite s týmto reportom.

**Behy workflow `deepseek-test.yml`:**
- docs: [44144771251](https://github.com/matejstolarik/eventapp/actions/runs/44144771251);
- skúška 3 akcií: [44146149119](https://github.com/matejstolarik/eventapp/actions/runs/44146149119);
- **test 50 akcií: [44146358954](https://github.com/matejstolarik/eventapp/actions/runs/44146358954)**;
- kontrola zostatku: [44147739673](https://github.com/matejstolarik/eventapp/actions/runs/44147739673).

### Časť 1 – oficiálne údaje
Celé s URL a citátmi je v [`061/official-docs.md`](061/official-docs.md). Zhrnutie:
- **Docs sa so zadaním zhodujú.** Model `deepseek-flash` existuje (overené cez GET `/models` s naším kľúčom). `POST /v1/tools/search` aj `POST /v1/tools/fetch` existujú. JSON mode aj tool calls sú podporené. Jediné spresnenie: dotaz pre Search má max. 128 znakov.
- **Ceny `deepseek-flash`** za 1M tokenov (mimo špičky / špička):
  - vstup cache hit: $0.003 / $0.006;
  - vstup cache miss: $0.15 / $0.30;
  - výstup: $0.60 / $1.20.
- Search aj Fetch stoja $0.75 za 1 000 úspešných požiadaviek. Prázdne výsledky a chyby sa neplatia.
- **Špička:** 01–04 a 06–10 UTC, po–pi. V pražskom čase je to v zime **02–05 a 07–11**, v lete 03–06 a 08–12. Víkendy a čínske sviatky sú mimo špičky. Denný beh (`cron 17 4 * * *` = 04:17 UTC) beží **mimo špičky**.
- **Limity:** Search 100 QPS, Fetch 25 QPS (plus limit na doménu), súbežnosť 2 500.
- **Podmienky:**
  - obmedzenie ukladania výsledkov Search/Fetch: **nenájdené**;
  - povinná citácia zdrojov: **nenájdené**;
  - výstup treba označiť ako AI („You shall clearly disclose to your end users that the Output content is generated by AI“).
- Z lokálneho počítača sú domény DeepSeek nedostupné, preto sa docs sťahujú v GitHub Actions.

### Časť 2 – provider `_DeepSeek` (`pipeline/deepseek.py`)
- **Tri kroky ako `_Gemini2`**, všetko `deepseek-flash` bez premýšľania:
  1. prieskum: tool calls `search` / `fetch` vykonáva náš kód;
  2. rozhodnutie v JSON mode z faktov, číslovaných zdrojov a textu stránky podniku;
  3. preklad CZ → SK, EN samostatným volaním.
- **Limity v kóde:**
  - max. 3 hľadania + 2 načítania na akciu; ďalšie volanie dostane odpoveď „limit reached“;
  - každý dotaz má `-site:ra.co -site:instagram.com`, výsledky z ra.co a instagram.com sa zahadzujú a také URL sa nenačítajú;
  - Facebook je povolený;
  - Spotify sa nehľadá a každý Spotify odkaz od modelu sa zahodí.
- **Poistky:** výstup ide cez `process_result`, teda tie isté ako pri Gemini (URL len zo zdrojov, overenie ceny GET-om, popis bez výkričníkov a reklamy, `party` len s dôvodom…).
  - **Funkcia `apply_rules` zo zadania v kóde neexistuje.**
  - Žáner bez citátu kód nezahadzuje (ani pri Gemini), preto ho meria test (nižšie).
- **Rozpočet:** beh sa zastaví pri 1 $ (`DEEPSEEK_BUDGET_USD`) a pri HTTP 401/402. Pri každej akcii sa ukladajú tokeny, hľadania, načítania a cena (aj cena v špičke a mimo nej).
- **Prieskum** sa ukladá cez `research_store.record_from` do [`061/research/2026-11.json`](061/research/2026-11.json).
- **Preklad zvlášť:** rozhodnutie tak má rovnaký prompt ako Gemini D (len CZ). Spojené volanie by ušetrilo len ~$0.0001 na akciu.
- `pytest -q`: **358 passed**, z toho 8 nových v `tests/test_deepseek.py` (bez siete).

### Časť 3 – test na 50 akciách
Výsledky:
- [`061/deepseek-test.xlsx`](061/deepseek-test.xlsx): hárok Akcie (Matej, Gemini D, DeepSeek A) a hárok Súhrn;
- `061/deepseek-test.json`.

Príkaz na súhrn: `python -m pipeline.deepseek_test xlsx docs/tasks/061/deepseek-test.json docs/tasks/061/deepseek-test.xlsx` (alebo `summary docs/tasks/061/deepseek-test.json`).

**Skúška 3 akcií:** $0.016. Odhad pre 50 akcií je $0.27 (v špičke $0.38), teda pod 1 $, preto som test pustil.

| | DeepSeek A | Gemini D (059) |
|---|---|---|
| typ správne | **47/50** | 46/50 (pozn. 1) |
| nepodložené žánre (ručne posúdené) | 13 | 7 |
| ceny od AI (nie z webu podniku) | 8, z toho 6 overených GET-om | 4 |
| čas začiatku | 47/50 | – |
| popis CZ | 48/50 | 48/50 |
| bez hľadania / nič relevantné | 0 / 0 | – |
| na kontrolu (`needs_review`) | 9 | – |
| zahodené poistkami | 9 | – |
| hľadania / načítania na akciu | 2,54 / 1,12 | 2,58 / – |
| $ na akciu | **0.0051** mimo špičky (pozn. 2), 0.0075 v špičke | 0.0043 (od 2027 0.0062) |
| spolu za 50 akcií | **$0.255** | – |
| mesačne pri 280 akciách | **$1.43** mimo špičky / $2.08 v špičke | $1.22 (od 2027 $1.74) |
| mesačne pri 1 300 akciách | **$6.62** mimo špičky / $9.68 v špičke | $5.65 (od 2027 $8.06) |

1. Zadanie uvádza pri D 47/50, ale to je výsledok 058. Podľa `059/tune.json` má D 46/50.
2. Test bežal mimo špičky.

**Tokeny a kredit:**
- vstup ~19 900 tokenov na akciu (54 % z cache), výstup ~1 560;
- zostatok účtu klesol z 2,00 na **1,76 $**. Vypočítaná cena skúšky a testu je $0.271, výpočet je teda skôr horný odhad.

**Chyby typu A:**
- REEAL TIME 3 → `other` (Matej: `performance`);
- REVO → `music` (nič nenašiel, pravidlo H);
- Tinlicker → `dj` (Roxy píše „DJ SETEM“, otvorené od 059).
- Oproti D opravil Asta Hiroki (`concert`).

**Žánre:**
- Matejove označenia (`labels-matej.csv`) žánre nemajú, preto sa zhoda s Matejom **nedá zmerať**.
- Zhoda s D: rovnaké poradie 18/50, rovnaká množina 20/50, rovnaký hlavný žáner 40/50.

**Nepodložené žánre A (13):**
- Amphibian `ambient` (len „atmosférické poslúchanie“ rádia);
- Warhaus `indie` + `electronic` (fakt: alternative pop, rytmy Gqom);
- Text-appeal `experimental` (fakt sám hovorí, že nejde o jeden žáner);
- Žižkovská benefice `experimental` (fakt: noise rock);
- Student Wednesday `electronic` (fakt: EDM, pridaný nadradený žáner);
- Almost Weekend `electronic`;
- SLVL `hardcore` (fakt: hard techno, pravidlo C6);
- Video Oldies `pop`;
- Omah Lay `pop`;
- High Speed Fairytales `electronic`;
- Keo `indie` (fakt: alt-rock);
- Allt `death-metal` (stránka: death-core).

Ostatné žánre majú citát, v ktorom je názov žánru.

**Zahodené poistkami (9):**
- 3× `party` bez dôvodu: Psytrance United, SLVL, Tinlicker;
- 3× cena nie je na stránke: Bonobo 1 190, Family Therapy 400, Xzibit 55 €;
- 1× cena bez platného zdroja: Keo;
- 2× popis s výkričníkom: Modeselektor LIVE a FIRE!. Pri FIRE! je výkričník v názve kapely, ide teda o **falošné zahodenie**.

**Popisy:**
- často majú 5–6 viet a sú dlhšie ako pri Gemini;
- niektoré obsahujú miesto („Koncert se koná ve Velkém sále…“, „v Čítárně Unijazz“), čo je proti pravidlu F;
- slovenský preklad pri Amphibian zmenil rod (CZ „producent… který“ → SK „producentka… ktorá“).

#### 10 popisov na posúdenie (CZ / SK / EN)

**José González**
- CZ: José González je švédský zpěvák a kytarista s argentinskými kořeny, narozený v roce 1978 v Göteborgu, známý také jako člen skupiny Junip. Na scénu vstoupil v roce 2003 albem Veneer a písní Heartbeats, po němž následovala alba In Our Nature, Vestiges & Claws a Local Valley. Jeho rukopis stojí na akustické kytaře, fingerpickingu klasické kytary a klidném, soustředěném vokálu s vlivem latinskoamerických rytmů. Do Prahy přiveze také album Against The Dying Of The Light, které vychází 27. března 2026 u labelu City Slang a které sám popisuje jako reakci na obavy o budoucnost světa a povzbuzení k růstu i plnění si snů. Koncert se koná ve Velkém sále ve stoje, pořadatelem je D Smack U Promotion.
- SK: José González je švédsky spevák a gitarista s argentínskymi koreňmi, narodený v roku 1978 v Göteborgu, známy aj ako člen skupiny Junip. Na scénu vstúpil v roku 2003 albumom Veneer a piesňou Heartbeats, po ktorom nasledovali albumy In Our Nature, Vestiges & Claws a Local Valley. Jeho rukopis stojí na akustickej gitare, fingerpickingu klasickej gitary a pokojnom, sústredenom vokále s vplyvom latinskoamerických rytmov. Do Prahy prinesie aj album Against The Dying Of The Light, ktorý vychádza 27. marca 2026 u labelu City Slang a ktorý sám opisuje ako reakciu na obavy o budúcnosť sveta a povzbudenie k rastu aj plneniu si snov. Koncert sa koná vo Veľkej sále na stojato, organizátorom je D Smack U Promotion.
- EN: José González is a Swedish singer and guitarist with Argentine roots, born in 1978 in Gothenburg, also known as a member of the band Junip. He entered the scene in 2003 with the album Veneer and the song Heartbeats, followed by the albums In Our Nature, Vestiges & Claws and Local Valley. His signature style is based on acoustic guitar, classical guitar fingerpicking and a calm, focused vocal with the influence of Latin American rhythms. To Prague he will also bring the album Against The Dying Of The Light, which is released on 27 March 2026 on the City Slang label and which he himself describes as a reaction to concerns about the future of the world and an encouragement to grow and fulfil one's dreams. The concert takes place in the Great Hall standing, the organiser is D Smack U Promotion.

**Pragokoncert: Allt + Avralize + Bite Down**
- CZ: Švédská kapela Allt z Karlskogy vznikla v roce 2020 a hraje progresivní metalcore, v němž se temné, zamyšlené zvukové krajiny a melodie potkávají s drtivým zvukem. Debutové album From The New World vyšlo v roce 2024 a tematicky vychází z prostředí města postaveného na zbrojním průmyslu, odkud kapela pochází; letos následovalo druhé album Ataraxia. Kapela je známá propracovaným audiovizuálním vyprávěním příběhů. Jako speciální hosté turné vystoupí němečtí moderní metalcore Avralize z Rottweilu, kteří se prosadili debutem Freaks z roku 2024 a letos vydali album Liminal, a švédští Bite Down s intenzivní metalcore show a albem Violent Playground.
- SK: Švédska kapela Allt z Karlskogy vznikla v roku 2020 a hrá progresívny metalcore, v ktorom sa temné, zamyslené zvukové krajiny a melódie stretávajú s drvivým zvukom. Debutový album From The New World vyšiel v roku 2024 a tematicky vychádza z prostredia mesta postaveného na zbrojnom priemysle, odkiaľ kapela pochádza; tento rok nasledoval druhý album Ataraxia. Kapela je známa prepracovaným audiovizuálnym rozprávaním príbehov. Ako špeciálni hostia turné vystúpia nemeckí moderní metalcore Avralize z Rottweilu, ktorí sa presadili debutom Freaks z roku 2024 a tento rok vydali album Liminal, a švédski Bite Down s intenzívnou metalcore show a albumom Violent Playground.
- EN: The Swedish band Allt from Karlskoga was formed in 2020 and plays progressive metalcore, in which dark, contemplative soundscapes and melodies meet a crushing sound. The debut album From The New World was released in 2024 and thematically draws from the environment of a city built on the arms industry, where the band comes from; this year it was followed by the second album Ataraxia. The band is known for elaborate audiovisual storytelling. As special guests of the tour, German modern metalcore Avralize from Rottweil, who broke through with the debut Freaks from 2024 and released the album Liminal this year, and Swedish Bite Down with an intense metalcore show and the album Violent Playground will perform.

**BONOBO**
- CZ: Bonobo je projekt britského producenta, skladatele a hudebníka Simona Greena, který začínal v Brightonu a od přelomového alba Animal Magic (2000) patří mezi nejvýraznější postavy elektronické scény. Na svých deskách propojuje elektroniku s downtempem, housem, UK garage a vlivy jazzu, folku a soulu, přičemž do nahrávek zve hosty napříč žánry – objevili se na nich Erykah Badu, Fink, Chet Faker nebo Jordan Rakei. Proslul především koncerty s celou živou kapelou, s níž vystupoval na Coachelle, Glastonbury i v londýnské Royal Albert Hall. Do Prahy přijíždí v rámci turné Distance in Static s novým albem, které vyjde 11. září u Ninja Tune a vznikalo mimo jiné ve studiu Neila Younga.
- SK: Bonobo je projekt britského producenta, skladateľa a hudobníka Simona Greena, ktorý začínal v Brightone a od prelomového albumu Animal Magic (2000) patrí medzi najvýraznejšie postavy elektronickej scény. Na svojich doskách prepája elektroniku s downtempom, housom, UK garage a vplyvmi jazzu, folku a soulu, pričom do nahrávok pozýva hostí naprieč žánrami – objavili sa na nich Erykah Badu, Fink, Chet Faker alebo Jordan Rakei. Preslávil sa predovšetkým koncertmi s celou živou kapelou, s ktorou vystupoval na Coachelle, Glastonbury i v londýnskej Royal Albert Hall. Do Prahy prichádza v rámci turné Distance in Static s novým albumom, ktorý vyjde 11. septembra u Ninja Tune a vznikal okrem iného v štúdiu Neila Younga.
- EN: Bonobo is the project of British producer, composer and musician Simon Green, who started out in Brighton and since the breakthrough album Animal Magic (2000) has been one of the most distinctive figures of the electronic scene. On his records he connects electronics with downtempo, house, UK garage and influences of jazz, folk and soul, while inviting guests across genres to the recordings – Erykah Badu, Fink, Chet Faker or Jordan Rakei have appeared on them. He is known primarily for concerts with a full live band, with which he performed at Coachella, Glastonbury and the Royal Albert Hall in London. He is coming to Prague as part of the Distance in Static tour with a new album, which will be released on 11 September on Ninja Tune and was created among other places in Neil Young's studio.

**Warhaus**
- CZ: Warhaus je sólový projekt belgického hudebníka Maartena Devolderea, známého jako člena kapely Balthazar, s níž získal dvě ocenění Music Industry Awards za nejlepší album. Pod vlastním jménem si vybudoval svébytný popový svět a v roce 2017 obdržel MIA v kategorii Best Alternative, o tři roky později byl oceněn jako nejlepší autor a skladatel. Dosud vydal alba We Fucked a Flame Into Being, Warhaus, Ha Ha Heartbreak a Karaoke Moon, s nímž v roce 2024 vyprodal velký sál ARCHY+. Pátá deska The Donkey, jejíž vydání je ohlášeno na leden 2027, přináší hypnotické texty, syrové vokály, rytmy inspirované jihoafrickým žánrem Gqom a svižné groovy protkané grimeovými prvky. Vedle nových skladeb včetně singlu The Baby zazní v Praze i písně, které se za léta koncertování staly součástí repertoáru, například Love's a Stranger.
- SK: Warhaus je sólový projekt belgického hudobníka Maartena Devolderea, známeho ako člena kapely Balthazar, s ktorou získal dve ocenenia Music Industry Awards za najlepší album. Pod vlastným menom si vybudoval svojbytný popový svet a v roku 2017 obdržal MIA v kategórii Best Alternative, o tri roky neskôr bol ocenený ako najlepší autor a skladateľ. Doteraz vydal albumy We Fucked a Flame Into Being, Warhaus, Ha Ha Heartbreak a Karaoke Moon, s ktorým v roku 2024 vypredal veľkú sálu ARCHY+. Piata doska The Donkey, ktorej vydanie je ohlásené na január 2027, prináša hypnotické texty, surové vokály, rytmy inšpirované juhoafrickým žánrom Gqom a svižné groovy pretkané grimeovými prvkami. Popri nových skladbách vrátane singla The Baby zaznejú v Prahe aj piesne, ktoré sa za roky koncertovania stali súčasťou repertoáru, napríklad Love's a Stranger.
- EN: Warhaus is the solo project of Belgian musician Maarten Devoldere, known as a member of the band Balthazar, with which he won two Music Industry Awards for best album. Under his own name he has built a distinctive pop world and in 2017 received a MIA in the Best Alternative category, three years later he was awarded as best author and songwriter. So far he has released the albums We Fucked a Flame Into Being, Warhaus, Ha Ha Heartbreak and Karaoke Moon, with which he sold out the large hall of ARCHY+ in 2024. The fifth record The Donkey, whose release is announced for January 2027, brings hypnotic lyrics, raw vocals, rhythms inspired by the South African genre Gqom and brisk grooves interwoven with grime elements. Alongside new songs including the single The Baby, songs that have become part of the repertoire over years of touring will also be heard in Prague, for example Love's a Stranger.

**TINLICKER**
- CZ: Tinlicker je nizozemský projekt z Utrechtu, který v roce 2013 založili Jordi van Achthoven a Micha Heyboer; spojili precizní houseovou produkci s hlubokou zvukovou paletou. Mezinárodní průlom jim přinesl hit „Because You Move Me“, po němž opustili vydavatelství Anjunadeep a přešli pod [PIAS]. Místo klasických DJ setů začali vystupovat jako živá kapela, což definovalo album Cold Enough For Snow (2024) nahrané s Metropole Orkest, které balancuje mezi melodickým housem, indie-elektronikou a klubovým technem. V roce 2025 se k Miche a Jordimu připojila Hero Baldwin a Tinlicker se etablovali jako trio. Do Roxy se vracejí s DJ setem, na kterém je doplní Lumiere, VIIITO a John Sarkander, v místnosti ROOM8 pak Mini S, Amarettina a StreetKid.
- SK: Tinlicker je holandský projekt z Utrechtu, ktorý v roku 2013 založili Jordi van Achthoven a Micha Heyboer; spojili precíznu houseovú produkciu s hlbokou zvukovou paletou. Medzinárodný prielom im priniesol hit „Because You Move Me“, po ktorom opustili vydavateľstvo Anjunadeep a prešli pod [PIAS]. Namiesto klasických DJ setov začali vystupovať ako živá kapela, čo definovalo album Cold Enough For Snow (2024) nahratý s Metropole Orkest, ktorý balansuje medzi melodickým housom, indie-elektronikou a klubovým technom. V roku 2025 sa k Miche a Jordimu pripojila Hero Baldwin a Tinlicker sa etablovali ako trio. Do Roxy sa vracajú s DJ setom, na ktorom ich doplnia Lumiere, VIIITO a John Sarkander, v miestnosti ROOM8 potom Mini S, Amarettina a StreetKid.
- EN: Tinlicker is a Dutch project from Utrecht, founded in 2013 by Jordi van Achthoven and Micha Heyboer; they combined precise house production with a deep sound palette. Their international breakthrough came with the hit "Because You Move Me", after which they left the Anjunadeep label and moved to [PIAS]. Instead of classic DJ sets, they began performing as a live band, which defined the album Cold Enough For Snow (2024) recorded with Metropole Orkest, balancing between melodic house, indie-electronica and club techno. In 2025, Hero Baldwin joined Micha and Jordi and Tinlicker established themselves as a trio. They return to Roxy with a DJ set, where they will be joined by Lumiere, VIIITO and John Sarkander, and in the ROOM8 room by Mini S, Amarettina and StreetKid.

**Text-appeal vol. 28**
- CZ: Text-appeal je pravidelný autorský večer studentů, učitelů a absolventů oboru Tvorba textu a scénáře Konzervatoře a VOŠ Jaroslava Ježka v Praze. Program nabízí písně, poezii, prózu i čtené scénáře, které doplňují hosté a příznivci oboru. Jde o 28. díl série, konkrétní účinkující pro tento večer nejsou zveřejněni. Akce se koná v Čítárně Unijazz na Žižkově.
- SK: Text-appeal je pravidelný autorský večer študentov, učiteľov a absolventov odboru Tvorba textu a scenára Konzervatória a VOŠ Jaroslava Ježka v Prahe. Program ponúka piesne, poéziu, prózu aj čítané scenáre, ktoré dopĺňajú hostia a priaznivci odboru. Ide o 28. diel série, konkrétni účinkujúci pre tento večer nie sú zverejnení. Akcia sa koná v Čitárni Unijazz na Žižkove.
- EN: Text-appeal is a regular author evening of students, teachers and graduates of the Text and Screenwriting programme at the Jaroslav Ježek Conservatory and Higher Vocational School in Prague. The programme offers songs, poetry, prose and read screenplays, complemented by guests and supporters of the programme. It is the 28th instalment of the series; the specific performers for this evening have not been announced. The event takes place in the Unijazz Reading Room in Žižkov.

**DRUMSTATION**
- CZ: Drum & bassová noc DRUMSTATION probíhá na hlavní i dolní stage Cross Clubu a potrvá až do sedmi ráno. Hlavní hvězdou je britský producent a DJ Sub Zero, původem z Newcastlu a usazený v Leicesteru, který dříve tvořil duo G Dub a vydává na labelech Ganja, Playaz a Crucast; z jeho diskografie pochází například Spin Doc, The Collab EP nebo letošní Pulse EP. Vedle něj vystoupí pražská drum & bassová producentka a DJ Magenta, známá releasy na Low Down Deep a BassLayerz. Program doplní Critical J, Upfockerz, Prase, N.E.D., Jimmy Cocaine, Mr Be, Lesi, Zakilo, Wetbandits, Kroom, Brejchus Pavián, Baddabap a MC Jelen. Druhá scéna patří projektu PSYCHOSOUND s techno-house-acid-breaks live sety.
- SK: Drum & bassová noc DRUMSTATION prebieha na hlavnej aj dolnej stage Cross Clubu a potrvá až do siedmej ráno. Hlavnou hviezdou je britský producent a DJ Sub Zero, pôvodom z Newcastlu a usadený v Leicesteri, ktorý predtým tvoril duo G Dub a vydáva na labeloch Ganja, Playaz a Crucast; z jeho diskografie pochádza napríklad Spin Doc, The Collab EP alebo tohtoročný Pulse EP. Vedľa neho vystúpi pražská drum & bassová producentka a DJ Magenta, známa releasmi na Low Down Deep a BassLayerz. Program doplní Critical J, Upfockerz, Prase, N.E.D., Jimmy Cocaine, Mr Be, Lesi, Zakilo, Wetbandits, Kroom, Brejchus Pavián, Baddabap a MC Jelen. Druhá scéna patrí projektu PSYCHOSOUND s techno-house-acid-breaks live setmi.
- EN: The drum & bass night DRUMSTATION takes place on the main and lower stage of Cross Club and lasts until seven in the morning. The main star is British producer and DJ Sub Zero, originally from Newcastle and based in Leicester, who previously formed the duo G Dub and releases on the labels Ganja, Playaz and Crucast; his discography includes Spin Doc, The Collab EP and this year's Pulse EP. Alongside him will perform Prague drum & bass producer and DJ Magenta, known for releases on Low Down Deep and BassLayerz. The programme will be completed by Critical J, Upfockerz, Prase, N.E.D., Jimmy Cocaine, Mr Be, Lesi, Zakilo, Wetbandits, Kroom, Brejchus Pavián, Baddabap and MC Jelen. The second stage belongs to the project PSYCHOSOUND with techno-house-acid-breaks live sets.

**Omah Lay**
- CZ: Omah Lay, vlastním jménem Stanley Omah Didia, pochází z nigerijského Port Harcourtu a od vstupu na scénu v roce 2020 se stal jednou z nejvýraznějších tváří afrobeatu. Jeho diskografie zahrnuje EP Get Layd a What Have We Done a debutové album Boy Alone, z něhož pocházejí hity Bad Influence, Godly, Soso, Reason a Holy Ghost. V roce 2025 vydal album Clarity of Mind a za skladbu s Davido získal nominaci na Grammy 2026 v kategorii Nejlepší africký hudební výkon. Spolupracoval s Olamidem, Davido, Tylou, Ninhem, Ozunou i Justinem Bieberem a celosvětově prodal přes 10 milionů desek. V pražském Foru Karlín vystoupí poprvé, a to s plnohodnotnou živou kapelou, bohatými aranžmá a vizuální produkcí.
- SK: Omah Lay, vlastným menom Stanley Omah Didia, pochádza z nigérijského Port Harcourtu a od vstupu na scénu v roku 2020 sa stal jednou z najvýraznejších tvárí afrobeatu. Jeho diskografia zahŕňa EP Get Layd a What Have We Done a debutový album Boy Alone, z ktorého pochádzajú hity Bad Influence, Godly, Soso, Reason a Holy Ghost. V roku 2025 vydal album Clarity of Mind a za skladbu s Davido získal nomináciu na Grammy 2026 v kategórii Najlepší africký hudobný výkon. Spolupracoval s Olamidem, Davido, Tylou, Ninhem, Ozunou i Justinom Bieberom a celosvetovo predal viac ako 10 miliónov platní. V pražskom Foru Karlín vystúpi prvýkrát, a to s plnohodnotnou živou kapelou, bohatými aranžmánmi a vizuálnou produkciou.
- EN: Omah Lay, whose real name is Stanley Omah Didia, comes from the Nigerian city of Port Harcourt and since entering the scene in 2020 has become one of the most distinctive faces of afrobeats. His discography includes the EPs Get Layd and What Have We Done and the debut album Boy Alone, from which the hits Bad Influence, Godly, Soso, Reason and Holy Ghost come. In 2025 he released the album Clarity of Mind and for a song with Davido he received a Grammy 2026 nomination in the Best African Music Performance category. He has collaborated with Olamide, Davido, Tyla, Ninho, Ozuna and Justin Bieber and has sold over 10 million records worldwide. He will perform at Prague's Forum Karlín for the first time, with a full live band, rich arrangements and visual production.

**Keo (UK)**
- CZ: Londýnská čtveřice Keo vznikla v roce 2020 z bratrů Keoghových a tvoří ji Finn Keogh (zpěv), Conor Keogh (baskytara), Oli Spackman (bicí) a Jimmy Lanwern (kytara). Kapela na sebe upozornila debutovým singlem Echo On (2023) a EP Siren (2025), na kterém frontman Finn během necelých dvaceti minut vypovídá o svých prohřešcích, zklamáních i touhách. Zvuk postavený na kytarových riffech doplňuje jeho zpěv a v baladách kapela umí ubrat na tempu, aniž by ztratila intenzitu. Debutové album Put A Smile On For Me vyšlo v roce 2026 u Island Records a v britské hitparádě dosáhlo druhého místa. Do Kasáren Karlín se Keo vracejí po premiéře na Rock for People 2026, tentokrát s tímto albem.
- SK: Londýnska štvorica Keo vznikla v roku 2020 z bratov Keoghovcov a tvoria ju Finn Keogh (spev), Conor Keogh (basgitara), Oli Spackman (bicie) a Jimmy Lanwern (gitara). Kapela na seba upozornila debutovým singlom Echo On (2023) a EP Siren (2025), na ktorom frontman Finn za necelých dvadsať minút vypovedá o svojich prehreškoch, sklamaniach aj túžbach. Zvuk postavený na gitarových riffoch dopĺňa jeho spev a v baladách kapela vie ubrať na tempe bez toho, aby stratila intenzitu. Debutový album Put A Smile On For Me vyšiel v roku 2026 u Island Records a v britskom rebríčku dosiahol druhé miesto. Do Kasární Karlín sa Keo vracajú po premiére na Rock for People 2026, tentoraz s týmto albumom.
- EN: The London quartet Keo was formed in 2020 by the Keogh brothers and consists of Finn Keogh (vocals), Conor Keogh (bass guitar), Oli Spackman (drums) and Jimmy Lanwern (guitar). The band drew attention with their debut single Echo On (2023) and the EP Siren (2025), on which frontman Finn recounts his transgressions, disappointments and desires in under twenty minutes. The sound built on guitar riffs is complemented by his vocals, and in ballads the band can slow the tempo without losing intensity. The debut album Put A Smile On For Me was released in 2026 on Island Records and reached second place in the British chart. Keo return to Kasárna Karlín after their premiere at Rock for People 2026, this time with this album.

**Amphibian Quadrophonic Soundsystem**
- CZ: Pražský label Amphibian pořádá v ARŠE+ už třetí edici noci Quadrophonic Soundsystem, která představuje současnou elektronickou hudbu na čtyřkanálovém zvuku. Ze zahraničí přijede berlínský producent a zvukový designér A Strange Wedding, který se věnuje experimentální bass music, psychedelickému a deep technu, dubu i trancu a vydal desky Meta Romance a The Null Zone, a z Velké Británie Carrier, který tvaruje podobu dnešního IDM. Z domácích live aktů vystoupí DDAT z Amphibian s novým live setem, Natálie Pleváková ze Sanatorium Sonorum a HRTL s modulárními syntezátory. DJskou část obstará slovenská dvojice Madeleine v b2b s Ninou Farrinou a ranní closing odehraje Aplus Plusplus. Součástí večera je i live radio stage Radia Labe s pořady Ajran, Brightside, Margi a On the Road, zaměřená na klidné, atmosférické poslouchání; noc zahájí RUCH se svým synth jamem a live performance show Here Be Dragons.
- SK: Pražský label Amphibian organizuje v ARŠE+ už tretiu edíciu noci Quadrophonic Soundsystem, ktorá predstavuje súčasnú elektronickú hudbu na štvorkanálovom zvuku. Zo zahraničia príde berlínska producentka a zvuková dizajnérka A Strange Wedding, ktorá sa venuje experimentálnej bass music, psychedelickému a deep technu, dubu aj trancu a vydala albumy Meta Romance a The Null Zone, a z Veľkej Británie Carrier, ktorý formuje podobu dnešného IDM. Z domácich live aktov vystúpi DDAT z Amphibian s novým live setom, Natálie Pleváková zo Sanatorium Sonorum a HRTL s modulárnymi syntetizátormi. DJskú časť zabezpečí slovenská dvojica Madeleine v b2b s Ninou Farrinou a ranný closing odohrá Aplus Plusplus. Súčasťou večera je aj live radio stage Radia Labe s reláciami Ajran, Brightside, Margi a On the Road, zameraná na pokojné, atmosférické počúvanie; noc začne RUCH so svojím synth jamom a live performance show Here Be Dragons.
- EN: The Prague label Amphibian is holding the third edition of the Quadrophonic Soundsystem night at ARŠE+, which presents contemporary electronic music in four-channel sound. From abroad, Berlin producer and sound designer A Strange Wedding will come, who works on experimental bass music, psychedelic and deep techno, dub and trance and has released the albums Meta Romance and The Null Zone, and from Great Britain Carrier, who shapes the form of today's IDM. From domestic live acts, DDAT from Amphibian will perform with a new live set, Natálie Pleváková from Sanatorium Sonorum and HRTL with modular synthesizers. The DJ part will be provided by the Slovak duo Madeleine in b2b with Nina Farrina and the morning closing will be played by Aplus Plusplus. Part of the evening is also a live radio stage of Radio Labe with the shows Ajran, Brightside, Margi and On the Road, focused on calm, atmospheric listening; the night will be opened by RUCH with their synth jam and live performance show Here Be Dragons.

#### Ručné overenie 5 akcií na webe (2026-11-17)
1. **Warhaus** – https://archa-plus.cz/cz/program/detail/898/2027-03-17-warhaus-1
   - na stránke: „St 17 03, 20:00“ a „Vstupenky za 990 Kč včetně poplatků“;
   - A: 20:00, 990 Kč, overená – **správne**.
2. **Allt + Avralize + Bite Down** – https://meetfactory.cz/cs/program/detail/pragokoncert-allt-avralize-bite-down
   - na stránke: „19. 11. 20:00“, „Švédská death-core banda ALLT“, „od 950 Kč“;
   - A: 20:00 správne; cenu má už web podniku; žáner `death-metal` je odvodený z „death-core“, teda nepodložený.
3. **Tinlicker** – https://www.roxy.cz/events/detail/5077/tinlicker
   - na stránke: „So 21/11/2026 23:00“, „Early Birds 750 Kč“, nadpis „TINLICKER OVLÁDNOU ROXY SVÝM DJ SETEM“, v texte, že namiesto DJ setov vystupujú ako živá kapela;
   - A: 23:00 správne; typ `dj` podľa nadpisu (Matej: `concert`).
4. **Bonobo** – https://www.forumkarlin.cz/udalost/bonobo
   - na stránke: „17. 3. 2027 st 20:00“, len odkazy na Ticketmaster, cena nie je uvedená;
   - A: 20:00 správne; cenu 1 190 CZK so zdrojom na tejto stránke poistka zahodila – **správne**; popis „s celou kapelou“ zodpovedá textu stránky.
5. **Stahlzeit** – https://www.forumkarlin.cz/udalost/stahlzeit
   - na stránke: „21. 11. 2026 so 20:00“, cena nie je uvedená;
   - A: 20:00 správne; cenu 1 290 Kč z https://rezervace.ticketportal.cz/event/STAHLZEIT pipeline overila GET-om (stránku Ticketportal som ručne neotváral).

### Rozhodnutia urobené samostatne (v `decisions.md`)
- Docs DeepSeek sa sťahujú v GitHub Actions, lebo lokálne sú nedostupné.
- Štruktúra providera: 3 kroky, bez premýšľania, preklad zvlášť.
- Limity výsledkov: Search 6 výsledkov (len summary), Fetch orezaný na 6 000 znakov.
- Cena sa počíta podľa času volania; ukladá sa cena v špičke aj mimo nej.
- Prieskum testu je uložený v `docs/tasks/061/research/`, nie v `site/`.

### Otvorené a odporúčanie
**Odporúčanie: A je použiteľný, ak Matej akceptuje slabšie žánre.**
- **Za A:**
  - typ je najlepší z lacných variantov: 47/50, D má 46/50;
  - našiel 2× viac cien ako D (8 vs. 4, z toho 6 overených);
  - stojí $0.0051 na akciu mimo špičky a denný beh je mimo špičky. To je o ~18 % viac ako D dnes, ale menej ako D od 1. 1. 2027 ($0.0062).
- **Proti A:**
  - **13 nepodložených žánrov** (D má 7), hlavne pridané nadradené žánre (`electronic`, `pop`, `indie`);
  - dlhé popisy, niektoré s miestom.
- Pred nasadením treba sprísniť prompt pre žánre a popis a znova zmerať (~$0.25).

Ďalšie otvorené body:
- **B** (hľadanie DeepSeek + rozhodnutie Gemini bez hľadania) som netestoval, čaká na schválenie.
- Poistka na výkričník zahodí popis, keď je „!“ v názve interpreta (FIRE!). Oprava patrí do `description_problems` v dennom behu; nerobil som ju.
- Tinlicker: štítok `concert` vs. „DJ SETEM“ na stránke Roxy (otvorené od 059).
- Označenie „AI“ pri popise v appke: podmienky DeepSeek ho vyžadujú, rozhodne Matej.
- Zostatok kreditu: 1,76 $.
