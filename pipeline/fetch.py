"""Central HTTP fetch module: rate limiting, dev cache, per-source limits."""

import hashlib
import logging
import os
import pathlib
import time

import requests

USER_AGENT = "eventapp/0.1 (personal project; contact matejstolarik@gmail.com)"
REQUEST_DELAY = 1.0        # seconds between requests to same host
CACHE_DIR = pathlib.Path(".cache/http")
DEFAULT_MAX_REQUESTS = 50
DEFAULT_TIMEOUT_SECS = 120

log = logging.getLogger(__name__)

_last_request: dict[str, float] = {}


class LimitExceeded(Exception):
    """Raised when a per-source limit (max_requests or timeout_secs) is hit."""


class Fetcher:
    """HTTP fetcher with per-host rate limiting, optional dev cache, and source limits.

    Tracks request count and elapsed wall-clock time per source run.
    Raises LimitExceeded when max_requests or timeout_secs is exceeded.
    """

    def __init__(
        self,
        *,
        max_requests: int = DEFAULT_MAX_REQUESTS,
        timeout_secs: int = DEFAULT_TIMEOUT_SECS,
        use_cache: bool = False,
    ):
        self.max_requests = max_requests
        self.timeout_secs = timeout_secs
        self.use_cache = use_cache
        self._count = 0
        self._start = time.monotonic()

    def get(self, url: str, http_timeout: int = 30) -> str:
        """Fetch URL and return response text.

        Applies rate limiting, dev cache and source-level limits.
        Raises LimitExceeded if max_requests or timeout_secs is exceeded.
        """
        self._count += 1
        if self._count > self.max_requests:
            raise LimitExceeded(
                f"max_requests={self.max_requests} reached after {self._count - 1} requests"
            )
        elapsed = time.monotonic() - self._start
        if elapsed > self.timeout_secs:
            raise LimitExceeded(
                f"source timeout {self.timeout_secs}s exceeded at {elapsed:.0f}s"
            )

        if self.use_cache:
            cached = _cache_read(url)
            if cached is not None:
                log.debug("cache hit: %s", url)
                return cached

        _rate_limit(url)

        resp = requests.get(
            url, headers={"User-Agent": USER_AGENT}, timeout=http_timeout
        )
        resp.raise_for_status()

        if self.use_cache:
            _cache_write(url, resp.text)

        return resp.text

    @property
    def request_count(self) -> int:
        return self._count


def make_fetcher(source_config: dict) -> Fetcher:
    """Create a Fetcher from source_config; honours EVENTAPP_DEV_CACHE env var."""
    use_cache = bool(os.getenv("EVENTAPP_DEV_CACHE"))
    return Fetcher(
        max_requests=source_config.get("max_requests", DEFAULT_MAX_REQUESTS),
        timeout_secs=source_config.get("timeout_secs", DEFAULT_TIMEOUT_SECS),
        use_cache=use_cache,
    )


# ── rate limiting ─────────────────────────────────────────────────────────────

def _rate_limit(url: str) -> None:
    from urllib.parse import urlparse
    host = urlparse(url).netloc
    now = time.time()
    wait = REQUEST_DELAY - (now - _last_request.get(host, 0.0))
    if wait > 0:
        time.sleep(wait)
    _last_request[host] = time.time()


# ── dev cache ─────────────────────────────────────────────────────────────────

def _cache_path(url: str) -> pathlib.Path:
    key = hashlib.sha256(url.encode()).hexdigest()
    return CACHE_DIR / key[:2] / f"{key}.txt"


def _cache_read(url: str) -> "str | None":
    p = _cache_path(url)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


def _cache_write(url: str, text: str) -> None:
    p = _cache_path(url)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
