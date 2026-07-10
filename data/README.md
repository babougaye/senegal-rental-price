# Données — provenance et description

## Origine

Ce projet utilise un **jeu de données synthétique** (option 2 du sujet), généré par
`src/senegal_rental_price/data/generate_synthetic_data.py`. Ce choix a été fait pour
garantir la reproductibilité du projet sans dépendre de la disponibilité ou des
conditions d'utilisation de sites d'annonces tiers.

La génération applique une distribution de prix cohérente avec le marché sénégalais :

- **Prix de base au m²** différencié par ville (Dakar > Saly > Mbour > Thiès ≈ Saint-Louis).
- **Prime de quartier** pour Dakar (Almadies, Ngor et Plateau en tête, Grand Yoff et
  Parcelles Assainies en bas de fourchette).
- **Multiplicateur par type de bien** (villa > maison > appartement > studio).
- **Bonus d'équipements** (piscine, climatisation, gardiennage...) et **prime au meublé**.
- **Bruit multiplicatif** pour simuler la variabilité réelle du marché.
- **Valeurs manquantes injectées** (≈3 % sur `nb_chambres` et `equipements`) pour rendre
  le pipeline de nettoyage pertinent à tester.

## Régénérer le jeu de données

```bash
python -m senegal_rental_price.data.generate_synthetic_data \
    --n-rows 4000 --seed 42 --output data/raw/locations_senegal.csv
```

## Variables

| Variable             | Description                                      |
|-----------------------|--------------------------------------------------|
| `ville`                | Ville ou commune du bien                          |
| `quartier`             | Quartier (Dakar uniquement, sinon vide)           |
| `type_bien`            | appartement, maison, studio, villa                |
| `surface_m2`           | Surface en m²                                     |
| `nb_pieces`            | Nombre de pièces                                  |
| `nb_chambres`          | Nombre de chambres                                |
| `meuble`               | Meublé ou non (booléen)                           |
| `equipements`          | Équipements séparés par `\|`                      |
| `prix_loyer_mensuel`   | Variable cible, en FCFA                           |

## Fichiers

- `data/raw/` : données brutes générées, **non versionnées** (voir `.gitignore`).
- `data/processed/` : données nettoyées produites par le pipeline de prétraitement.

Le notebook `notebooks/01_exploration.ipynb` documente l'analyse exploratoire de ce
jeu de données (distributions, corrélations, valeurs manquantes).
