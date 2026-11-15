# Design source (main chat only)

Sources of the design artifact "EventApp – mapa" (https://claude.ai/artifact/6CbW85Yj2AY7LFTqMs48WM).
Used by the main chat to edit the design; Claude Code does not need to read this folder.

- `boards/` – artboards of the design canvas (`*.dc.html`, `canvas.json`), as published in the artifact.
- `gen/` – Python generators for boards (`screens.py`, `pins.py`, `filter.py`). Paths inside point to an old
  scratchpad folder; replace them with a working folder before running.
- `shots/` – Playwright scripts that export boards to `docs/design/screens/` and `docs/design/html/`.

Review helper for the map: `scripts/review/map-names-check.js` (runs the dev app with `?debugPair=1`,
synthetic `events.json` and a stub map style, prints which pin names are visible/hidden/combined).
