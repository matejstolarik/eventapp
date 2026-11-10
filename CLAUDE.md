# CLAUDE.md

App that shows events (concerts, parties, culture) at the user's favourite venues in Prague. Personal project of Matej, built to be usable by others later.

## Before you start
- **Read only what the task needs** (credits are limited). The task file says which docs and sections to read. Do not read whole large docs by default:
  - `docs/decisions.md` (large, append-only): search it (`grep -n`) for the topic of the task and read only the matching rows. Read it whole only for changes to the pipeline architecture or data sources.
  - `docs/design.md`: read section 1 (general, colours) plus the sections named in the task.
  - `docs/data-model.md`: only when the task touches data fields.
  - `docs/project.md`: only for scope questions.
- In code, read the files and functions the task names; search (`grep -n`) before opening big files whole.
- Data structures are defined in `docs/data-model.md`. Follow it exactly; if you need to change it, propose the change first and update the doc.
- If a task would contradict a decision in `docs/decisions.md`, stop and say so instead of silently deviating.
- When a new decision is made while coding, add it to `docs/decisions.md` (date, decision, reason).

## Stack (v1)
- Pipeline: Python, run daily by GitHub Actions.
- Storage: static JSON (`events.json`) published to GitHub Pages. No database.
- Frontend: PWA in React (later, after the data pipeline works).
- Instagram is not a data source, only a link in the venue profile (`instagram` field = handle). Sources: RSS, schema.org Event (JSON-LD), HTML program pages.

## Collaboration rules
- **Decide independently.** Ask Matej only for: data model changes, contradictions with `docs/decisions.md`, new source types or changes to how data is fetched, git history rewriting or force push, paid services or new secrets (API keys).
- Other decisions: record them in `decisions.md` or `docs/status.md` and summarise in the closing report.
- Tasks are tracked in `docs/tasks/` — each task is a file `NNN-name.md`. Run `git pull` before starting a task.
- **At the end of every task**, write `## Report` in the task file with: date + commit hashes, what is done, decisions made independently and why, numbers (computed from `site/events.json` of the latest pipeline run — always include the command used), verification against the web (specific URLs and values), what remains open or was not finished. Commit and push the report together with the work. Write only: task number, done/not done, commit hash.
- **Do not report intermediate results as final.** Numbers and results in the closing report must come from `events.json` from the latest pipeline run.
- **`docs/` is the single source of truth** for all technical matters. `decisions.md` and `docs/tasks/` are append-only — old entries are never deleted or rewritten. A change to a decision = a new row that supersedes the old one.

## Rules
- Never invent data. If a source does not provide a value, leave it empty (`null`). Do not guess dates, times, prices or URLs.
- Dates and times are stored as Prague local time strings (`YYYY-MM-DD`, `HH:MM`), never converted through UTC.
- Each source is a separate adapter: `fetch(venue, source_config) -> list[RawEvent]`. Adapters do not deduplicate and do not touch other adapters.
- Data from sources is not trusted blindly: inconsistencies are flagged (see Quality checks in `docs/data-model.md`), not silently fixed.
- If sampling reveals that a venue's actual source type or fetch method differs from the plan (e.g. planned JSON-LD but the site has no Event JSON-LD, or requires JS rendering), **stop and report** before implementing. Do not silently switch to a different source type or add new adapters without agreement.
- Be polite to websites: one request at a time per site, identify with a clear User-Agent, cache during development.
- Each source has a hard limit: max requests per run and a per-source wall-clock timeout. A slow or broken source must log a warning and let the pipeline continue — it must never block other sources.
- Never fetch data from Resident Advisor (ra.co). Only link to it via venue `ra_url`.
- Secrets (API keys) only via environment variables / GitHub Secrets, never in the repo.
- Code, comments, commit messages and docs inside code: English. Talk to Matej in Slovak.
- Keep it simple. This is a small personal project; prefer plain functions and standard libraries over frameworks.
- **UI design:** UI must follow `docs/design.md` and `docs/design/` almost 1:1. Do not invent UI behaviour, colours or layout. If something is missing or not feasible, stop and ask Matej.
- **Screenshots and browser (credits):**
  - Make screenshots only with a Playwright script run from the shell (reuse the existing scripts in `tests/playwright/`). Never use the session's interactive browser tools.
  - Take only the screenshots the task lists. Save them as JPEG (quality 80, 390 × 844 unless stated) into `docs/tasks/NNN/`.
  - Do not open/view the screenshots yourself to judge the design; the main chat and Matej review them. Check the script ran and the files exist. View an image only to debug a concrete failure, at most a few times per task.
  - If a screenshot cannot be made reliably after 2 attempts, stop trying, say so in the report and move on.
  - Do not paste long build/test logs into the context; use `--reporter=dot`/`-q` and look only at failures.
- **Never rewrite git history** (no `filter-branch`, `rebase -i`, `reset --hard` on pushed commits, or `push --force`) without explicit approval from Matej. To remove a file: `git rm` + normal commit is enough.

## Repository layout (proposal, adjust when scaffolding)
```
CLAUDE.md
docs/                 project.md, decisions.md, data-model.md
data/venues.json      venues, tags and sources (edited by hand)
pipeline/             Python package
  adapters/           one module per source type (rss, jsonld, html_*, ra)
  normalize.py
  dedup.py
  checks.py
  classify.py         later: LLM classification
  main.py             entry point: fetch -> normalize -> dedup -> checks -> write events.json
tests/                fixtures with saved HTML/RSS samples, tests per adapter
.github/workflows/    daily pipeline run
web/                  PWA (later)
```

## Commands

```bash
# Install dependencies (first time)
pip install -r requirements.txt

# Run the pipeline (fetches live RSS, writes site/events.json)
python -m pipeline.main

# Run tests
pytest
```
