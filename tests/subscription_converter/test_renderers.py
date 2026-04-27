import json

import yaml

from subscription_converter.models import NormalizedNode
from subscription_converter.renderers import render_clash_yaml, render_singbox_json

NODE_SELECT = "\u8282\u70b9\u9009\u62e9"
AUTO_SELECT = "\u81ea\u52a8\u9009\u62e9"
AI_SELECT = "AI"
YOUTUBE_SELECT = "YouTube"
GOOGLE_SELECT = "Google"
TELEGRAM_SELECT = "Telegram"
GITHUB_SELECT = "GitHub"
NETFLIX_SELECT = "Netflix"
MICROSOFT_SELECT = "Microsoft"
APPLE_SELECT = "Apple"
HK_SELECT = "HK"
DIRECT_SELECT = "\u56fd\u5185\u76f4\u8fde"
FALLBACK_SELECT = "\u6f0f\u7f51\u4e4b\u9c7c"
BLOCK_SELECT = "\u5e7f\u544a\u62e6\u622a"
RULES_HTTP_CLIENT = "rules-http"
CLASH_LOCAL_DNS = ["https://dns.alidns.com/dns-query", "https://doh.pub/dns-query"]
CLASH_REMOTE_DNS = ["https://1.1.1.1/dns-query", "https://dns.google/dns-query"]
CLASH_OPENAI_RULESET_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@meta/geo/geosite/openai.mrs"
CLASH_ANTHROPIC_RULESET_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@meta/geo/geosite/anthropic.mrs"
SING_OPENAI_RULESET_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/openai.srs"
SING_ANTHROPIC_RULESET_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/anthropic.srs"
SING_GOOGLE_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/google.srs"
SING_YOUTUBE_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/youtube.srs"
SING_TELEGRAM_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/telegram.srs"
SING_GITHUB_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/github.srs"
SING_NETFLIX_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/netflix.srs"
SING_MICROSOFT_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/microsoft.srs"
SING_APPLE_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/apple.srs"
SING_PRIVATE_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/private.srs"
SING_CN_GEOSITE_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geosite/cn.srs"
SING_GOOGLE_GEOIP_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geoip/google.srs"
SING_TELEGRAM_GEOIP_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geoip/telegram.srs"
SING_NETFLIX_GEOIP_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geoip/netflix.srs"
SING_PRIVATE_GEOIP_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geoip/private.srs"
SING_CN_GEOIP_URL = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo/geoip/cn.srs"


def _sample_nodes() -> list[NormalizedNode]:
    return [
        NormalizedNode(
            name="HK Hysteria2",
            protocol="hysteria2",
            server="hk.example.com",
            port=443,
            credentials={"auth": "top-secret"},
            tls_server_name="www.bing.com",
            skip_cert_verify=True,
        ),
        NormalizedNode(
            name="US Vmess",
            protocol="vmess",
            server="us.example.com",
            port=8443,
            credentials={"uuid": "11111111-2222-3333-4444-555555555555"},
            tls_server_name="edge.example.com",
        ),
    ]


def test_render_clash_yaml_renders_nodes_groups_dns_and_rules():
    rendered = render_clash_yaml(_sample_nodes())

    data = yaml.safe_load(rendered)
    group_names = [group["name"] for group in data["proxy-groups"]]

    assert [proxy["name"] for proxy in data["proxies"]] == ["HK Hysteria2", "US Vmess"]
    assert data["proxies"][0]["password"] == "top-secret"
    assert data["proxies"][0]["skip-cert-verify"] is True
    assert data["proxies"][1]["uuid"] == "11111111-2222-3333-4444-555555555555"
    assert data["proxies"][1]["tls"] is True
    assert group_names == [
        NODE_SELECT,
        AUTO_SELECT,
        AI_SELECT,
        YOUTUBE_SELECT,
        GOOGLE_SELECT,
        HK_SELECT,
        TELEGRAM_SELECT,
        GITHUB_SELECT,
        NETFLIX_SELECT,
        MICROSOFT_SELECT,
        APPLE_SELECT,
        DIRECT_SELECT,
        FALLBACK_SELECT,
        BLOCK_SELECT,
    ]
    assert data["proxy-groups"][0]["proxies"] == [AUTO_SELECT, "HK Hysteria2", "US Vmess", DIRECT_SELECT]
    assert data["dns"]["enable"] is True
    assert data["dns"]["nameserver"] == CLASH_LOCAL_DNS
    assert data["dns"]["fallback"] == CLASH_REMOTE_DNS
    assert data["dns"]["default-nameserver"] == ["223.5.5.5", "119.29.29.29"]
    assert data["dns"]["proxy-server-nameserver"] == CLASH_LOCAL_DNS
    assert data["dns"]["direct-nameserver"] == CLASH_LOCAL_DNS
    assert data["dns"]["direct-nameserver-follow-policy"] is True
    assert data["dns"]["nameserver-policy"] == {
        "geosite:private": CLASH_LOCAL_DNS,
        "geosite:cn": CLASH_LOCAL_DNS,
        "+.google.com": CLASH_REMOTE_DNS,
        "+.hk": CLASH_REMOTE_DNS,
        "+.youtube.com": CLASH_REMOTE_DNS,
        "+.telegram.org": CLASH_REMOTE_DNS,
        "+.github.com": CLASH_REMOTE_DNS,
        "+.netflix.com": CLASH_REMOTE_DNS,
        "+.microsoft.com": CLASH_REMOTE_DNS,
        "+.apple.com": CLASH_REMOTE_DNS,
    }
    assert data["dns"]["fallback-filter"] == {
        "geoip": True,
        "geoip-code": "CN",
        "geosite": ["gfw"],
    }
    assert "rule-providers" not in data
    assert any(rule == f"GEOSITE,openai,{AI_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOSITE,anthropic,{AI_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOSITE,youtube,{YOUTUBE_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOSITE,google,{GOOGLE_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOIP,google,{GOOGLE_SELECT}" for rule in data["rules"])
    assert any(rule == f"DOMAIN-SUFFIX,tvb.com,{HK_SELECT}" for rule in data["rules"])
    assert any(rule == f"DOMAIN-SUFFIX,hk,{HK_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOIP,HK,{HK_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOSITE,telegram,{TELEGRAM_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOIP,telegram,{TELEGRAM_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOSITE,github,{GITHUB_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOSITE,netflix,{NETFLIX_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOIP,netflix,{NETFLIX_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOSITE,microsoft,{MICROSOFT_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOSITE,apple,{APPLE_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOSITE,PRIVATE,{DIRECT_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOSITE,CN,{DIRECT_SELECT}" for rule in data["rules"])
    assert any(rule == f"GEOIP,private,{DIRECT_SELECT}" for rule in data["rules"])
    assert data["rules"][-1] == f"MATCH,{FALLBACK_SELECT}"


