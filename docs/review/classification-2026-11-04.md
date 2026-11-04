# AI Classification Review — 2026-11-04

Pipeline run: 2026-11-04. Commit s dátami: `00fed5c` (kód), dáta z lokálneho behu toho istého dňa.

## Súhrn

| Metrika | Hodnota |
|---|---|
| Celkový počet akcií | 298 |
| AI (llm) | 162 (54 %) |
| keyword | 58 (19 %) |
| source | 78 (26 %) |
| API volania | 9 |
| Vstupné tokeny | 25 408 |
| Výstupné tokeny | 6 088 |
| Odhadovaná cena | $0.0056 |
| Čas behu | ~2 min (Fuchs2 timeout pri 121 s) |

### Distribúcia istoty (AI akcie, n=162)

| Bucket | Počet |
|---|---|
| 0.9–1.0 | 33 (20 %) |
| 0.8–0.9 | 37 (23 %) |
| 0.7–0.8 | 30 (19 %) |
| 0.6–0.7 | 32 (20 %) |
| 0.5–0.6 | 12 (7 %) |
| < 0.5 | 18 (11 %) |

Nízka istota (< 0.6): **30 akcií** — pozri zoznam nižšie.

### Distribúcia formátov (všetky akcie)

| Formát | Počet |
|---|---|
| live | 160 |
| theatre | 60 |
| dj | 35 |
| music | 19 |
| dance | 9 |
| talk | 7 |
| other | 5 |
| workshop | 4 |
| opening | 2 |
| comedy | 1 |
| film | 1 |
| quiz | 1 |

### Akcie s nízkou istotou (< 0.6)

| Istota | Podnik | Názov | Formát | Žánre |
|---|---|---|---|---|
| 0.20 | fuchs2 | POSTPONED: deBasement | music | — |
| 0.20 | bike-jesus | Rikas | music | — |
| 0.20 | bike-jesus | Tonic Walter | music | — |
| 0.20 | bike-jesus | deary | music | — |
| 0.20 | bike-jesus | Iluka | music | — |
| 0.20 | bike-jesus | Dudlíkfest 2026 | music | — |
| 0.30 | bike-jesus | REVO: Z Gumy Do Gumy | music | — |
| 0.30 | bike-jesus | ACT OF THE BOUNCE | music | — |
| 0.30 | bike-jesus | REVO: Spirála | music | — |
| 0.30 | bike-jesus | FEVERDREAM | music | — |
| 0.30 | bike-jesus | SEBE + Pokoj25 | music | — |
| 0.40 | citarna-unijazz | Argo: Michal Vrba – Hlušický čtverec | live | — |
| 0.40 | citarna-unijazz | Vidět hutnou hudbu | film | experimental |
| 0.40 | citarna-unijazz | Text-appeal vol. 28 | theatre | — |
| 0.40 | archa-plus | LEAP | music | electronic |
| 0.40 | archa-plus | Health + VOWWS | music | electronic |
| 0.40 | forum-karlin | SLAVA VAKARCHUK IN PRAGUE | talk, live | — |
| 0.40 | forum-karlin | Stronger Together | other | — |
| 0.50 | cross-club | ARRAKIS FESTIVAL (×2) | music | — |
| 0.50 | cross-club | FESTIVAL NADPRAHOU PULMESIC & TECHNO STAGE… | music | — |
| 0.50 | meetfactory | Selection: Skeler + LXST CXNTURY + Æstral | music | electronic |
| 0.50 | meetfactory | Winter Prague Gothic Treffen | other | post-punk |
| 0.50 | fuchs2 | PŘESUNUTO DO MEETFACTORY / RFP CONCERTS… | live | post-punk |
| 0.50 | bike-jesus | REVO: SOUR ROOM | dj | techno |
| 0.50 | palac-akropolis | TROS SKETOS | live | — |
| 0.50 | archa-plus | KARAOKE+ | other | — |
| 0.50 | archa-plus | Festival Alternativa: Den 1. | music | experimental |
| 0.50 | archa-plus | Festival Alternativa: Den 2. | music | experimental |
| 0.50 | archa-plus | ROAST slaví narozky | live | — |

---

## Manuálna kontrola 20 akcií

Skontroloval som nasledovné akcie voči webu podniku alebo na základe zdravého rozumu. Výsledok: **4–5 chýb AI**, ostatné správne alebo akceptovateľné.

### ✓ Správne

1. **Citárna Unijazz — PSYTRANCE UNITED** → `dj`, `electronic` [0.70]  
   Psytrance akcia na noc, prichádzajúci DJs. Správne. Žáner `electronic` je ok (psytrance nie je v našom zozname).

2. **Cross Club — TECHNO STAGE** → `dj`, `techno` [0.70]  
   Cross Club techno stage = DJ sety. ✓

3. **MeetFactory — Fource: Nieve Ella** → `live`, `pop` [0.80]  
   Fource je hudobná séria MeetFactory. Nieve Ella je španielska speváčka (indie/pop). Správne.

