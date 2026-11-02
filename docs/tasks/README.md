# Task files

Each task is a Markdown file `NNN-short-name.md` in this directory.

## File format

```markdown
# NNN: Short title

## Zadanie
(Written by the main chat / Matej. Do not edit.)

## Report
(Written by Claude at the end of the task.)
```

## Rules

- Files are never deleted or overwritten. A new task = a new number.
- The `## Zadanie` section is written by the main chat; Claude only writes `## Report`.
- Run `git pull` before starting a task — the main chat may have committed the task file.
- Completed tasks stay here forever. Task history: `000-history.md`.

## Report sections

At the end of every task, write `## Report` with:
- Date, commit hashes and messages
- What is done
- Decisions made independently and why
- Numbers: computed from `site/events.json` of the latest pipeline run; always include the command used
- Verification against the web (specific URLs and values)
- What remains open or was not finished

## Rules for the report

- **Commit hash**: write the final hash on `origin/main` **after push**. If a rebase changes it, correct it in the next commit. Never write a local pre-push hash.
- **Otvorené** (open issues): must not say "nothing" if there are known limitations, edge cases, or unverified items. List them explicitly.
