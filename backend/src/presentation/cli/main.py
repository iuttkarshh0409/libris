import argparse
import sys

from loguru import logger

from src.infrastructure.logging import setup_logging


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(
        description="CLI utility for Knowledge Retrieval Platform administration."
    )
    parser.add_argument(
        "--status", action="store_true", help="Check the health status of all engines"
    )

    args = parser.parse_args()

    if args.status:
        logger.info("CLI Status check: All systems are operational (placeholder).")
        sys.exit(0)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
