from __future__ import annotations

import argparse
import logging
import time
from collections.abc import Sequence

from subscription_converter import __version__
from subscription_converter.config import ConverterConfig
from subscription_converter.service import ConverterService


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logger = logging.getLogger(__name__)

    try:
        config = ConverterConfig()
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