def test_render_singbox_json_renders_outbounds_dns_and_route():
    rendered = render_singbox_json(_sample_nodes())

    data = json.loads(rendered)
    outbound_tags = [outbound["tag"] for outbound in data["outbounds"][2:]]
    dns_servers = data["dns"]["servers"]

    assert [outbound["tag"] for outbound in data["outbounds"][:2]] == [
        "HK Hysteria2",
        "US Vmess",
    ]
    assert data["outbounds"][0]["password"] == "top-secret"
    assert data["outbounds"][0]["tls"] == {
        "enabled": True,
        "server_name": "www.bing.com",
        "insecure": True,
    }
    assert data["outbounds"][1]["uuid"] == "11111111-2222-3333-4444-555555555555"
    assert outbound_tags == [
        NODE_SELECT,
        AUTO_SELECT,
        AI_SELECT,
        YOUTUBE_SELECT,
        GOOGLE_SELECT,
        HK_SELECT,
        TELEGRAM_SELECT,
        GITHUB_SELECT,
        NETFLIX_SELECT,
        MICROSOFT_SELECT,
        APPLE_SELECT,
        DIRECT_SELECT,
        FALLBACK_SELECT,
    ]
    assert data["dns"]["strategy"] == "prefer_ipv4"
    assert dns_servers == [
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
    ]
    assert data["dns"]["final"] == "dns-remote"
    assert data["dns"]["rules"][0] == {
        "clash_mode": "Direct",
        "action": "route",
        "server": "dns-direct",
    }
    assert any(rule == {"rule_set": ["openai", "anthropic"], "action": "route", "server": "dns-remote"} for rule in data["dns"]["rules"])
    assert any(rule == {"rule_set": ["google", "youtube", "telegram", "github", "netflix", "microsoft", "apple"], "action": "route", "server": "dns-remote"} for rule in data["dns"]["rules"])
    assert any(
        rule == {
            "rule_set": ["geoip-private", "geosite-private", "geoip-cn", "geosite-cn"],
            "action": "route",
            "server": "dns-direct",
        }
        for rule in data["dns"]["rules"]
    )
    assert any(
        rule == {
            "domain_suffix": ["hk"],
            "action": "route",
            "server": "dns-remote",
        }
        for rule in data["dns"]["rules"]
    )
    assert data["route"]["final"] == FALLBACK_SELECT
    assert data["route"]["default_domain_resolver"] == "dns-remote"
    assert any(rule.get("outbound") == AI_SELECT for rule in data["route"]["rules"])
    assert any(rule == {"rule_set": ["openai", "anthropic"], "action": "route", "outbound": AI_SELECT} for rule in data["route"]["rules"])
    assert any(rule == {"rule_set": ["youtube"], "action": "route", "outbound": YOUTUBE_SELECT} for rule in data["route"]["rules"])
    assert any(rule == {"rule_set": ["google", "geoip-google"], "action": "route", "outbound": GOOGLE_SELECT} for rule in data["route"]["rules"])
    assert any(
        rule == {
            "rule_set": ["geoip-cn", "geosite-cn"],
            "action": "route",
            "outbound": DIRECT_SELECT,
        }
        for rule in data["route"]["rules"]
    )
    assert any(
        rule == {
            "domain_suffix": ["hk"],
            "action": "route",
            "outbound": HK_SELECT,
        }
        for rule in data["route"]["rules"]
    )
    assert any(rule == {"domain_suffix": ["tvb.com"], "action": "route", "outbound": HK_SELECT} for rule in data["route"]["rules"])
    assert any(
        rule == {
            "rule_set": ["geoip-hk"],
            "action": "route",
            "outbound": HK_SELECT,
        }
        for rule in data["route"]["rules"]
    )
    assert any(rule == {"rule_set": ["telegram", "geoip-telegram"], "action": "route", "outbound": TELEGRAM_SELECT} for rule in data["route"]["rules"])
    assert any(rule == {"rule_set": ["github"], "action": "route", "outbound": GITHUB_SELECT} for rule in data["route"]["rules"])
    assert any(rule == {"rule_set": ["netflix", "geoip-netflix"], "action": "route", "outbound": NETFLIX_SELECT} for rule in data["route"]["rules"])
    assert any(rule == {"rule_set": ["microsoft"], "action": "route", "outbound": MICROSOFT_SELECT} for rule in data["route"]["rules"])
    assert any(rule == {"rule_set": ["apple"], "action": "route", "outbound": APPLE_SELECT} for rule in data["route"]["rules"])
    assert any(rule == {"rule_set": ["geoip-private", "geosite-private"], "action": "route", "outbound": DIRECT_SELECT} for rule in data["route"]["rules"])
    assert any(rule == {"domain_keyword": ["ad"], "action": "reject"} for rule in data["route"]["rules"])
    assert data["route"]["rules"][-1] == {"ip_is_private": True, "action": "route", "outbound": DIRECT_SELECT}
    assert all("geoip" not in rule for rule in data["route"]["rules"])
    assert data["http_clients"] == [
        {
            "tag": RULES_HTTP_CLIENT,
        }
    ]
    assert data["route"]["default_http_client"] == RULES_HTTP_CLIENT
    assert data["route"]["rule_set"] == [
        {
            "tag": "openai",
            "type": "remote",
            "format": "binary",
            "url": SING_OPENAI_RULESET_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "anthropic",
            "type": "remote",
            "format": "binary",
            "url": SING_ANTHROPIC_RULESET_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "google",
            "type": "remote",
            "format": "binary",
            "url": SING_GOOGLE_GEOSITE_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "youtube",
            "type": "remote",
            "format": "binary",
            "url": SING_YOUTUBE_GEOSITE_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "telegram",
            "type": "remote",
            "format": "binary",
            "url": SING_TELEGRAM_GEOSITE_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "github",
            "type": "remote",
            "format": "binary",
            "url": SING_GITHUB_GEOSITE_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "netflix",
            "type": "remote",
            "format": "binary",
            "url": SING_NETFLIX_GEOSITE_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "microsoft",
            "type": "remote",
            "format": "binary",
            "url": SING_MICROSOFT_GEOSITE_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "apple",
            "type": "remote",
            "format": "binary",
            "url": SING_APPLE_GEOSITE_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "geoip-private",
            "type": "remote",
            "format": "binary",
            "url": SING_PRIVATE_GEOIP_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "geosite-private",
            "type": "remote",
            "format": "binary",
            "url": SING_PRIVATE_GEOSITE_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "geoip-hk",
            "type": "remote",
            "format": "binary",
            "url": "https://testingcf.jsdelivr.net/gh/SagerNet/sing-geoip@rule-set/geoip-hk.srs",
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "geoip-google",
            "type": "remote",
            "format": "binary",
            "url": SING_GOOGLE_GEOIP_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "geoip-telegram",
            "type": "remote",
            "format": "binary",
            "url": SING_TELEGRAM_GEOIP_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "geoip-netflix",
            "type": "remote",
            "format": "binary",
            "url": SING_NETFLIX_GEOIP_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "geoip-cn",
            "type": "remote",
            "format": "binary",
            "url": SING_CN_GEOIP_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
        {
            "tag": "geosite-cn",
            "type": "remote",
            "format": "binary",
            "url": SING_CN_GEOSITE_URL,
            "http_client": RULES_HTTP_CLIENT,
        },
    ]
    assert data["experimental"]["cache_file"] == {"enabled": True}


def test_render_singbox_json_always_adds_tls_for_hysteria2():
    rendered = render_singbox_json(
        [
            NormalizedNode(
                name="Bare Hysteria2",
                protocol="hysteria2",
                server="bare.example.com",
                port=443,
                credentials={"auth": "secret"},
            )
        ]
    )

    data = json.loads(rendered)

    assert data["outbounds"][0]["tag"] == "Bare Hysteria2"
    assert data["outbounds"][0]["tls"] == {
        "enabled": True,
        "server_name": "",
        "insecure": False,
    }
