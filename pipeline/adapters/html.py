"""Dispatcher for HTML adapters.  Routes to the correct venue-specific module."""

import logging

from pipeline.adapters import (html_akropolis, html_archa, html_epic, html_fortuna,
                               html_forum_karlin, html_futurum, html_jazzrepublic, html_kcp,
                               html_lucerna, html_o2, html_roxy, html_sasazu)

log = logging.getLogger(__name__)

_STRATEGIES = {
    "akropolis": html_akropolis,
    "archa": html_archa,
    "epic": html_epic,
    "fortuna": html_fortuna,
    "forum_karlin": html_forum_karlin,
    "futurum": html_futurum,
    "jazzrepublic": html_jazzrepublic,
    "kcp": html_kcp,
    "lucerna": html_lucerna,
    "o2": html_o2,
    "roxy": html_roxy,
    "sasazu": html_sasazu,
}


def fetch(venue: dict, source_config: dict) -> list:
    strategy = source_config.get("strategy")
    module = _STRATEGIES.get(strategy)
    if module is None:
        log.warning("%s [html]: unknown strategy '%s'", venue["id"], strategy)
        return []
    return module.fetch(venue, source_config)
