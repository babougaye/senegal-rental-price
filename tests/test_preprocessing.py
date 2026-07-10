from __future__ import annotations

import pandas as pd
import pytest

from senegal_rental_price.data.preprocessing import (
    clean_dataset,
    compute_price_per_m2,
    encode_categoricals,
    handle_missing_values,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ville": ["Dakar", "Dakar", "Thiès"],
            "quartier": ["Almadies", None, None],
            "type_bien": ["appartement", "studio", "maison"],
            "surface_m2": [80.0, 30.0, None],
            "nb_pieces": [4, 1, 5],
            "nb_chambres": [2, None, 3],
            "meuble": [True, False, True],
            "equipements": ["climatisation|parking", None, "piscine"],
            "prix_loyer_mensuel": [500000.0, 100000.0, 250000.0],
        }
    )


def test_handle_missing_values_imputes_numeric_with_median() -> None:
    df = _sample_df()
    out = handle_missing_values(df)

    assert out["surface_m2"].isna().sum() == 0
    assert out["surface_m2"].iloc[2] == df["surface_m2"].median()
    assert out["nb_chambres"].isna().sum() == 0


def test_handle_missing_values_fills_quartier_and_equipements() -> None:
    df = _sample_df()
    out = handle_missing_values(df)

    assert out["quartier"].iloc[1] == "inconnu"
    assert out["equipements"].iloc[1] == ""


def test_encode_categoricals_creates_dummy_columns() -> None:
    df = handle_missing_values(_sample_df())
    out = encode_categoricals(df)

    assert "ville_Dakar" in out.columns
    assert "type_bien_studio" in out.columns
    assert out["meuble"].dtype.kind in {"i", "u"}


def test_clean_dataset_end_to_end_has_no_missing_values_in_key_columns() -> None:
    df = _sample_df()
    out = clean_dataset(df)

    assert out["surface_m2"].isna().sum() == 0
    assert out["nb_chambres"].isna().sum() == 0


def test_compute_price_per_m2_basic() -> None:
    assert compute_price_per_m2(surface_m2=100.0, prix_loyer_mensuel=500_000.0) == 5_000.0


def test_compute_price_per_m2_raises_on_non_positive_surface() -> None:
    with pytest.raises(ValueError):
        compute_price_per_m2(surface_m2=0.0, prix_loyer_mensuel=100_000.0)
