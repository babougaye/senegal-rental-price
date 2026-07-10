from __future__ import annotations

import numpy as np
import pytest

from senegal_rental_price.data.generate_synthetic_data import (
    TYPES_BIEN,
    VILLE_BASE_PRIX_M2,
    GenerationConfig,
    _sample_equipements,
    _sample_quartier,
    generate_dataset,
    generate_listing_row,
)


def test_sample_quartier_returns_none_outside_dakar() -> None:
    rng = np.random.default_rng(0)
    assert _sample_quartier(rng, "Thiès") is None


def test_sample_quartier_returns_known_name_for_dakar() -> None:
    rng = np.random.default_rng(0)
    quartier = _sample_quartier(rng, "Dakar")
    assert quartier is not None
    assert isinstance(quartier, str)


def test_sample_equipements_returns_unique_subset() -> None:
    rng = np.random.default_rng(1)
    equipements = _sample_equipements(rng)
    assert len(equipements) == len(set(equipements))


def test_generate_listing_row_has_expected_keys_and_types() -> None:
    rng = np.random.default_rng(42)
    row = generate_listing_row(rng)

    assert row["ville"] in VILLE_BASE_PRIX_M2
    assert row["type_bien"] in TYPES_BIEN
    assert row["surface_m2"] > 0
    assert row["nb_pieces"] >= 1
    assert 0 <= row["nb_chambres"] <= row["nb_pieces"]
    assert isinstance(row["meuble"], bool)
    assert row["prix_loyer_mensuel"] >= 30_000.0


def test_generate_listing_row_quartier_only_for_dakar() -> None:
    rng = np.random.default_rng(7)
    for _ in range(20):
        row = generate_listing_row(rng)
        if row["ville"] != "Dakar":
            assert row["quartier"] is None


@pytest.mark.parametrize("n_rows", [10, 50])
def test_generate_dataset_has_correct_shape(n_rows: int) -> None:
    config = GenerationConfig(n_rows=n_rows, seed=123)
    df = generate_dataset(config)

    assert len(df) == n_rows
    assert "prix_loyer_mensuel" in df.columns


def test_generate_dataset_is_reproducible_with_same_seed() -> None:
    df1 = generate_dataset(GenerationConfig(n_rows=20, seed=99))
    df2 = generate_dataset(GenerationConfig(n_rows=20, seed=99))

    assert df1["prix_loyer_mensuel"].tolist() == df2["prix_loyer_mensuel"].tolist()


def test_generate_dataset_injects_some_missing_values() -> None:
    df = generate_dataset(GenerationConfig(n_rows=2000, seed=1))
    assert df["nb_chambres"].isna().sum() > 0
