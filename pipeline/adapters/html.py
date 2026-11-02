"""Dispatcher for HTML adapters.  Routes to the correct venue-specific module."""

import logging

from pipeline.adapters import html_akropolis

log = logging.getLogger(__name__)

_STRATEGIES = {
    "akropolis": html_akropolis,
}


def fetch(venue: dict, source_config: dict) -> list:
    strategy = source_config.get("strategy")
    module = _STRATEGIES.get(strategy)
    if module is None:
        log.warning("%s [html]: unknown strategy '%s'", venue["id"], strategy)
        return []
    return module.fetch(venue, source_config)
