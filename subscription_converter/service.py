from __future__ import annotations

import hashlib
from pathlib import Path

from subscription_converter.config import ConverterConfig
from subscription_converter.parser import parse_subscription_text
from subscription_converter.renderers import render_clash_yaml, render_singbox_json
from subscription_converter.rules import RuleCatalog
from subscription_converter.state import StateStore
from subscription_converter.writer import atomic_write


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_metadata(path: Path) -> dict[str, int | str]:
    stat = path.stat()
    return {
        "digest": _digest(path),
        "mtime_ns": stat.st_mtime_ns,
        "size": stat.st_size,
    }


class ConverterService:
    def __init__(
        self,
        config: ConverterConfig,
        rule_catalog: RuleCatalog | None = None,
    ):
        self.config = config
        self.state_store = StateStore(config.state_file)
        self.rule_catalog = rule_catalog or RuleCatalog(config.rules_cache_dir)

    def process_once(self) -> list[str]:
        state = self.state_store.load()
        self.rule_catalog.refresh_if_due(state, self.config.rules_refresh_hours)
        sources = state["sources"]
        processed: list[str] = []

        for source_path in sorted(self.config.scan_dir.iterdir()):
            if not source_path.is_file() or source_path.suffix:
                continue

            source_name = source_path.name
            source_text = source_path.read_text(encoding="utf-8")
            source_metadata = _source_metadata(source_path)

            if sources.get(source_name) == source_metadata:
                continue

            nodes = parse_subscription_text(source_text)
            if not nodes:
                continue

            atomic_write(source_path.with_suffix(".yaml"), render_clash_yaml(nodes))
            atomic_write(source_path.with_suffix(".json"), render_singbox_json(nodes))

            sources[source_name] = source_metadata
            processed.append(source_name)

        self.state_store.save(state)
        return processed
