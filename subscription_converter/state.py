from __future__ import annotations

import json
from pathlib import Path

from subscription_converter.writer import atomic_write


class StateStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> dict[str, object]:
        if not self.path.exists():
            return {"sources": {}, "rules": {"last_refresh": None}}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, state: dict[str, object]) -> None:
        atomic_write(self.path, json.dumps(state, indent=2, sort_keys=True))
