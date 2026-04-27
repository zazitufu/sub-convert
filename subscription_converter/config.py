from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ConverterConfig:
    scan_dir: Path = Path("/srv/sub-convert/subscriptions")
    scan_interval_seconds: int = 10
    rules_refresh_hours: int = 24
    rules_cache_dir: Path = Path("/var/lib/subscription-converter/rules")
    state_file: Path = Path("/var/lib/subscription-converter/converter-state.json")
    log_file: Path = Path("/var/log/subscription-converter.log")
