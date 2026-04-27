import base64
import json
from pathlib import Path

from subscription_converter.config import ConverterConfig
from subscription_converter.models import NormalizedNode
from subscription_converter.parser import parse_subscription_text


def test_converter_config_defaults():
    config = ConverterConfig()

    assert config.scan_dir == Path("/srv/sub-convert/subscriptions")
    assert config.scan_interval_seconds == 10
    assert config.rules_refresh_hours == 24
    assert config.state_file.name == "converter-state.json"


def test_converter_config_reads_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("SUBSCRIPTIONS_DIR", str(tmp_path / "subscriptions"))
    monkeypatch.setenv("SCAN_INTERVAL_SECONDS", "7")
    monkeypatch.setenv("RULES_REFRESH_HOURS", "12")
    monkeypatch.setenv("RULES_CACHE_DIR", str(tmp_path / "rules"))
    monkeypatch.setenv("STATE_FILE", str(tmp_path / "state.json"))
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "converter.log"))

    config = ConverterConfig()

    assert config.scan_dir == tmp_path / "subscriptions"
    assert config.scan_interval_seconds == 7
    assert config.rules_refresh_hours == 12
    assert config.rules_cache_dir == tmp_path / "rules"
    assert config.state_file == tmp_path / "state.json"
    assert config.log_file == tmp_path / "converter.log"


def test_normalized_node_keeps_required_fields():
    node = NormalizedNode(
        name="demo",
        protocol="hysteria2",
        server="example.com",
        port=443,
        credentials={"auth": "secret"},
        tls_server_name="www.bing.com",
        skip_cert_verify=True,
    )

    assert node.credentials["auth"] == "secret"


def test_parse_subscription_text_decodes_multiple_nodes():
    fixture_path = Path(__file__).parent / "fixtures" / "sample_base64.txt"
    text = fixture_path.read_text(encoding="utf-8").strip()

    nodes = parse_subscription_text(text)

    assert [node.protocol for node in nodes] == ["hysteria2", "vmess"]
    assert nodes[0].server == "node-a.example.net"
    assert nodes[0].credentials["auth"] == "demo-secret"
    assert nodes[1].server == "203.0.113.10"


def test_parse_subscription_text_ignores_bad_lines():
    bad_payload = "not-base64"

    nodes = parse_subscription_text(bad_payload)

    assert nodes == []


def test_parse_subscription_text_accepts_urlsafe_base64_without_padding():
    subscription = "\n".join(
        [
            "hysteria2://secret@example.com:443?sni=www.bing.com&insecure=1#Demo",
            "vmess://"
            + base64.urlsafe_b64encode(
                json.dumps(
                    {
                        "add": "1.2.3.4",
                        "port": "443",
                        "id": "123456789",
                        "ps": "demo",
                        "host": "www.bing.com",
                    }
                ).encode("utf-8")
            ).decode("ascii").rstrip("="),
        ]
    )
    text = base64.urlsafe_b64encode(subscription.encode("utf-8")).decode("ascii").rstrip("=")

    nodes = parse_subscription_text(text)

    assert [node.protocol for node in nodes] == ["hysteria2", "vmess"]
    assert nodes[1].server == "1.2.3.4"


def test_parse_subscription_text_treats_common_truthy_insecure_values_as_true():
    subscription = (
        "hysteria2://secret@example.com:443?sni=www.bing.com&insecure=yes#Demo"
    )
    text = base64.b64encode(subscription.encode("utf-8")).decode("ascii")

    nodes = parse_subscription_text(text)

    assert len(nodes) == 1
    assert nodes[0].skip_cert_verify is True
