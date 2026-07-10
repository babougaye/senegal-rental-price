"""Data preprocessing: missing-value handling and categorical encoding."""

from __future__ import annotations

import pandas as pd

from senegal_rental_price.utils.logger import get_logger

logger = get_logger(__name__)

NUMERIC_COLUMNS: list[str] = ["surface_m2", "nb_pieces", "nb_chambres"]
CATEGORICAL_COLUMNS: list[str] = ["ville", "quartier", "type_bien"]
BOOLEAN_COLUMNS: list[str] = ["meuble"]
TARGET_COLUMN: str = "prix_loyer_mensuel"


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Impute missing values with simple, explainable rules.

    - Numeric columns: median imputation.
    - ``quartier``: filled with the literal string ``"inconnu"`` (not every
      city has a neighborhood breakdown).
    - ``equipements``: missing means no amenities, encoded as an empty list.
    """
    out = df.copy()

    for col in NUMERIC_COLUMNS:
        if col in out.columns and out[col].isna().any():
            median = out[col].median()
            n_missing = int(out[col].isna().sum())
            out[col] = out[col].fillna(median)
            logger.info(
                "Imputed %d missing values in '%s' with median=%s",
                n_missing,
                col,
                median,
            )

    if "quartier" in out.columns:
        out["quartier"] = out["quartier"].fillna("inconnu")

    if "equipements" in out.columns:
        out["equipements"] = out["equipements"].fillna("")

    return out


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode categorical columns and cast booleans to int."""
    out = df.copy()

    present_categoricals = [c for c in CATEGORICAL_COLUMNS if c in out.columns]
    if present_categoricals:
        out = pd.get_dummies(out, columns=present_categoricals, dummy_na=False)

    for col in BOOLEAN_COLUMNS:
        if col in out.columns:
            out[col] = out[col].astype(int)

    return out


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full cleaning pipeline: missing values then encoding."""
    logger.info("Starting cleaning pipeline on %d rows", len(df))
    df = handle_missing_values(df)
    df = encode_categoricals(df)
    logger.info("Cleaning pipeline finished, %d columns produced", df.shape[1])
    return df


def compute_price_per_m2(surface_m2: float, prix_loyer_mensuel: float) -> float:
    """Compute the monthly rent price per square meter.

    Raises
    ------
    ValueError
        If ``surface_m2`` is not strictly positive.
    """
    if surface_m2 <= 0:
        raise ValueError("surface_m2 must be strictly positive")
    return prix_loyer_mensuel / surface_m2
