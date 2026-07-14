import sys

from loguru import logger

from src.infrastructure.configuration import settings


def setup_logging() -> None:
    """Configures application-wide logging using loguru."""
    logger.remove()

    # Standard structured format for development/production
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        level=settings.log_level.upper(),
        format=log_format,
        enqueue=True,
    )

    logger.info("Logging infrastructure initialized.")
