import logging
from pathlib import Path

import subscription_converter.cli as cli


class FakeConfig:
    scan_interval_seconds = 10
    log_file = Path("/tmp/sub-convert-test.log")


def test_configure_logging_writes_package_logs_to_configured_file(tmp_path):
    config = FakeConfig()
    config.log_file = tmp_path / "converter.log"
    package_logger = logging.getLogger("subscription_converter")
    original_handlers = list(package_logger.handlers)

    try:
        cli.configure_logging(config)
        logging.getLogger("subscription_converter.cli").error("file-log-check")

        assert "file-log-check" in config.log_file.read_text(encoding="utf-8")
    finally:
        for handler in package_logger.handlers:
            if handler not in original_handlers:
                package_logger.removeHandler(handler)
                handler.close()


def test_daemon_mode_returns_error_code_when_processing_crashes(monkeypatch, caplog):
    class CrashingService:
        def __init__(self, config):
            self.config = config

        def process_once(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(cli, "ConverterConfig", FakeConfig)
    monkeypatch.setattr(cli, "ConverterService", CrashingService)

    with caplog.at_level(logging.ERROR):
        exit_code = cli.main([])

    assert exit_code == 1
    assert "Subscription converter crashed" in caplog.text


def test_daemon_mode_treats_keyboard_interrupt_as_clean_shutdown(monkeypatch, caplog):
    class InterruptedService:
        def __init__(self, config):
            self.config = config

        def process_once(self):
            raise KeyboardInterrupt

    monkeypatch.setattr(cli, "ConverterConfig", FakeConfig)
    monkeypatch.setattr(cli, "ConverterService", InterruptedService)

    with caplog.at_level(logging.INFO):
        exit_code = cli.main([])

    assert exit_code == 0
    assert "Subscription converter stopped" in caplog.text
