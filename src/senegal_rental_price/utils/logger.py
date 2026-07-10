"""Centralized logging configuration for the senegal_rental_price package.

This module must be imported (via ``get_logger``) anywhere a log line is
needed. ``print()`` is forbidden in production code (see project spec,
section 3.3): all output must go through this configured logger.
"""

from __future__ import annotations

import logging
import os
import sys

_CONFIGURED = False

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _configure_root_logger() -> None:
    """Configure the root logger exactly once.

    The log level is read from the ``SRP_LOG_LEVEL`` environment variable
    (defaults to ``INFO``), so it can be changed without touching the code.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    level_name = os.environ.get("SRP_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger, configuring the root logger if needed.

    Parameters
    ----------
    name:
        Usually ``__name__`` of the calling module, so log lines show their
        origin.
    """
    _configure_root_logger()
    return logging.getLogger(name)
