export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const VILLES = ["Dakar", "Thiès", "Saint-Louis", "Mbour", "Saly"];

// Prix de référence au m² par ville (FCFA/mois), à titre indicatif pour la
// comparaison affichée dans la carte de résultat. Ordre de grandeur cohérent
// avec la génération des données synthétiques du projet (voir
// generate_synthetic_data.py), mais non recalculé dynamiquement.
export const VILLE_PRIX_M2_REFERENCE = {
  Dakar: 6500,
  Thiès: 2800,
  "Saint-Louis": 2600,
  Mbour: 3200,
  Saly: 4200,
};

export const TYPES_BIEN = [
  { value: "appartement", label: "Appartement" },
  { value: "maison", label: "Maison" },
  { value: "studio", label: "Studio" },
  { value: "villa", label: "Villa" },
];

export const EQUIPEMENTS = [
  { value: "climatisation", label: "Climatisation" },
  { value: "piscine", label: "Piscine" },
  { value: "gardiennage", label: "Gardiennage" },
  { value: "parking", label: "Parking" },
  { value: "groupe_electrogene", label: "Groupe électrogène" },
  { value: "ascenseur", label: "Ascenseur" },
  { value: "jardin", label: "Jardin" },
  { value: "fibre_internet", label: "Fibre internet" },
  { value: "cuisine_equipee", label: "Cuisine équipée" },
  { value: "balcon", label: "Balcon" },
];

/**
 * Call the /predict endpoint of the rental price API.
 * @param {object} payload - matches the RentalFeatures Pydantic schema
 * @returns {Promise<{prix_loyer_mensuel_estime: number, devise: string, model_version: string}>}
 */
export async function predictPrice(payload) {
  const response = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const error = new Error("La validation du formulaire a échoué.");
    error.status = response.status;
    error.details = body?.detail ?? null;
    throw error;
  }

  return response.json();
}

export async function fetchHealth() {
  const response = await fetch(`${API_URL}/health`);
  if (!response.ok) throw new Error("API indisponible");
  return response.json();
}
