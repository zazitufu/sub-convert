from __future__ import annotations

import json

from subscription_converter.models import NormalizedNode

NODE_SELECT = "\u8282\u70b9\u9009\u62e9"
AUTO_SELECT = "\u81ea\u52a8\u9009\u62e9"
AI_SELECT = "AI"
YOUTUBE_SELECT = "YouTube"
GOOGLE_SELECT = "Google"
HK_SELECT = "HK"
TELEGRAM_SELECT = "Telegram"
GITHUB_SELECT = "GitHub"
NETFLIX_SELECT = "Netflix"
MICROSOFT_SELECT = "Microsoft"
APPLE_SELECT = "Apple"
DIRECT_SELECT = "\u56fd\u5185\u76f4\u8fde"
FALLBACK_SELECT = "\u6f0f\u7f51\u4e4b\u9c7c"
TEST_URL = "http://www.gstatic.com/generate_204"
GEOIP_PRIVATE_RULESET_URL = "https://testingcf.jsdelivr.net/gh/SagerNet/sing-geoip@rule-set/geoip-private.srs"
GEOSITE_PRIVATE_RULESET_URL = "https://testingcf.jsdelivr.net/gh/SagerNet/sing-geosite@rule-set/geosite-private.srs"
GEOIP_HK_RULESET_URL = "https://testingcf.jsdelivr.net/gh/SagerNet/sing-geoip@rule-set/geoip-hk.srs"
GEOIP_CN_RULESET_URL = "https://testingcf.jsdelivr.net/gh/SagerNet/sing-geoip@rule-set/geoip-cn.srs"
GEOSITE_CN_RULESET_URL = "https://testingcf.jsdelivr.net/gh/SagerNet/sing-geosite@rule-set/geosite-cn.srs"
OPENAI_RULESET_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/openai.srs"
ANTHROPIC_RULESET_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/anthropic.srs"
GOOGLE_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/google.srs"
YOUTUBE_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/youtube.srs"
TELEGRAM_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/telegram.srs"
GITHUB_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/github.srs"
NETFLIX_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/netflix.srs"
MICROSOFT_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/microsoft.srs"
APPLE_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/apple.srs"
PRIVATE_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/private.srs"
CN_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/cn.srs"
GOOGLE_GEOIP_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geoip/google.srs"
TELEGRAM_GEOIP_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geoip/telegram.srs"
NETFLIX_GEOIP_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geoip/netflix.srs"
PRIVATE_GEOIP_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geoip/private.srs"
CN_GEOIP_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geoip/cn.srs"
RULES_HTTP_CLIENT = "rules-http"


def _render_singbox_outbound(node: NormalizedNode) -> dict[str, object]:
    outbound: dict[str, object] = {
        "tag": node.name,
        "type": node.protocol,
        "server": node.server,
        "server_port": node.port,
    }
    if node.protocol == "hysteria2":
        outbound["password"] = node.credentials.get("auth", "")
        outbound["tls"] = {
            "enabled": True,
            "server_name": node.tls_server_name or "",
            "insecure": node.skip_cert_verify,
        }
    elif node.protocol == "vmess":
        outbound["uuid"] = node.credentials.get("uuid", "")
    if node.protocol != "hysteria2" and (node.tls_server_name or node.skip_cert_verify):
        outbound["tls"] = {
            "enabled": True,
            "server_name": node.tls_server_name or "",
            "insecure": node.skip_cert_verify,
        }
    return outbound


def _selector_outbound(tag: str, outbounds: list[str]) -> dict[str, object]:
    return {
        "tag": tag,
        "type": "selector",
        "outbounds": outbounds,
    }


