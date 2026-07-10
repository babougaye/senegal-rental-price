"""Dependency injection helpers for the FastAPI application.

Loads the trained model once at startup (not on every request) and exposes
it to route handlers via FastAPI's dependency-injection system.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from senegal_rental_price.models.predict import ModelBundle, load_model_bundle
from senegal_rental_price.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for the API, sourced from environment variables."""

    model_name: str = os.environ.get("SRP_MODEL_NAME", "random_forest")
    model_dir: str = os.environ.get("SRP_MODEL_DIR", "models")

    @property
    def model_path(self) -> str:
        return f"{self.model_dir}/{self.model_name}.joblib"

    @property
    def metadata_path(self) -> str:
        return f"{self.model_dir}/{self.model_name}.metadata.json"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()


@lru_cache(maxsize=1)
def get_model_bundle() -> ModelBundle:
    """Load (once) and return the model bundle used to serve predictions.

    In a fuller setup this would pull from an MLflow Model Registry; here it
    reads the locally serialized artifact produced by ``train.py``, which
    keeps the contract identical regardless of where the model actually
    comes from.
    """
    settings = get_settings()
    logger.info("Loading model bundle from %s", settings.model_path)
    return load_model_bundle(settings.model_path, settings.metadata_path)
