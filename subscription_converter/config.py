import os
from dataclasses import dataclass, field
from pathlib import Path


def _path_from_env(name: str, default: str) -> Path:
    return Path(os.environ.get(name, default))


def _int_from_env(name: str, default: int) -> int:
    return int(os.environ.get(name, str(default)))


@dataclass(slots=True)
class ConverterConfig:
    scan_dir: Path = field(
        default_factory=lambda: _path_from_env("SUBSCRIPTIONS_DIR", "/srv/sub-convert/subscriptions")
    )
    scan_interval_seconds: int = field(
        default_factory=lambda: _int_from_env("SCAN_INTERVAL_SECONDS", 10)
    )
    rules_refresh_hours: int = field(default_factory=lambda: _int_from_env("RULES_REFRESH_HOURS", 24))
    rules_cache_dir: Path = field(
        default_factory=lambda: _path_from_env(
            "RULES_CACHE_DIR",
            "/var/lib/subscription-converter/rules",
        )
    )
    state_file: Path = field(
        default_factory=lambda: _path_from_env(
            "STATE_FILE",
            "/var/lib/subscription-converter/converter-state.json",
        )
    )
    log_file: Path = field(
        default_factory=lambda: _path_from_env("LOG_FILE", "/var/log/subscription-converter.log")
    )
