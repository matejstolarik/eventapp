# 030: Mená dvojice pinov tesne pri sebe

## Zadanie
Zadal: hlavný chat, 2026-11-10. Po úlohe 029.

Matej: pri priblížení, keď sa ukážu mená, sa pri Fuchs2 a Bike Jesus ukáže len „Bike Jesus“, „Fuchs2“ zmizne (kolízia mien). Takto to riešiť nemôžeme. Malá úloha, nič iné nemeň.

### Úloha
Pravidlo je v `docs/design.md` (časť 2, „Miesta tesne pri sebe“):
- dvojica pinov, ktoré `checkPinOverlaps()` rozostúpi (alebo sú bližšie ako ~40 px), **sa navzájom neskrýva mená**,
- meno západného pinu sa zarovná doprava, končí pod jeho pinom a text ide na západ,
- meno východného pinu sa zarovná doľava, začína pod jeho pinom a text ide na východ,
- ak sa ani tak nezmestia (prekrývali by sa), zobraz jedno spoločné meno „Bike Jesus · Fuchs2“ (západ · východ) vycentrované pod dvojicou,
- vybraný pin z dvojice má meno biele a tučné ako inde; pri spoločnom mene je tučná len jeho časť,
- kolízie s ostatnými menami podľa doterajších priorít, dvojica sa berie ako jeden celok,
- prepočet po `zoomend`/`moveend` ako doteraz.

### Overenie
- `npm test`, `npm run build`, úspešné nasadenie (číslo behu).
- Hlavný chat spustil denný beh 2026-11-10 (`42840975398`), takže Fuchs2 a Bike Jesus majú v `events.json` rôzne súradnice. Over to v reporte zo zverejneného súboru.
- Snímky 390 × 844, `sk`, do `docs/tasks/030/`:
  - dvojica pri priblížení ~14 (mená vedľa seba),
  - pri ~13 (spoločné meno, ak nastane),
  - pri ~16,
  - s vybraným Fuchs2.

## Report
