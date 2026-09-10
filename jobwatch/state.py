"""Persistent state: which job ids we have already seen."""
from __future__ import annotations

import json
import os


class State:
    def __init__(self, path: str):
        self.path = path
        self.seen: set[str] = self._load()

    def _load(self) -> set[str]:
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, list):
                    return set(str(x) for x in data)
            except Exception:
                pass
        return set()

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(sorted(self.seen), fh, indent=2)

    def new_jobs(self, jobs: list[dict]) -> list[dict]:
        return [j for j in jobs if j["id"] not in self.seen]

    def mark_seen(self, jobs: list[dict]) -> None:
        for j in jobs:
            self.seen.add(j["id"])
