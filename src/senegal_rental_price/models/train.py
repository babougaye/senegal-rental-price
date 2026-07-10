"""Model training entry point, configured with Hydra and tracked with MLflow.

Example
-------
    python -m senegal_rental_price.models.train model=xgboost model.params.max_depth=8
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol, cast

import hydra
import joblib
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from omegaconf import DictConfig, OmegaConf
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from senegal_rental_price.data.preprocessing import clean_dataset
from senegal_rental_price.features.build_features import build_features
from senegal_rental_price.utils.logger import get_logger

logger = get_logger(__name__)


class TrainableRegressor(Protocol):
    """Structural type for any fittable, predictable scikit-learn-like regressor."""

    def fit(self, x: pd.DataFrame, y: pd.Series) -> object: ...

    def predict(self, x: pd.DataFrame) -> object: ...


def build_model(model_cfg: DictConfig) -> TrainableRegressor:
    """Instantiate a regressor from its Hydra configuration."""
    params = dict(model_cfg.params)
    name = str(model_cfg.name)

    if name == "random_forest":
        rf_model: TrainableRegressor = RandomForestRegressor(**params)
        return rf_model
    if name == "ridge":
        ridge_model: TrainableRegressor = Ridge(**params)
        return ridge_model
    if name == "xgboost":
        from xgboost import XGBRegressor

        xgb_model: TrainableRegressor = XGBRegressor(**params)
        return xgb_model
    raise ValueError(f"Unknown model name: {name}")


def load_dataset(path: str) -> pd.DataFrame:
    """Load the raw CSV dataset from disk."""
    df = pd.read_csv(path)
    logger.info("Loaded dataset from %s with shape %s", path, df.shape)
    return df


def prepare_training_data(df: pd.DataFrame, target: str) -> tuple[pd.DataFrame, pd.Series]:
    """Run cleaning + feature engineering and split features from target."""
    df = clean_dataset(df)
    df = build_features(df)
    y = df[target]
    x = df.drop(columns=[target])
    return x, y


def evaluate(y_true: pd.Series, y_pred: NDArray[np.float64]) -> dict[str, float]:
    """Compute regression metrics."""
    rmse = float(mean_squared_error(y_true, y_pred) ** 0.5)
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    return {"rmse": rmse, "mae": mae, "r2": r2}


@hydra.main(version_base=None, config_path="../../../conf", config_name="config")
def main(cfg: DictConfig) -> None:
    """Train a model, log it to MLflow and serialize it to disk."""
    logger.info("Resolved configuration:\n%s", OmegaConf.to_yaml(cfg))

    mlflow.set_tracking_uri(cfg.mlflow.tracking_uri)
    mlflow.set_experiment(cfg.mlflow.experiment_name)

    df = load_dataset(cfg.data.raw_path)
    x, y = prepare_training_data(df, target=cfg.data.target)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=cfg.data.test_size, random_state=cfg.seed
    )

    model = build_model(cfg.model)
    feature_columns = list(x_train.columns)

    with mlflow.start_run(run_name=cfg.model.name):
        mlflow.log_params({f"model__{k}": v for k, v in cfg.model.params.items()})
        mlflow.log_param("model_name", cfg.model.name)
        mlflow.log_param("n_features", len(feature_columns))

        model.fit(x_train, y_train)
        y_pred = cast(NDArray[np.float64], model.predict(x_test))
        metrics = evaluate(y_test, y_pred)
        mlflow.log_metrics(metrics)

        logger.info("Model=%s metrics=%s", cfg.model.name, metrics)

        output_dir = Path(cfg.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        model_path = output_dir / f"{cfg.model.name}.joblib"
        joblib.dump(model, model_path)

        metadata = {
            "model_name": cfg.model.name,
            "trained_at": datetime.now(UTC).isoformat(),
            "metrics": metrics,
            "feature_columns": feature_columns,
            "params": dict(cfg.model.params),
        }
        metadata_path = output_dir / f"{cfg.model.name}.metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2))

        mlflow.log_artifact(str(model_path))
        mlflow.log_artifact(str(metadata_path))
        if cfg.model.name == "xgboost":
            mlflow.xgboost.log_model(model, artifact_path="model")
        else:
            mlflow.sklearn.log_model(model, artifact_path="model")

        logger.info("Saved model to %s", model_path)


if __name__ == "__main__":
    main()
