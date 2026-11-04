# 018: Vyhľadávanie na webe pre neisté akcie (vrstva 3)

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-04. Oddelené z úlohy 017 kvôli šetreniu kreditov. **Spustiť až keď o tom rozhodne Matej.** Predpoklad: úloha 017 hotová (AI funguje aj v CI).

Odsúhlasené Matejom 2026-11-04.

- Len pre akcie, kde vrstva 2 vrátila istotu pod prahom (konfigurácia, začni 0,6) alebo len `music`.
- Použi nástroj na vyhľadávanie na webe v Anthropic API (over v oficiálnej dokumentácii názov nástroja, cenu za vyhľadávanie a limity; uveď odkazy). Obmedz počet vyhľadávaní na akciu (napr. 2) a na beh (konfigurácia).
- **Cache podľa interpreta** (normalizované meno): výsledok (je to kapela / DJ / iné, žánre, zdrojová URL) sa uloží a pri ďalšej akcii toho istého interpreta sa nehľadá. Kde uložiť cache medzi behmi (repo nie, beh nič necommituje), navrhni a zdôvodni; napr. ako súčasť zverejnených dát na Pages.
- K výsledku ulož URL, z ktorej AI vychádzala, a zobraz ju v súbore na kontrolu.
- Výsledky len z pevných zoznamov formátov a žánrov.
- Matej: „hlavne nech sú dáta kvalitné“ – kvalita má prednosť pred cenou, ale s limitmi, aby chyba nemohla minúť veľa peňazí. Uveď skutočnú cenu.

### Report navyše
Commit práce, počet vyhľadávaní a skutočná cena, zoznam akcií, ktorým vyhľadávanie zmenilo formát (pred → po, zdrojová URL), nový `docs/review/classification-RRRR-MM-DD.md`.

## Report
