import logging

import subscription_converter.cli as cli


class FakeConfig:
    scan_interval_seconds = 10


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
