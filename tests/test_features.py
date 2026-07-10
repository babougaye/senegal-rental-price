from __future__ import annotations

import pandas as pd

from senegal_rental_price.features.build_features import (
    add_equipements_count,
    add_equipements_dummies,
    add_surface_per_piece,
    build_features,
    split_equipements,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "surface_m2": [80.0, 30.0],
            "nb_pieces": [4, 1],
            "equipements": ["climatisation|parking", ""],
        }
    )


def test_split_equipements_handles_empty_string() -> None:
    assert split_equipements("") == []


def test_split_equipements_splits_on_pipe() -> None:
    assert split_equipements("climatisation|piscine") == ["climatisation", "piscine"]


def test_add_equipements_count() -> None:
    out = add_equipements_count(_sample_df())
    assert out["nb_equipements"].tolist() == [2, 0]


def test_add_equipements_dummies_creates_expected_columns() -> None:
    out = add_equipements_dummies(_sample_df())
    assert out["equip_climatisation"].tolist() == [1, 0]
    assert out["equip_piscine"].tolist() == [0, 0]


def test_add_surface_per_piece() -> None:
    out = add_surface_per_piece(_sample_df())
    assert out["surface_par_piece"].iloc[0] == 20.0


def test_build_features_drops_raw_equipements_column() -> None:
    out = build_features(_sample_df())
    assert "equipements" not in out.columns
    assert "nb_equipements" in out.columns
    assert "surface_par_piece" in out.columns
