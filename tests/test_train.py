from __future__ import annotations

import pandas as pd
import pytest
from omegaconf import OmegaConf
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge

from senegal_rental_price.models.train import (
    build_model,
    evaluate,
    load_dataset,
    prepare_training_data,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ville": ["Dakar", "Thiès", "Dakar", "Saly"],
            "quartier": ["Almadies", None, "Plateau", None],
            "type_bien": ["appartement", "maison", "studio", "villa"],
            "surface_m2": [90.0, 120.0, 35.0, 200.0],
            "nb_pieces": [4, 5, 1, 8],
            "nb_chambres": [2, 3, 1, 5],
            "meuble": [True, False, True, False],
            "equipements": ["climatisation|parking", "", "piscine", None],
            "prix_loyer_mensuel": [500000.0, 300000.0, 150000.0, 1200000.0],
        }
    )


def test_build_model_random_forest() -> None:
    cfg = OmegaConf.create({"name": "random_forest", "params": {"n_estimators": 10}})
    model = build_model(cfg)
    assert isinstance(model, RandomForestRegressor)


def test_build_model_ridge() -> None:
    cfg = OmegaConf.create({"name": "ridge", "params": {"alpha": 0.5}})
    model = build_model(cfg)
    assert isinstance(model, Ridge)


def test_build_model_xgboost() -> None:
    from xgboost import XGBRegressor

    cfg = OmegaConf.create({"name": "xgboost", "params": {"n_estimators": 10}})
    model = build_model(cfg)
    assert isinstance(model, XGBRegressor)


def test_build_model_unknown_raises() -> None:
    cfg = OmegaConf.create({"name": "unknown_model", "params": {}})
    with pytest.raises(ValueError):
        build_model(cfg)


def test_load_dataset(tmp_path: object) -> None:
    df = _sample_df()
    path = f"{tmp_path}/sample.csv"
    df.to_csv(path, index=False)

    loaded = load_dataset(path)
    assert len(loaded) == len(df)


def test_prepare_training_data_splits_target() -> None:
    df = _sample_df()
    x, y = prepare_training_data(df, target="prix_loyer_mensuel")

    assert "prix_loyer_mensuel" not in x.columns
    assert len(x) == len(y)


def test_evaluate_returns_expected_metric_keys() -> None:
    y_true = pd.Series([100.0, 200.0, 300.0])
    y_pred = pd.Series([110.0, 190.0, 320.0])

    metrics = evaluate(y_true, y_pred)

    assert set(metrics.keys()) == {"rmse", "mae", "r2"}
    assert metrics["rmse"] >= 0
    assert metrics["mae"] >= 0
