"""Streamlit front-end calling the rental price prediction API."""

from __future__ import annotations

import os

import requests
import streamlit as st

API_URL = os.environ.get("SRP_API_URL", "http://localhost:8000")

VILLES = ["Dakar", "Thiès", "Saint-Louis", "Mbour", "Saly"]
TYPES_BIEN = ["appartement", "maison", "studio", "villa"]
EQUIPEMENTS = [
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

st.set_page_config(page_title="Prix de location - Sénégal", page_icon="🏠")
st.title("🏠 Estimation du prix de location au Sénégal")
st.caption("Remplissez les caractéristiques du bien pour obtenir une estimation.")

with st.form("rental_form"):
    col1, col2 = st.columns(2)
    with col1:
        ville = st.selectbox("Ville", VILLES)
        type_bien = st.selectbox("Type de bien", TYPES_BIEN)
        surface_m2 = st.number_input(
            "Surface (m²)", min_value=1.0, max_value=2000.0, value=80.0, step=1.0
        )
        meuble = st.checkbox("Meublé", value=False)
    with col2:
        quartier = st.text_input("Quartier (optionnel, surtout pour Dakar)")
        nb_pieces = st.number_input("Nombre de pièces", min_value=1, max_value=20, value=3, step=1)
        nb_chambres = st.number_input(
            "Nombre de chambres", min_value=0, max_value=15, value=2, step=1
        )

    equipements = st.multiselect("Équipements", EQUIPEMENTS)
    submitted = st.form_submit_button("Estimer le prix")

if submitted:
    payload = {
        "ville": ville,
        "quartier": quartier or None,
        "type_bien": type_bien,
        "surface_m2": surface_m2,
        "nb_pieces": int(nb_pieces),
        "nb_chambres": int(nb_chambres),
        "meuble": meuble,
        "equipements": equipements,
    }
    try:
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.success(
                f"Prix estimé : **{data['prix_loyer_mensuel_estime']:,.0f} "
                f"{data['devise']}** / mois"
            )
            st.caption(f"Modèle utilisé : {data['model_version']}")
        else:
            st.error(f"Erreur de validation ({response.status_code}) : {response.text}")
    except requests.exceptions.RequestException as exc:
        st.error(f"Impossible de contacter l'API ({API_URL}) : {exc}")
