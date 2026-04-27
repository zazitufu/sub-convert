import json
import logging
import os
from pathlib import Path

import yaml

import subscription_converter.service as service_module
from subscription_converter.config import ConverterConfig
from subscription_converter.rules import RuleCatalog
from subscription_converter.service import ConverterService, _digest


def _config_for(tmp_path):
    return ConverterConfig(
        scan_dir=tmp_path / "scan",
        rules_cache_dir=tmp_path / "rules",
        state_file=tmp_path / "state.json",
        log_file=tmp_path / "converter.log",
    )


class FakeCatalog(RuleCatalog):
    def __init__(self, cache_dir):
        super().__init__(cache_dir)
        self.refresh_count = 0

    def refresh_if_due(self, state, refresh_hours):
        self.refresh_count += 1
        state.setdefault("rules", {})["last_refresh"] = "2026-04-24T00:00:00+00:00"
        return True


class FailingCatalog(RuleCatalog):
    def refresh_if_due(self, state, refresh_hours):
        raise RuntimeError("rules offline")


def test_service_rebuilds_outputs_for_changed_source(tmp_path):
    fixture_path = Path(__file__).parent / "fixtures" / "sample_base64.txt"
    config = _config_for(tmp_path)
    config.scan_dir.mkdir()
    source = config.scan_dir / "myhy2"
    source.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")
    catalog = FakeCatalog(config.rules_cache_dir)

    service = ConverterService(config, rule_catalog=catalog)

    processed = service.process_once()

    assert processed == ["myhy2"]

    first_state = json.loads(config.state_file.read_text(encoding="utf-8"))
    first_yaml = yaml.safe_load((config.scan_dir / "myhy2.yaml").read_text(encoding="utf-8"))
    first_json = json.loads((config.scan_dir / "myhy2.json").read_text(encoding="utf-8"))

    assert first_yaml["proxies"][0]["server"] == "node-a.example.net"
    assert first_json["outbounds"][0]["tag"] == "Demo-Hy2"
    assert first_state["sources"] == {
        "myhy2": {
            "digest": _digest(source),
            "mtime_ns": source.stat().st_mtime_ns,
            "size": source.stat().st_size,
        }
    }
    assert first_state["rules"] == {"last_refresh": "2026-04-24T00:00:00+00:00"}

    updated_text = (
        "aHlzdGVyaWEyOi8vc2VjcmV0QG5ldy5leGFtcGxlLmNvbTo0NDM/c25pPXd3dy5iaW5nLmNvbSZp"
        "bnNlY3VyZT0xI05ldy1IeTIK"
    )
    source.write_text(updated_text, encoding="utf-8")

    processed = service.process_once()

    assert processed == ["myhy2"]

    second_state = json.loads(config.state_file.read_text(encoding="utf-8"))
    second_yaml = yaml.safe_load((config.scan_dir / "myhy2.yaml").read_text(encoding="utf-8"))
    second_json = json.loads((config.scan_dir / "myhy2.json").read_text(encoding="utf-8"))

    assert second_yaml["proxies"][0]["server"] == "new.example.com"
    assert second_json["outbounds"][0]["tag"] == "New-Hy2"
    assert second_state["sources"] == {
        "myhy2": {
            "digest": _digest(source),
            "mtime_ns": source.stat().st_mtime_ns,
            "size": source.stat().st_size,
        }
    }
    assert second_state["rules"] == {"last_refresh": "2026-04-24T00:00:00+00:00"}


def test_service_rebuilds_outputs_for_touched_source(tmp_path, monkeypatch):
    fixture_path = Path(__file__).parent / "fixtures" / "sample_base64.txt"
    config = _config_for(tmp_path)
    config.scan_dir.mkdir()
    source = config.scan_dir / "myhy2"
    source.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")
    catalog = FakeCatalog(config.rules_cache_dir)

    service = ConverterService(config, rule_catalog=catalog)

    assert service.process_once() == ["myhy2"]

    original_state = json.loads(config.state_file.read_text(encoding="utf-8"))
    recorded_writes = []

    real_atomic_write = service_module.atomic_write

    def recording_atomic_write(path, content):
        recorded_writes.append((path.name, content))
        real_atomic_write(path, content)

    monkeypatch.setattr(service_module, "atomic_write", recording_atomic_write)

    touched_mtime_ns = source.stat().st_mtime_ns + 5_000_000_000
    os.utime(source, ns=(touched_mtime_ns, touched_mtime_ns))

    processed = service.process_once()

    updated_state = json.loads(config.state_file.read_text(encoding="utf-8"))

    assert processed == ["myhy2"]
    assert [name for name, _ in recorded_writes] == ["myhy2.yaml", "myhy2.json"]
    assert updated_state["sources"]["myhy2"]["digest"] == original_state["sources"]["myhy2"]["digest"]
    assert updated_state["sources"]["myhy2"]["size"] == original_state["sources"]["myhy2"]["size"]
    assert updated_state["sources"]["myhy2"]["mtime_ns"] == touched_mtime_ns


