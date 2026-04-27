import base64
import binascii
import json
from urllib.parse import parse_qs, unquote, urlparse

from subscription_converter.models import NormalizedNode


def _decode_base64(text: str) -> str:
    normalized = "".join(text.split())
    padding = (-len(normalized)) % 4
    try:
        raw = base64.b64decode(
            normalized + ("=" * padding),
            altchars=b"-_",
            validate=True,
        )
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Invalid base64 payload") from exc
    return raw.decode("utf-8")


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _parse_hysteria2(line: str) -> NormalizedNode:
    parsed = urlparse(line)
    query = parse_qs(parsed.query)
    return NormalizedNode(
        name=unquote(parsed.fragment or parsed.hostname or "hysteria2"),
        protocol="hysteria2",
        server=parsed.hostname or "",
        port=parsed.port or 0,
        credentials={"auth": unquote(parsed.username or "")},
        tls_server_name=query.get("sni", [None])[0],
        skip_cert_verify=_is_truthy(query.get("insecure", [None])[0]),
    )


def _parse_vmess(line: str) -> NormalizedNode:
    payload = line.removeprefix("vmess://")
    data = json.loads(_decode_base64(payload))
    return NormalizedNode(
        name=data.get("ps", "vmess"),
        protocol="vmess",
        server=data.get("add", ""),
        port=int(data.get("port", 0)),
        credentials={"uuid": data.get("id", "")},
        tls_server_name=data.get("sni") or data.get("host"),
        skip_cert_verify=False,
    )


def parse_subscription_text(text: str) -> list[NormalizedNode]:
    try:
        decoded = _decode_base64(text.strip())
    except Exception:
        return []

    nodes: list[NormalizedNode] = []
    for line in decoded.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            if line.startswith("hysteria2://"):
                nodes.append(_parse_hysteria2(line))
            elif line.startswith("vmess://"):
                nodes.append(_parse_vmess(line))
        except Exception:
            continue
    return nodes
