from __future__ import annotations

import yaml

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
BLOCK_SELECT = "\u5e7f\u544a\u62e6\u622a"
TEST_URL = "http://www.gstatic.com/generate_204"
LOCAL_DNS = ["https://dns.alidns.com/dns-query", "https://doh.pub/dns-query"]
REMOTE_DNS = ["https://1.1.1.1/dns-query", "https://dns.google/dns-query"]
BOOTSTRAP_DNS = ["223.5.5.5", "119.29.29.29"]


def _render_clash_proxy(node: NormalizedNode) -> dict[str, object]:
    proxy: dict[str, object] = {
        "name": node.name,
        "type": node.protocol,
        "server": node.server,
        "port": node.port,
    }
    if node.protocol == "hysteria2":
        proxy["password"] = node.credentials.get("auth", "")
    elif node.protocol == "vmess":
        proxy["uuid"] = node.credentials.get("uuid", "")
        proxy["cipher"] = "auto"
        if node.tls_server_name:
            proxy["tls"] = True
    if node.tls_server_name:
        proxy["sni"] = node.tls_server_name
        proxy["servername"] = node.tls_server_name
    if node.skip_cert_verify:
        proxy["skip-cert-verify"] = True
    return proxy


def _select_group(name: str, proxies: list[str]) -> dict[str, object]:
    return {
        "name": name,
        "type": "select",
        "proxies": proxies,
    }


def render_clash_yaml(nodes: list[NormalizedNode]) -> str:
    node_names = [node.name for node in nodes]
    policy_proxies = [NODE_SELECT, AUTO_SELECT, *node_names, DIRECT_SELECT]
    document = {
        "proxies": [_render_clash_proxy(node) for node in nodes],
        "proxy-groups": [
            _select_group(NODE_SELECT, [AUTO_SELECT, *node_names, DIRECT_SELECT]),
            {
                "name": AUTO_SELECT,
                "type": "url-test",
                "url": TEST_URL,
                "interval": 300,
                "proxies": node_names,
            },
            _select_group(AI_SELECT, policy_proxies),
            _select_group(YOUTUBE_SELECT, policy_proxies),
            _select_group(GOOGLE_SELECT, policy_proxies),
            _select_group(HK_SELECT, policy_proxies),
            _select_group(TELEGRAM_SELECT, policy_proxies),
            _select_group(GITHUB_SELECT, policy_proxies),
            _select_group(NETFLIX_SELECT, policy_proxies),
            _select_group(MICROSOFT_SELECT, policy_proxies),
            _select_group(APPLE_SELECT, policy_proxies),
            _select_group(DIRECT_SELECT, ["DIRECT"]),
            _select_group(FALLBACK_SELECT, [NODE_SELECT, DIRECT_SELECT]),
            _select_group(BLOCK_SELECT, ["REJECT", NODE_SELECT]),
        ],
        "dns": {
            "enable": True,
            "ipv6": False,
            "enhanced-mode": "fake-ip",
            "nameserver": LOCAL_DNS,
            "fallback": REMOTE_DNS,
            "default-nameserver": BOOTSTRAP_DNS,
            "proxy-server-nameserver": LOCAL_DNS,
            "direct-nameserver": LOCAL_DNS,
            "direct-nameserver-follow-policy": True,
            "nameserver-policy": {
                "geosite:private": LOCAL_DNS,
                "geosite:cn": LOCAL_DNS,
                "+.google.com": REMOTE_DNS,
                "+.hk": REMOTE_DNS,
                "+.youtube.com": REMOTE_DNS,
                "+.telegram.org": REMOTE_DNS,
                "+.github.com": REMOTE_DNS,
                "+.netflix.com": REMOTE_DNS,
                "+.microsoft.com": REMOTE_DNS,
                "+.apple.com": REMOTE_DNS,
            },
            "fallback-filter": {
                "geoip": True,
                "geoip-code": "CN",
                "geosite": ["gfw"],
            },
        },
        "rules": [
            f"GEOSITE,openai,{AI_SELECT}",
            f"GEOSITE,anthropic,{AI_SELECT}",
            f"GEOSITE,youtube,{YOUTUBE_SELECT}",
            f"GEOSITE,google,{GOOGLE_SELECT}",
            f"GEOIP,google,{GOOGLE_SELECT}",
            f"DOMAIN-SUFFIX,tvb.com,{HK_SELECT}",
            f"DOMAIN-SUFFIX,hk,{HK_SELECT}",
            f"GEOSITE,telegram,{TELEGRAM_SELECT}",
            f"GEOIP,telegram,{TELEGRAM_SELECT}",
            f"GEOSITE,github,{GITHUB_SELECT}",
            f"GEOSITE,netflix,{NETFLIX_SELECT}",
            f"GEOIP,netflix,{NETFLIX_SELECT}",
            f"GEOSITE,microsoft,{MICROSOFT_SELECT}",
            f"GEOSITE,apple,{APPLE_SELECT}",
            f"DOMAIN-KEYWORD,ad,{BLOCK_SELECT}",
            f"GEOSITE,PRIVATE,{DIRECT_SELECT}",
            f"GEOSITE,CN,{DIRECT_SELECT}",
            f"GEOIP,private,{DIRECT_SELECT}",
            f"GEOIP,HK,{HK_SELECT}",
            f"GEOIP,CN,{DIRECT_SELECT}",
            f"MATCH,{FALLBACK_SELECT}",
        ],
    }
    return yaml.safe_dump(document, allow_unicode=True, sort_keys=False)
