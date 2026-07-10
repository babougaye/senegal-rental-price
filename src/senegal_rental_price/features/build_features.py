"""Feature engineering for the rental price model."""

from __future__ import annotations

import pandas as pd

from senegal_rental_price.utils.logger import get_logger

logger = get_logger(__name__)

EQUIPEMENTS_REFERENCE: list[str] = [
    "climatisation",
    "piscine",
    "gardiennage",
    "parking",
    "groupe_electrogene",
    "ascenseur",
    "jardin",
    "fibre_internet",
    "cuisine_equipee",
    "balcon",
]


def split_equipements(equipements: str) -> list[str]:
    """Split a ``"a|b|c"`` amenities string into a list of tokens."""
    if not equipements:
        return []
    return [e for e in equipements.split("|") if e]


def add_equipements_count(df: pd.DataFrame) -> pd.DataFrame:
    """Add a ``nb_equipements`` column counting the amenities per listing."""
    out = df.copy()
    out["nb_equipements"] = out["equipements"].apply(lambda value: len(split_equipements(value)))
    return out


def add_equipements_dummies(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode each known amenity as its own boolean column."""
    out = df.copy()
    for equip in EQUIPEMENTS_REFERENCE:
        out[f"equip_{equip}"] = out["equipements"].apply(
            lambda value, e=equip: int(e in split_equipements(value))
        )
    return out


def add_surface_per_piece(df: pd.DataFrame) -> pd.DataFrame:
    """Add a ``surface_par_piece`` ratio feature."""
    out = df.copy()
    out["surface_par_piece"] = out["surface_m2"] / out["nb_pieces"].clip(lower=1)
    return out


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the full feature-engineering pipeline and drop raw text columns."""
    logger.info("Building features for %d rows", len(df))
    out = add_equipements_count(df)
    out = add_equipements_dummies(out)
    out = add_surface_per_piece(out)
    out = out.drop(columns=["equipements"], errors="ignore")
    logger.info("Feature engineering done, %d columns produced", out.shape[1])
    return out
