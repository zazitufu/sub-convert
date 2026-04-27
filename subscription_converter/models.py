from dataclasses import dataclass, field


@dataclass(slots=True)
class NormalizedNode:
    name: str
    protocol: str
    server: str
    port: int
    credentials: dict[str, str] = field(default_factory=dict)
    tls_server_name: str | None = None
    skip_cert_verify: bool = False
