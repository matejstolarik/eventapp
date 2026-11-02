# 008: Prieskum webov zvyšných podnikov

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-02. Robí sa **pred úlohou 007**. Len prieskum: žiadne adaptéry, žiadna zmena `venues.json` ani pipeline. Spúšťať na normálnej sieti (Wi-Fi vo vlaku blokovala twistbar.co).

Cieľ: pre každý podnik zistiť, ako rýchlo a akým spôsobom ho vieme pridať. Od toho závisí, či LLM vôbec potrebujeme (úloha 007) a na ktorých weboch ho testovať.

### Podniky
Známy web z auditu (2026-10-29), nájdi stránku s programom:
- Twist: https://twistbar.co/music
- Forum Karlín: forumkarlin.cz
- Archa+: archa-plus.cz
- Jazz Republic: jazzrepublic.cz
- Futurum Music Bar: futurum.musicbar.cz
- Fuchs2: fuchs2.cz (v audite odkazuje na RA; RA nikdy nesťahuj, len zisti, či má program aj na vlastnom webe)
- Bike Jesus: bikejesus.com (rovnako ako Fuchs2)

Web neauditovaný, nájdi oficiálny web a stránku s programom; uveď, ako si overil, že ide o ten podnik (adresa, IG), a nič nedomýšľaj:
- Kino Aero, Strecha Radost (over presný názov), Kolektor, Acid Kafe, El Magico

### Pre každý podnik zisti
1. URL stránky s programom (ak existuje). Ak program na webe nie je (len IG/FB/RA), napíš to.
2. Štruktúrované zdroje: RSS/iCal, schema.org Event (JSON-LD), verejné API alebo JSON endpoint, ktorý web sám používa.
3. Ak nič štruktúrované: ako pravidelné je HTML (opakujúci sa blok na akciu, kde je dátum/čas/názov), či sa obsah renderuje cez JS (statické HTML prázdne?), stránkovanie.
4. Aké údaje sú k dispozícii: dátum (s rokom?), čas, názov, interpreti, cena, lístky, sekcia/žáner.
5. `robots.txt` pre URL programu.
6. Či web odpovedá nášmu `fetch.py` (User-Agent, bez prehliadača). Ak nie, prečo (HTTP kód, TLS chyba, ochrana typu Cloudflare).
7. Počet akcií v okne +180 dní (približne).
8. Odhad náročnosti: **rýchle** (štruktúrovaný zdroj), **parser** (pravidelné HTML), **ťažké** (nepravidelné HTML, JS, voľný text) alebo **bez zdroja**.

Ulož 1 vzorku HTML programu na podnik do `tests/fixtures/survey/` (poslúži pre adaptéry aj pre úlohu 007).

### Report navyše
- Tabuľka všetkých 12 podnikov s bodmi 1 až 8.
- Odporúčané poradie pridávania (najrýchlejšie najprv).
- Ktoré weby sú kandidáti na test LLM (kategória **ťažké**). Ak žiadne, napíš to.
- Podniky na potvrdenie Matejom (neauditované weby).

## Report