def test_service_keeps_previous_outputs_when_source_is_invalid(tmp_path):
    fixture_path = Path(__file__).parent / "fixtures" / "sample_base64.txt"
    config = _config_for(tmp_path)
    config.scan_dir.mkdir()
    source = config.scan_dir / "myhy2"
    source.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")
    (config.scan_dir / "ignored.yaml").write_text("keep: true\n", encoding="utf-8")
    (config.scan_dir / "nested").mkdir()
    catalog = FakeCatalog(config.rules_cache_dir)

    service = ConverterService(config, rule_catalog=catalog)

    assert service.process_once() == ["myhy2"]

    previous_yaml = (config.scan_dir / "myhy2.yaml").read_text(encoding="utf-8")
    previous_json = (config.scan_dir / "myhy2.json").read_text(encoding="utf-8")
    previous_state = json.loads(config.state_file.read_text(encoding="utf-8"))

    source.write_text("not-base64", encoding="utf-8")

    processed = service.process_once()

    assert processed == []
    assert (config.scan_dir / "myhy2.yaml").read_text(encoding="utf-8") == previous_yaml
    assert (config.scan_dir / "myhy2.json").read_text(encoding="utf-8") == previous_json
    assert (config.scan_dir / "ignored.yaml").read_text(encoding="utf-8") == "keep: true\n"
    assert json.loads(config.state_file.read_text(encoding="utf-8")) == previous_state


def test_service_logs_invalid_sources_without_stopping_batch(tmp_path, caplog):
    fixture_path = Path(__file__).parent / "fixtures" / "sample_base64.txt"
    config = _config_for(tmp_path)
    config.scan_dir.mkdir()
    (config.scan_dir / "bad").write_bytes(b"\xff\xfe\x00")
    (config.scan_dir / "empty").write_text("not-base64", encoding="utf-8")
    (config.scan_dir / "valid").write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")

    service = ConverterService(config, rule_catalog=FakeCatalog(config.rules_cache_dir))

    with caplog.at_level(logging.WARNING):
        processed = service.process_once()

    assert processed == ["valid"]
    assert (config.scan_dir / "valid.yaml").exists()
    assert "Failed to process source bad" in caplog.text
    assert "No supported nodes found in source empty" in caplog.text


def test_service_continues_when_rule_refresh_fails(tmp_path, caplog):
    fixture_path = Path(__file__).parent / "fixtures" / "sample_base64.txt"
    config = _config_for(tmp_path)
    config.scan_dir.mkdir()
    (config.scan_dir / "valid").write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")

    service = ConverterService(config, rule_catalog=FailingCatalog(config.rules_cache_dir))

    with caplog.at_level(logging.ERROR):
        processed = service.process_once()

    assert processed == ["valid"]
    assert "Failed to refresh rule assets" in caplog.text


def test_service_refreshes_rules_before_processing(tmp_path: Path):
    scan_dir = tmp_path / "sss"
    scan_dir.mkdir()
    source = scan_dir / "myhy2"
    source.write_text(
        "aHlzdGVyaWEyOi8vZGVtby1zZWNyZXRAbm9kZS1hLmV4YW1wbGUubmV0OjQ0Mz9zbmk9ZXhhbXBsZS5uZXQmaW5zZWN1cmU9MSZhbGxvd0luc2VjdXJlPTEjRGVtby1IeTI=",
        encoding="utf-8",
    )
    config = ConverterConfig(
        scan_dir=scan_dir,
        scan_interval_seconds=10,
        rules_refresh_hours=24,
        rules_cache_dir=tmp_path / "rules",
        state_file=tmp_path / "state.json",
        log_file=tmp_path / "converter.log",
    )
    catalog = FakeCatalog(config.rules_cache_dir)

    service = ConverterService(config, rule_catalog=catalog)
    processed = service.process_once()

    assert processed == ["myhy2"]
    assert catalog.refresh_count == 1


def test_service_upgrades_legacy_state_without_rules_section(tmp_path):
    fixture_path = Path(__file__).parent / "fixtures" / "sample_base64.txt"
    config = _config_for(tmp_path)
    config.scan_dir.mkdir()
    source = config.scan_dir / "myhy2"
    source.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")
    config.state_file.write_text(
        json.dumps({"sources": {"old": {"digest": "stale"}}}),
        encoding="utf-8",
    )
    catalog = FakeCatalog(config.rules_cache_dir)

    service = ConverterService(config, rule_catalog=catalog)

    assert service.process_once() == ["myhy2"]

    state = json.loads(config.state_file.read_text(encoding="utf-8"))
    assert state["sources"]["old"] == {"digest": "stale"}
    assert state["sources"]["myhy2"] == {
        "digest": _digest(source),
        "mtime_ns": source.stat().st_mtime_ns,
        "size": source.stat().st_size,
    }
    assert state["rules"] == {"last_refresh": "2026-04-24T00:00:00+00:00"}
    assert catalog.refresh_count == 1
