from __future__ import annotations

from typing import Any

import pandas as pd

from senegal_rental_price.models.predict import (
    ModelBundle,
    align_to_training_columns,
    predict_price,
)


class FakeModel:
    """Mock regressor returning a constant prediction, for testing."""

    def predict(self, x: pd.DataFrame) -> Any:
        return [321000.0] * len(x)


def _fake_bundle() -> ModelBundle:
    feature_columns = [
        "surface_m2",
        "nb_pieces",
        "nb_chambres",
        "meuble",
        "nb_equipements",
        "surface_par_piece",
        "equip_climatisation",
        "equip_piscine",
        "ville_Dakar",
        "ville_Thiès",
        "type_bien_appartement",
        "type_bien_studio",
        "type_bien_maison",
        "type_bien_villa",
        "quartier_Almadies",
        "quartier_inconnu",
    ]
    metadata = {
        "model_name": "fake_model",
        "trained_at": "2026-01-01T00:00:00+00:00",
        "metrics": {"rmse": 1.0, "mae": 1.0, "r2": 0.9},
    }
    return ModelBundle(model=FakeModel(), feature_columns=feature_columns, metadata=metadata)


def test_align_to_training_columns_fills_missing_with_zero() -> None:
    df = pd.DataFrame({"surface_m2": [80.0]})
    out = align_to_training_columns(df, ["surface_m2", "ville_Dakar"])

    assert out["ville_Dakar"].iloc[0] == 0
    assert list(out.columns) == ["surface_m2", "ville_Dakar"]


def test_predict_price_returns_float() -> None:
    bundle = _fake_bundle()
    listing = {
        "ville": "Dakar",
        "quartier": "Almadies",
        "type_bien": "appartement",
        "surface_m2": 90.0,
        "nb_pieces": 4,
        "nb_chambres": 2,
        "meuble": True,
        "equipements": ["climatisation", "parking"],
    }

    result = predict_price(bundle, listing)

    assert isinstance(result, float)
    assert result == 321000.0
