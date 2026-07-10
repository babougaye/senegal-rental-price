"""Prediction utilities: load a serialized model and run inference on a single listing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

import joblib
import pandas as pd

from senegal_rental_price.data.preprocessing import (
    CATEGORICAL_COLUMNS,
    encode_categoricals,
    handle_missing_values,
)
from senegal_rental_price.features.build_features import build_features
from senegal_rental_price.utils.logger import get_logger

logger = get_logger(__name__)


class Regressor(Protocol):
    """Structural type for any fitted scikit-learn-like regressor."""

    def predict(self, x: pd.DataFrame) -> Any: ...


class ModelBundle:
    """A trained model together with the feature columns it was fit on."""

    def __init__(
        self, model: Regressor, feature_columns: list[str], metadata: dict[str, Any]
    ) -> None:
        self.model = model
        self.feature_columns = feature_columns
        self.metadata = metadata


def load_model_bundle(model_path: str, metadata_path: str) -> ModelBundle:
    """Load a serialized model and its metadata from disk."""
    model: Regressor = joblib.load(model_path)
    metadata: dict[str, Any] = json.loads(Path(metadata_path).read_text())
    feature_columns: list[str] = metadata["feature_columns"]
    logger.info("Loaded model from %s (%d features)", model_path, len(feature_columns))
    return ModelBundle(model=model, feature_columns=feature_columns, metadata=metadata)


def _listing_to_dataframe(listing: dict[str, Any]) -> pd.DataFrame:
    """Convert a single listing dict (as received by the API) into a one-row DataFrame."""
    row = dict(listing)
    equipements = row.get("equipements", [])
    row["equipements"] = "|".join(equipements) if equipements else ""
    return pd.DataFrame([row])


def align_to_training_columns(df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    """Reindex a feature DataFrame to match the columns seen at training time.

    Missing dummy columns (e.g. a ``ville`` value with no corresponding
    one-hot column in training, which should not happen given the Enum
    validation) are filled with 0; extra columns are dropped.
    """
    return df.reindex(columns=feature_columns, fill_value=0)


def predict_price(bundle: ModelBundle, listing: dict[str, Any]) -> float:
    """Predict the monthly rent price (FCFA) for a single listing."""
    df = _listing_to_dataframe(listing)
    df = handle_missing_values(df)

    present_categoricals = [c for c in CATEGORICAL_COLUMNS if c in df.columns]
    if present_categoricals:
        df = encode_categoricals(df)

    df = build_features(df)
    df = align_to_training_columns(df, bundle.feature_columns)

    prediction = bundle.model.predict(df)
    return float(prediction[0])
