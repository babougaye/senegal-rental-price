"""Generate a realistic synthetic dataset of rental listings in Senegal.

This script implements option 2 of the project specification: a synthetic
dataset with a price distribution that is coherent with city, neighborhood
and surface (Dakar more expensive than secondary cities, premium
neighborhoods such as Almadies/Mermoz/Plateau, etc.).

Usage
-----
    python -m senegal_rental_price.data.generate_synthetic_data \
        --n-rows 4000 --output data/raw/locations_senegal.csv
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np
import pandas as pd

from senegal_rental_price.utils.logger import get_logger

logger = get_logger(__name__)

EQUIPEMENTS_POOL: list[str] = [
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

TYPES_BIEN: list[str] = ["appartement", "maison", "studio", "villa"]

# Base monthly price per m2 (FCFA), by city.
VILLE_BASE_PRIX_M2: dict[str, float] = {
    "Dakar": 6500.0,
    "Thiès": 2800.0,
    "Saint-Louis": 2600.0,
    "Mbour": 3200.0,
    "Saly": 4200.0,
}

# Dakar neighborhoods with a price multiplier relative to the city base.
QUARTIERS_DAKAR: dict[str, float] = {
    "Almadies": 1.9,
    "Mermoz": 1.5,
    "Plateau": 1.6,
    "Ngor": 1.7,
    "Sacré-Coeur": 1.3,
    "Ouakam": 1.2,
    "Yoff": 1.1,
    "Liberté": 1.0,
    "Parcelles Assainies": 0.75,
    "Grand Yoff": 0.65,
}

TYPE_BIEN_MULTIPLIER: dict[str, float] = {
    "studio": 0.85,
    "appartement": 1.0,
    "maison": 1.1,
    "villa": 1.45,
}

EQUIPEMENT_PRICE_BONUS: dict[str, float] = {
    "climatisation": 0.06,
    "piscine": 0.20,
    "gardiennage": 0.05,
    "parking": 0.04,
    "groupe_electrogene": 0.05,
    "ascenseur": 0.03,
    "jardin": 0.05,
    "fibre_internet": 0.02,
    "cuisine_equipee": 0.04,
    "balcon": 0.02,
}


@dataclass(frozen=True)
class GenerationConfig:
    """Parameters controlling the synthetic data generation."""

    n_rows: int
    seed: int
    villes: tuple[str, ...] = tuple(VILLE_BASE_PRIX_M2.keys())


def _sample_quartier(rng: np.random.Generator, ville: str) -> str | None:
    """Sample a neighborhood for Dakar, ``None`` otherwise."""
    if ville != "Dakar":
        return None
    noms = list(QUARTIERS_DAKAR.keys())
    return str(rng.choice(noms))


def _sample_equipements(rng: np.random.Generator) -> list[str]:
    """Sample a random subset of amenities."""
    k = int(rng.integers(0, 6))
    if k == 0:
        return []
    return list(rng.choice(EQUIPEMENTS_POOL, size=k, replace=False))


def generate_listing_row(rng: np.random.Generator) -> dict[str, object]:
    """Generate a single synthetic rental listing.

    The price is derived from city, neighborhood, surface, property type and
    amenities, then perturbed with multiplicative noise to emulate market
    variability.
    """
    ville = str(rng.choice(list(VILLE_BASE_PRIX_M2.keys())))
    quartier = _sample_quartier(rng, ville)
    type_bien = str(rng.choice(TYPES_BIEN))

    surface_m2 = float(np.clip(rng.normal(loc=85, scale=40), 18, 600))
    nb_pieces = int(np.clip(round(surface_m2 / 22 + rng.normal(0, 0.8)), 1, 12))
    nb_chambres = int(np.clip(nb_pieces - rng.integers(1, 3), 0, nb_pieces))
    meuble = bool(rng.random() < 0.35)
    equipements = _sample_equipements(rng)

    base_prix_m2 = VILLE_BASE_PRIX_M2[ville]
    quartier_mult = QUARTIERS_DAKAR.get(quartier, 1.0) if quartier else 1.0
    type_mult = TYPE_BIEN_MULTIPLIER[type_bien]
    equip_bonus = 1.0 + sum(EQUIPEMENT_PRICE_BONUS.get(e, 0.0) for e in equipements)
    meuble_bonus = 1.12 if meuble else 1.0

    prix_m2 = base_prix_m2 * quartier_mult * type_mult * equip_bonus * meuble_bonus
    noise = float(rng.normal(loc=1.0, scale=0.12))
    prix_loyer_mensuel = max(30_000.0, round(surface_m2 * prix_m2 * noise, -3))

    return {
        "ville": ville,
        "quartier": quartier,
        "type_bien": type_bien,
        "surface_m2": round(surface_m2, 1),
        "nb_pieces": nb_pieces,
        "nb_chambres": nb_chambres,
        "meuble": meuble,
        "equipements": "|".join(equipements),
        "prix_loyer_mensuel": prix_loyer_mensuel,
    }


def generate_dataset(config: GenerationConfig) -> pd.DataFrame:
    """Generate a full synthetic dataset as a DataFrame."""
    rng = np.random.default_rng(config.seed)
    rows = [generate_listing_row(rng) for _ in range(config.n_rows)]
    df = pd.DataFrame(rows)

    # Inject a small, realistic proportion of missing values to make the
    # preprocessing pipeline meaningful.
    for col in ["nb_chambres", "equipements"]:
        mask = rng.random(len(df)) < 0.03
        df.loc[mask, col] = np.nan

    logger.info("Generated synthetic dataset with %d rows", len(df))
    return df


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-rows", type=int, default=4000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str, default="data/raw/locations_senegal.csv")
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = _parse_args()
    config = GenerationConfig(n_rows=args.n_rows, seed=args.seed)
    df = generate_dataset(config)
    df.to_csv(args.output, index=False)
    logger.info("Saved dataset to %s", args.output)


if __name__ == "__main__":
    main()
