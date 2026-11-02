# 002: Opravy Čitárne, polia sold_out a room, adaptér Akropolis

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02. Začni až po dokončení úlohy 001.

### Opravy z kontroly events.json (commit c792dfd)
1. HTML entity v názvoch: „Polanský &amp; Langman“. Dekóduj entity (`html.unescape`) v normalizácii pre všetky zdroje. Test.
2. Čitárna má v programe oznamy „pro veřejnost ZAVŘENO“ (2026-11-07, 2026-11-27). Nie sú to akcie: vyraď ich v adaptéri Čitárne a zaloguj, čo si vyradil. Pravidlo a dôvod daj do komentára adaptéra.
3. Test `test_citarna_detail_date_conflict_flag`: neplatný dátum `2026-11-99` netestuje konflikt. Použi dva platné rozdielne dátumy (výpis 2026-11-05, detail 2026-11-06).
4. Čitárna `max_requests` zvýš na 60 (dnes 22, v rušnom mesiaci by 30 nestačilo).

### Zmeny dátového modelu (odsúhlasené 2026-10-31, zapíš do docs/data-model.md a docs/decisions.md)
- `sold_out`: `true` len ak zdroj výslovne uvádza vypredané, `false` len ak výslovne ponúka lístky, inak `null`. Nie je to `status`.
- `room`: nepovinné, sála alebo priestor v rámci podniku tak, ako ho uvádza zdroj (Akropolis: Velký sál, Malá scéna, Jazz bar), inak `null`.
- Dátum bez roka: dátum pred včerajškom patrí do budúceho roka. Len pre zdroje bez roka, pravidlo v komentári adaptéra. Ak by padol za +180 dní, akcia sa nezaradí.
- Oznamy, ktoré nie sú akcie (napr. „ZAVŘENO“), sa vyraďujú v adaptéri daného podniku a logujú (Kontroly kvality).

### Nový zdroj: Palác Akropolis, typ `html` s vlastným parserom
Program: https://palacakropolis.cz/work/33298?genre=0&gsicon=0&no=62&page_id=33521
Výpis má 6 strán. Akcia má dátum bez roka („31. 10.“), čas začiatku, sálu, farebnú kategóriu (modrá = hudba, červená = divadlo, zelená = off program), odkaz na detail a „Kup teď!“ alebo „Vyprodáno!“.
1. Pozri HTML výpisu: ako je zapísaná kategória (trieda, nie farba), odkaz na detail, odkaz na lístky, stránkovanie. Over, či stránka nemá JSON-LD alebo RSS. Ak áno, zastav sa a napíš to do reportu ako otázku.
2. Kategóriu daj do `sources[].section` (`hudba` / `divadlo` / `off-program`) ako pri MeetFactory. Sálu do `room`.
3. `ticket_url` len ak „Kup teď!“ vedie na predaj lístkov, nie na detail akcie.
4. Pridaj Akropolis do `venues.json` (IG `palacakropolis`, FB `Palac.Akropolis.klub`, `ra_url` https://ra.co/clubs/306167; adresu a súradnice vezmi z webu podniku, štítky nechaj prázdne, doplní Matej).
5. Fixtures, testy (aj prechod december → január pri roku), pipeline, `status.md`, commit, bežný push.

Do reportu navyše: počet akcií podľa sekcie a podľa `room`, počet `sold_out` true/false/null, 3 akcie Akropolisu porovnané s webom (URL, dátum, čas, sála).

## Report
