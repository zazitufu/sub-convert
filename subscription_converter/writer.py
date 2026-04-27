from __future__ import annotations

import os
import tempfile
from pathlib import Path


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as handle:
        handle.write(text)
        temp_name = handle.name

    os.replace(temp_name, path)
