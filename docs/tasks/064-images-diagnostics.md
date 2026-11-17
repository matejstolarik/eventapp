# 064: Obrázky akcií – diagnostika (chýbajúce, rozlíšenie, orez) + psytrance/reggaeton

## Zadanie

**Schválené Matejom 2026-11-17.** Matej: obrázky sú základ appky, dnes (1) často chýbajú, (2) sú orezané tak, že nemajú výpovednú hodnotu (napr. Xzibit – vidno len rameno), (3) v detaile majú nízke rozlíšenie. **Táto úloha len meria a pripravuje podklad, appku ani dáta v `events.json` nemení** (okrem časti 4). Zmena zobrazenia príde po Matejovom posúdení a návrhu.

Príčiny z kódu (hlavný chat):
- `pipeline/thumbs.py`: náhľad akcie = štvorec zo stredu (`crop` + `resize` na 240 px). Políčko mriežky má ~120 CSS px, pri DPR ~3 treba ~360 px.
- `web/src/pages/EventPage.tsx`: detail ukazuje `image_url` v štvorci s `objectFit: cover` (tiež orez).
- Hypotéza (neistá): niektoré adaptéry berú malý obrázok zo zoznamu programu (`html_forum_karlin.py`, `html_archa.py`), hoci stránka akcie má väčší (`og:image`, `srcset`). `html_roxy.py`, `html_epic.py`, `rss.py`, `api.py` dávajú v zozname `image_url=None` – over, či sa doplní z detailu.

**Čítaj:** `pipeline/thumbs.py`, adaptéry s `image_url` (`grep -n image_url pipeline/adapters/*.py`), `docs/design.md` 1 a časti o mriežke Akcií a stránke akcie (len na pochopenie, nemeniť).

### 1. Chýbajúce a malé obrázky (po podnikoch)
- Z `events.json` posledného behu: na podnik počet akcií, bez obrázka, a rozlíšenie `image_url` (šírka × výška: medián, min; koľko pod 600 px na kratšej strane).
- Pre každý podnik otvor 2–3 stránky akcií (ohľaduplne, cache) a zisti, či je k dispozícii väčší obrázok (`og:image`, `srcset`, odkaz na plnú veľkosť) a pri akciách bez obrázka, či ho stránka akcie má. Tabuľka: podnik · odkiaľ berieme dnes · čo je k dispozícii · navrhovaná zmena. Nič neimplementuj.
- Bike Jesus: len konštatovať (program je na Facebooku).

### 2. Porovnanie orezov (kontaktný hárok)
- Pre všetky obrázky akcií v `events.json` vytvor 4 varianty štvorca 360 px:
  1. **dnes:** stred;
  2. **tváre:** detekcia tvárí (OpenCV, napr. YuNet alebo Haar – vyber a zdôvodni; závislosť len v skripte, nie v dennom behu). Štvorec okolo oblasti všetkých tvárí; ak sa nezmestí, okolo najväčších tvárí. Bez tváre: obrázok na výšku zhora, inak stred;
  3. **zhora:** na výšku zhora, inak stred (bez detekcie);
  4. **celý:** celý obrázok vycentrovaný na rozmazanom a stmavenom pozadí z neho samého.
- Výstup: **lokálna** HTML stránka `docs/tasks/064/sheet/index.html` (riadok = akcia: názov, podnik, pôvodný obrázok + rozmer + pomer strán, 4 varianty) s možnosťou pri každom riadku kliknúť, ktorý variant je najlepší, a export voľby do `docs/tasks/064/choices.json` (tlačidlo „Uložiť“ stiahne JSON; Matej ho vloží do repa).
- **Obrázky ani hárok s obrázkami necommituj** (cudzie autorské diela vo verejnom repe) – `docs/tasks/064/sheet/` daj do `.gitignore`. Commitni skript, ktorý hárok vytvorí (`scripts/review/crop-sheet.py`), a súhrn.
- Do reportu: počet obrázkov podľa pomeru strán (na výšku / štvorec / na šírku / banner ≥ 2 : 1), v koľkých detekcia našla tvár (1 / viac), koľko času detekcia trvá na obrázok.

### 3. Overenie zrušenia akcie (Forum Karlín)
- Pri prieskume AI (062) stránka Omah Lay (`forumkarlin.cz/udalost/omah-lay`, 18. 11.) ukazovala „ZRUŠENO“. `html_forum_karlin.py` má `status = "cancelled"` pri „ZRUŠENO“. Over v `events.json`, či má akcia `status: cancelled`, a v appke (Playwright, jedna snímka `docs/tasks/064/omah-lay.jpg`), ako sa zrušená akcia zobrazuje. Ak `status` nesedí, nájdi príčinu, neopravuj.

### 4. Drobnosť: psytrance a reggaeton samostatné žánre (Matej 2026-11-17)
- Zrušiť mapovanie `psytrance → trance` a `reggaeton → latin` v `data/genre_aliases.json`, pridať `psytrance` a `reggaeton` do zoznamu žánrov (`docs/data-model.md`) a kde treba (preklady žánrov v appke). Pravopisné varianty (`psy trance`, `psychedelic trance` → `psytrance`). Platí od najbližšieho behu, bez prepočítania AI (ak sa mapovanie robí z uloženej surovej hodnoty, napíš to).

## Overenie a report
- `pytest -q`, `npm test`/`build` len ak sa menila appka (časť 4 preklady).
- Report: tabuľka z časti 1, súhrn z časti 2 (bez obrázkov), výsledok časti 3, príkaz na vytvorenie hárku, otvorené body. Matejovi napíš, ako hárok otvoriť.
