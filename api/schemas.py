"""Pydantic schemas (request/response models) for the prediction API."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Ville(str, Enum):
    """Cities supported by the model."""

    dakar = "Dakar"
    thies = "Thiès"
    saint_louis = "Saint-Louis"
    mbour = "Mbour"
    saly = "Saly"


class TypeBien(str, Enum):
    """Property types supported by the model."""

    appartement = "appartement"
    maison = "maison"
    studio = "studio"
    villa = "villa"


class RentalFeatures(BaseModel):
    """Characteristics of a rental listing, as submitted to ``/predict``."""

    ville: Ville = Field(..., description="Ville ou commune du bien")
    quartier: str | None = Field(
        default=None,
        max_length=64,
        description="Quartier (recommandé pour Dakar, optionnel sinon)",
    )
    type_bien: TypeBien = Field(..., description="Type de bien")
    surface_m2: float = Field(..., gt=0, le=2000, description="Surface habitable en mètres carrés")
    nb_pieces: int = Field(..., ge=1, le=20, description="Nombre total de pièces")
    nb_chambres: int = Field(..., ge=0, le=15, description="Nombre de chambres")
    meuble: bool = Field(..., description="Le bien est-il meublé ?")
    equipements: list[str] = Field(
        default_factory=list,
        description="Liste d'équipements (climatisation, piscine, parking...)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ville": "Dakar",
                    "quartier": "Almadies",
                    "type_bien": "appartement",
                    "surface_m2": 90,
                    "nb_pieces": 4,
                    "nb_chambres": 2,
                    "meuble": True,
                    "equipements": ["climatisation", "parking", "gardiennage"],
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """Response payload for ``/predict``."""

    prix_loyer_mensuel_estime: float = Field(..., description="Prix de location mensuel estimé")
    devise: str = Field(default="FCFA", description="Devise du montant estimé")
    model_version: str = Field(..., description="Version/identifiant du modèle utilisé")


class HealthResponse(BaseModel):
    """Response payload for ``/health``."""

    status: str = Field(default="ok", description="État du service")


class ModelInfoResponse(BaseModel):
    """Response payload for ``/model/info``."""

    model_name: str = Field(..., description="Nom du modèle chargé")
    trained_at: str = Field(..., description="Date d'entraînement (ISO 8601)")
    metrics: dict[str, float] = Field(..., description="Métriques de performance")
    n_features: int = Field(..., description="Nombre de features utilisées")
