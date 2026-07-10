# Front React (bonus) — Sénégal Immo

Alternative au front Streamlit (`frontend/streamlit_app.py`, livrable principal),
proposée en bonus comme le permet le sujet ("une application React/Vue plus
élaborée est valorisée en bonus si le temps le permet").

Stack : Vite + React 19 + Tailwind CSS v4 (aucun compilateur externe requis,
uniquement les classes utilitaires de base + un thème de design tokens custom
dans `src/index.css`).

## Développement local

```bash
cd frontend/react-app
npm install
cp .env.example .env          # ajuster VITE_API_URL si besoin
npm run dev
```

L'application est servie sur http://localhost:5173 et appelle l'API définie
par `VITE_API_URL` (http://localhost:8000 par défaut — assurez-vous que l'API
FastAPI tourne, voir le README à la racine du projet).

## Build de production

```bash
npm run build      # génère dist/
npm run preview    # sert le build localement pour vérification
```

## Lancer avec Docker

Le service `frontend-react` est défini dans `docker/docker-compose.yml` sous
le profil optionnel `react`, pour ne pas interférer avec le service
`frontend` (Streamlit) qui reste le livrable par défaut :

```bash
docker compose -f docker/docker-compose.yml --profile react up --build
```

L'application est alors servie par Nginx sur http://localhost:5174.

## Structure

```
react-app/
├── src/
│   ├── api.js                 # client API + constantes (villes, équipements...)
│   ├── useCountUp.js          # hook d'animation du prix (respecte prefers-reduced-motion)
│   ├── App.jsx                # état du formulaire, validation, appel API
│   ├── index.css              # thème (couleurs, typographies) via @theme Tailwind v4
│   └── components/
│       ├── BrandPanel.jsx     # panneau de marque (gauche)
│       ├── Skyline.jsx        # silhouette SVG de Dakar
│       ├── RentalForm.jsx     # formulaire des caractéristiques du bien
│       └── ResultCard.jsx     # carte de résultat ("fiche d'estimation")
└── Dockerfile                 # build multi-stage, servi par Nginx non-root
```

## Notes de conception

- Le payload envoyé à `/predict` respecte exactement le schéma Pydantic
  `RentalFeatures` de l'API (mêmes bornes de validation côté client, pour un
  retour d'erreur immédiat avant l'appel réseau).
- Les erreurs 422 de l'API sont interceptées et affichées avec le détail
  renvoyé par Pydantic.
- La comparaison au "prix de référence" affichée dans la fiche d'estimation
  est indicative (calculée côté client à partir d'un prix au m² par ville),
  elle ne provient pas du modèle.
