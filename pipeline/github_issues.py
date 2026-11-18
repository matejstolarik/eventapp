"""
Minimal GitHub Issues client for alerts and the weekly report (task 057).

Uses the workflow's GITHUB_TOKEN (permissions: issues: write) and
GITHUB_REPOSITORY from the Actions environment; stdlib only.
"""

import json
import os
import urllib.error
import urllib.request

API = "https://api.github.com"

LABEL_COLORS = {"alert": "d73a4a", "weekly-report": "0e8a16"}


class Issues:
    def __init__(self, repo: str | None = None, token: str | None = None):
        self.repo = repo or os.environ["GITHUB_REPOSITORY"]
        self.token = token or os.environ["GITHUB_TOKEN"]

    def _req(self, method: str, path: str, body: dict | None = None):
        req = urllib.request.Request(
            f"{API}/repos/{self.repo}{path}", method=method,
            data=None if body is None else json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {self.token}",
                     "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28",
                     "User-Agent": "eventapp-pipeline",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            return json.loads(data) if data else None

    def ensure_label(self, name: str) -> None:
        try:
            self._req("POST", "/labels", {"name": name,
                                          "color": LABEL_COLORS.get(name, "ededed")})
        except urllib.error.HTTPError as exc:
            if exc.code != 422:          # 422 = already exists
                raise

    def open_issues(self, label: str) -> list[dict]:
        out, page = [], 1
        while True:
            batch = self._req("GET", f"/issues?state=open&labels={label}&per_page=100&page={page}")
            out += [i for i in batch if "pull_request" not in i]
            if len(batch) < 100:
                return out
            page += 1

    def create(self, title: str, body: str, label: str) -> dict:
        self.ensure_label(label)
        return self._req("POST", "/issues", {"title": title, "body": body, "labels": [label]})

    def comment(self, number: int, body: str) -> None:
        self._req("POST", f"/issues/{number}/comments", {"body": body})

    def close(self, number: int, comment: str | None = None) -> None:
        if comment:
            self.comment(number, comment)
        self._req("PATCH", f"/issues/{number}", {"state": "closed", "state_reason": "completed"})