4. **Forum Karlín — Fantastic Future Summit 2026** → `talk` [0.90]  
   Summit = konferencia. Správne.

5. **Citárna Unijazz — Svítit cestou - Motivační stand-up Světlany Nálepkové** → `comedy` [0.90]  
   "Stand-up" v názve. Správne.

6. **Fuchs2 — WRONG 10 YEARS presents Prison Religion ☆ Wick ☆ Zar** → `live`, `post-punk`, `ebm` [0.60]  
   Prison Religion je kapela (post-punk/EBM). ✓

7. **Archa+ — José González** → `live`, `indie` [0.90]  
   Španielsko-švédsky gitarista, koncert. ✓

8. **MeetFactory — Obscure: Archspire + Crown + The Zenith Passage** → `live`, `metal` [0.90]  
   Obscure je metalová séria MeetFactory. ✓

9. **Forum Karlín — The Pretty Reckless** → `live`, `rock`, `metal` [0.95]  
   Rocková kapela. ✓

10. **Bike Jesus — LYRA with FUNK D'VOID [Cocoon / Bedrock]** → `dj`, `techno`, `house` [0.80]  
    Funk D'Void je DJ na Cocoon/Bedrock labeli. ✓

### ✗ Chyby alebo nepresnosti

11. **Bike Jesus — REVO: Z Gumy Do Gumy** → `music` [0.30] — **Chyba**  
    REVO je klub s nočnými DJ setmi (techno/house scene). Správne by bolo `dj`. AI nepozná sériu REVO a dostala len záhadný názov.

12. **Bike Jesus — REVO: Spirála** → `music` [0.30] — **Chyba**  
    Rovnako ako REVO: Z Gumy Do Gumy — mal byť `dj`.

13. **Bike Jesus — ACT OF THE BOUNCE** → `music` [0.30] — **Pravdepodobná chyba**  
    "Bounce" naznačuje clubbing/DJ event. REVO-podobný kontext. Skôr `dj`.

14. **Forum Karlín — SLAVA VAKARCHUK IN PRAGUE** → `talk, live` [0.40] — **Chyba**  
    Slava Vakarchuk je spevák skupiny Okean Elzy (ukrajinskí rockeri). Toto je hudobný koncert, nie beseda. Správne by bolo len `live`. AI pravdepodobne zaradila `talk` pre kontext Ukrainy/vojny.

15. **MeetFactory — Selection: Skeler + LXST CXNTURY + Æstral + MRJay** → `music` [0.50] — **Chyba**  
    Selection je DJ séria MeetFactory. Skeler je bass music / drum-and-bass producent/DJ, ostatní tiež. Správne by bolo `dj` s žánrom `drum-and-bass` alebo `electronic`.

16. **Archa+ — LEAP** → `music`, `electronic` [0.40] — **Pravdepodobná chyba**  
    LEAP je tanečná inštalácia / hudobno-pohybová performance (sekcia `hudba` na Archa+, ale popis hovorí o tanci). Mohol by byť `dance`. AI má sekciu `hudba`, preto `music`.

17. **MeetFactory — Winter Prague Gothic Treffen** → `other`, `post-punk` [0.50] — **Nepresnosť**  
    Gothic Treffen je festival gotickej hudby s DJs a živými kapelami. Správne by bolo `dj` alebo `live`. AI nepozná formát a zvolila `other`.

### Zhrnutie chýb

| Typ chyby | Počet | Príklady |
|---|---|---|
| Neznáma séria / značka (REVO = DJ night) | 3+ | REVO: Z Gumy Do Gumy, Spirála, ACT OF THE BOUNCE |
| Zamiešanie talk + live | 1 | Slava Vakarchuk |
| DJ séria ako `music` | 1 | MeetFactory Selection |
| `other` namiesto `dj`/`live` | 1 | Gothic Treffen |
| Možný `dance` namiesto `music` | 1 | LEAP |

**Celkovo ~4–7 jasných chýb z 162 AI akcií (~3–4 %).** Väčšina chýb je pri neznámych lokálnych sériách (REVO, Selection, Gothic Treffen) alebo veľmi krátkych názvoch bez kontextu.

---

## Poznámky

- **Bike Jesus** má najviac nízko-istotných akcií (11/30). Príčina: Strapi API nedáva žánrovú sekciu, len dátum a názov. Názvy ako „deary", „Rikas", „Tonic Walter" (menej známi umelci) a „REVO: X" (séria bez popisu) nemajú pre AI žiadny kontext. Pomohlo by pridať `section` alebo popis do API adaptéra.
- **Cross Club festivaly** (ARRAKIS, FESTIVAL NADPRAHOU) majú 0.50 — multi-dňové festivaly s viacerými pódiami sú pre AI ťažké. Správny fallback je `music`.
- **Fuchs2 POSTPONED: deBasement** (0.20) — prefix „POSTPONED:" robí akciu neklasifikovateľnou. Mohlo by sa filtrovať v adaptéri.
- **Archa+ Festival Alternativa** (0.50) — viacdenný festival rôznych žánrov, `music` s `experimental` je rozumný fallback.
