"""FastAPI application exposing the Senegal rental price prediction service."""

from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies import get_model_bundle
from api.schemas import (
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse,
    RentalFeatures,
)
from senegal_rental_price.models.predict import ModelBundle, predict_price
from senegal_rental_price.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Senegal Rental Price API",
    description=(
        "Service de prédiction du prix de location d'un bien immobilier "
        "au Sénégal, à partir de ses caractéristiques."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
def health() -> HealthResponse:
    """Check that the service is up."""
    return HealthResponse(status="ok")


@app.get("/model/info", response_model=ModelInfoResponse, tags=["model"])
def model_info(bundle: ModelBundle = Depends(get_model_bundle)) -> ModelInfoResponse:
    """Return metadata about the currently loaded model."""
    metadata = bundle.metadata
    return ModelInfoResponse(
        model_name=metadata["model_name"],
        trained_at=metadata["trained_at"],
        metrics=metadata["metrics"],
        n_features=len(bundle.feature_columns),
    )


@app.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(
    features: RentalFeatures, bundle: ModelBundle = Depends(get_model_bundle)
) -> PredictionResponse:
    """Predict the monthly rent price (FCFA) for a given listing."""
    listing = features.model_dump(mode="json")
    estimated_price = predict_price(bundle, listing)
    logger.info("Prediction served: ville=%s -> %.0f FCFA", features.ville, estimated_price)
    return PredictionResponse(
        prix_loyer_mensuel_estime=round(estimated_price, -2),
        model_version=bundle.metadata["model_name"],
    )
