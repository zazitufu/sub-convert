from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests


RULE_URLS = {
    "ads": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ads-all.mrs",
    "openai": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/openai.mrs",
    "claude": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/anthropic.mrs",
    "youtube": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/youtube.mrs",
    "google": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/google.mrs",
    "telegram": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/telegram.mrs",
    "github": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/github.mrs",
    "netflix": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/netflix.mrs",
    "microsoft": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/microsoft.mrs",
    "apple": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/apple.mrs",
    "private": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/private.mrs",
    "cn": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/cn.mrs",
}


class RuleCatalog:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir

    def refresh_if_due(self, state: dict, refresh_hours: int) -> bool:
        rules_state = state.setdefault("rules", {})
        last_refresh = rules_state.get("last_refresh")
        if last_refresh:
            last_refresh_at = datetime.fromisoformat(last_refresh)
            if datetime.now(timezone.utc) - last_refresh_at < timedelta(hours=refresh_hours):
                return False

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        for name, url in RULE_URLS.items():
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            (self.cache_dir / f"{name}.mrs").write_bytes(response.content)

        rules_state["last_refresh"] = datetime.now(timezone.utc).isoformat()
        return True
