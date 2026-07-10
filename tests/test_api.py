from __future__ import annotations

from fastapi.testclient import TestClient

from api.dependencies import get_model_bundle
from api.main import app
from senegal_rental_price.models.predict import ModelBundle


class FakeModel:
    def predict(self, x: object) -> list[float]:
        return [275000.0]


def _fake_bundle() -> ModelBundle:
    return ModelBundle(
        model=FakeModel(),
        feature_columns=["surface_m2", "nb_pieces", "ville_Dakar"],
        metadata={
            "model_name": "fake_model",
            "trained_at": "2026-01-01T00:00:00+00:00",
            "metrics": {"rmse": 1.0, "mae": 1.0, "r2": 0.9},
        },
    )


app.dependency_overrides[get_model_bundle] = _fake_bundle
client = TestClient(app)

VALID_PAYLOAD = {
    "ville": "Dakar",
    "quartier": "Almadies",
    "type_bien": "appartement",
    "surface_m2": 90,
    "nb_pieces": 4,
    "nb_chambres": 2,
    "meuble": True,
    "equipements": ["climatisation", "parking"],
}


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_model_info_endpoint() -> None:
    response = client.get("/model/info")
    assert response.status_code == 200
    body = response.json()
    assert body["model_name"] == "fake_model"
    assert "rmse" in body["metrics"]


def test_predict_endpoint_valid_payload() -> None:
    response = client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["devise"] == "FCFA"
    assert body["model_version"] == "fake_model"
    assert body["prix_loyer_mensuel_estime"] > 0


def test_predict_endpoint_rejects_negative_surface() -> None:
    payload = {**VALID_PAYLOAD, "surface_m2": -10}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_endpoint_rejects_unknown_ville() -> None:
    payload = {**VALID_PAYLOAD, "ville": "Paris"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_endpoint_rejects_missing_required_field() -> None:
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "surface_m2"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
