"""Logging centralisé via loguru avec repli sur logging standard."""

import sys

try:
    from loguru import logger as _loguru_logger

    _loguru_logger.remove()
    _loguru_logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan> - <level>{message}</level>",
    )

    def get_logger(name: str = "deforestwatch"):
        return _loguru_logger.bind(name=name)

except ImportError:  # repli si loguru absent
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    def get_logger(name: str = "deforestwatch"):
        return logging.getLogger(name)
