from __future__ import annotations

import argparse
import logging
import time
from collections.abc import Sequence

from subscription_converter import __version__
from subscription_converter.config import ConverterConfig
from subscription_converter.service import ConverterService

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert subscription source files into Clash and Sing-box outputs.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process the scan directory once and exit.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def configure_logging(config: ConverterConfig) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
    )

    package_logger = logging.getLogger("subscription_converter")
    log_path = config.log_file
    if any(getattr(handler, "_sub_convert_log_file", None) == str(log_path) for handler in package_logger.handlers):
        return

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
    except OSError:
        logging.getLogger(__name__).exception("Failed to open log file %s", log_path)
        return

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    file_handler._sub_convert_log_file = str(log_path)
    package_logger.addHandler(file_handler)
    package_logger.setLevel(logging.INFO)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logger = logging.getLogger(__name__)

    try:
        config = ConverterConfig()
        configure_logging(config)
        service = ConverterService(config)

        if args.once:
            processed = service.process_once()
            logger.info("Processed sources: %s", processed)
            return 0

        while True:
            processed = service.process_once()
            logger.info("Processed sources: %s", processed)
            time.sleep(config.scan_interval_seconds)
    except KeyboardInterrupt:
        logger.info("Subscription converter stopped")
        return 0
    except Exception:
        logger.exception("Subscription converter crashed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
