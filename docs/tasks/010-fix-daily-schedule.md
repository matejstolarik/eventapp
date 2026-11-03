# 010: Ranný beh sa nespustil

## Zadanie
Zadal: hlavný chat (Matej), 2026-11-03. Malá úloha, robí sa pred 008.

Plánovaný beh 2026-11-03 o 05:00 UTC (`cron: '0 5 * * *'`) sa nespustil vôbec. Workflow je `active`, v Actions je len ručný beh z 2026-11-02 (`workflow_dispatch`), žiadny beh s udalosťou `schedule` (overené cez GitHub API 2026-11-03 11:00 UTC).

1. Zisti v dokumentácii GitHubu, prečo sa plánovaný beh môže oneskoriť alebo vynechať (napr. vysoká záťaž na začiatku každej hodiny), a uveď citáciu a odkaz.
2. Presuň čas behu na minútu mimo celej hodiny, napr. `17 4 * * *` (05:17 v zime, 06:17 v lete pražského času). Ak dokumentácia odporúča niečo iné, použi to a zdôvodni.
3. Do súhrnu behu (job summary) a do logu pridaj, či ide o beh `schedule` alebo `workflow_dispatch`, a čas začiatku, aby sa dalo sledovať, či ranné behy chodia.
4. Do `docs/status.md` zapíš: ako overiť, že ranný beh prebehol (kde v GitHube), a že prvé plánované behy po zmene treba sledovať pár dní.
5. Ručný beh nespúšťaj, chceme vidieť, či zajtra príde plánovaný.

## Report

Dátum: 2026-11-03.

### Príčina oneskoreného/vynechaného behu

GitHub dokumentácia ([Events that trigger workflows — schedule](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule)):

> "The `schedule` event can be delayed during periods of high loads of GitHub Actions workflow runs. High load times include the start of every hour. If the load is sufficiently high enough, some queued jobs may be dropped. To decrease the chance of delay, schedule your workflow to run at a different time of the hour."

Cron `0 5 * * *` (presne na :00) je preto nevhodný — GitHub ho spúšťa s oneskorením alebo preskočí.

### Čo bolo urobené

1. **Cron zmenený** z `0 5 * * *` na `17 4 * * *` (04:17 UTC = 05:17 CET / 06:17 CEST) — mimo najzaťaženejšej minúty :00.
2. **Nový krok `Log run metadata`** pridaný na začiatok workflow (pred checkout):
   - Vypíše do **job summary** (`$GITHUB_STEP_SUMMARY`): trigger (`schedule`/`workflow_dispatch`) a čas začiatku.
   - Vypíše rovnaké info aj do **logu** (stdout).
3. **`docs/status.md`** doplnený o sekciu „Ako overiť, že ranný beh prebehol" a upozornenie, že prvé behy po zmene treba sledovať 3 dni.
4. Ručný beh nespustený — čakáme na plánovaný beh zajtra (2026-11-04 ~04:17 UTC).

### Commit

`e29ed3a` — pushnutý na main 2026-11-03.
