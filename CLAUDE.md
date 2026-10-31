# CLAUDE.md

App that shows events (concerts, parties, culture) at the user's favourite venues in Prague. Personal project of Matej, built to be usable by others later.

## Before you start
- Read `docs/project.md` (goal, scope) and `docs/decisions.md` (agreed decisions) before any larger change.
- Data structures are defined in `docs/data-model.md`. Follow it exactly; if you need to change it, propose the change first and update the doc.
- If a task would contradict a decision in `docs/decisions.md`, stop and say so instead of silently deviating.
- When a new decision is made while coding, add it to `docs/decisions.md` (date, decision, reason).

## Stack (v1)
- Pipeline: Python, run daily by GitHub Actions.
- Storage: static JSON (`events.json`) published to GitHub Pages. No database.
- Frontend: PWA in React (later, after the data pipeline works).
- No Instagram in v1. Sources: RSS, schema.org Event (JSON-LD), HTML program pages.

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