def render_singbox_json(nodes: list[NormalizedNode]) -> str:
    node_names = [node.name for node in nodes]
    policy_outbounds = [NODE_SELECT, AUTO_SELECT, *node_names, DIRECT_SELECT]
    document = {
        "http_clients": [
            {
                "tag": RULES_HTTP_CLIENT,
            }
        ],
        "dns": {
            "strategy": "prefer_ipv4",
            "servers": [
                {
                    "tag": "dns-direct",
                    "type": "udp",
                    "server": "223.5.5.5",
                    "server_port": 53,
                },
                {
                    "tag": "dns-remote",
                    "type": "https",
                    "server": "1.1.1.1",
                    "server_port": 443,
                    "path": "/dns-query",
                    "detour": NODE_SELECT,
                },
            ],
            "rules": [
                {"clash_mode": "Direct", "action": "route", "server": "dns-direct"},
                {
                    "rule_set": ["geoip-private", "geosite-private", "geoip-cn", "geosite-cn"],
                    "action": "route",
                    "server": "dns-direct",
                },
                {"rule_set": ["openai", "anthropic"], "action": "route", "server": "dns-remote"},
                {"rule_set": ["google", "youtube", "telegram", "github", "netflix", "microsoft", "apple"], "action": "route", "server": "dns-remote"},
                {"domain_suffix": ["tvb.com"], "action": "route", "server": "dns-remote"},
                {"domain_suffix": ["hk"], "action": "route", "server": "dns-remote"},
            ],
            "final": "dns-remote",
        },
        "outbounds": [
            *[_render_singbox_outbound(node) for node in nodes],
            _selector_outbound(NODE_SELECT, [AUTO_SELECT, *node_names, DIRECT_SELECT]),
            {
                "tag": AUTO_SELECT,
                "type": "urltest",
                "url": TEST_URL,
                "interval": "5m",
                "outbounds": node_names,
            },
            _selector_outbound(AI_SELECT, policy_outbounds),
            _selector_outbound(YOUTUBE_SELECT, policy_outbounds),
            _selector_outbound(GOOGLE_SELECT, policy_outbounds),
            _selector_outbound(HK_SELECT, policy_outbounds),
            _selector_outbound(TELEGRAM_SELECT, policy_outbounds),
            _selector_outbound(GITHUB_SELECT, policy_outbounds),
            _selector_outbound(NETFLIX_SELECT, policy_outbounds),
            _selector_outbound(MICROSOFT_SELECT, policy_outbounds),
            _selector_outbound(APPLE_SELECT, policy_outbounds),
            {"tag": DIRECT_SELECT, "type": "direct"},
            _selector_outbound(FALLBACK_SELECT, [NODE_SELECT, DIRECT_SELECT]),
        ],
        "route": {
            "final": FALLBACK_SELECT,
            "default_domain_resolver": "dns-remote",
            "default_http_client": RULES_HTTP_CLIENT,
            "rule_set": [
                {
                    "tag": "openai",
                    "type": "remote",
                    "format": "binary",
                    "url": OPENAI_RULESET_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "anthropic",
                    "type": "remote",
                    "format": "binary",
                    "url": ANTHROPIC_RULESET_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "google",
                    "type": "remote",
                    "format": "binary",
                    "url": GOOGLE_GEOSITE_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "youtube",
                    "type": "remote",
                    "format": "binary",
                    "url": YOUTUBE_GEOSITE_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "telegram",
                    "type": "remote",
                    "format": "binary",
                    "url": TELEGRAM_GEOSITE_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "github",
                    "type": "remote",
                    "format": "binary",
                    "url": GITHUB_GEOSITE_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "netflix",
                    "type": "remote",
                    "format": "binary",
                    "url": NETFLIX_GEOSITE_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "microsoft",
                    "type": "remote",
                    "format": "binary",
                    "url": MICROSOFT_GEOSITE_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "apple",
                    "type": "remote",
                    "format": "binary",
                    "url": APPLE_GEOSITE_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "geoip-private",
                    "type": "remote",
                    "format": "binary",
                    "url": PRIVATE_GEOIP_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "geosite-private",
                    "type": "remote",
                    "format": "binary",
                    "url": PRIVATE_GEOSITE_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "geoip-hk",
                    "type": "remote",
                    "format": "binary",
                    "url": GEOIP_HK_RULESET_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "geoip-google",
                    "type": "remote",
                    "format": "binary",
                    "url": GOOGLE_GEOIP_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "geoip-telegram",
                    "type": "remote",
                    "format": "binary",
                    "url": TELEGRAM_GEOIP_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "geoip-netflix",
                    "type": "remote",
                    "format": "binary",
                    "url": NETFLIX_GEOIP_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "geoip-cn",
                    "type": "remote",
                    "format": "binary",
                    "url": CN_GEOIP_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
                {
                    "tag": "geosite-cn",
                    "type": "remote",
                    "format": "binary",
                    "url": CN_GEOSITE_URL,
                    "http_client": RULES_HTTP_CLIENT,
                },
            ],
            "rules": [
                {"rule_set": ["openai", "anthropic"], "action": "route", "outbound": AI_SELECT},
                {"rule_set": ["youtube"], "action": "route", "outbound": YOUTUBE_SELECT},
                {"rule_set": ["google", "geoip-google"], "action": "route", "outbound": GOOGLE_SELECT},
                {"domain_suffix": ["tvb.com"], "action": "route", "outbound": HK_SELECT},
                {"domain_suffix": ["hk"], "action": "route", "outbound": HK_SELECT},
                {"rule_set": ["telegram", "geoip-telegram"], "action": "route", "outbound": TELEGRAM_SELECT},
                {"rule_set": ["github"], "action": "route", "outbound": GITHUB_SELECT},
                {"rule_set": ["netflix", "geoip-netflix"], "action": "route", "outbound": NETFLIX_SELECT},
                {"rule_set": ["microsoft"], "action": "route", "outbound": MICROSOFT_SELECT},
                {"rule_set": ["apple"], "action": "route", "outbound": APPLE_SELECT},
                {"domain_keyword": ["ad"], "action": "reject"},
                {"rule_set": ["geoip-hk"], "action": "route", "outbound": HK_SELECT},
                {"rule_set": ["geoip-private", "geosite-private"], "action": "route", "outbound": DIRECT_SELECT},
                {"rule_set": ["geoip-cn", "geosite-cn"], "action": "route", "outbound": DIRECT_SELECT},
                {"ip_is_private": True, "action": "route", "outbound": DIRECT_SELECT},
            ],
        },
        "experimental": {
            "cache_file": {
                "enabled": True,
            }
        },
    }
    return json.dumps(document, ensure_ascii=False, indent=2)
