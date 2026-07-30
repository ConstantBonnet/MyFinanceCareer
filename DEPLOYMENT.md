# Deploiement Streamlit Community Cloud

Ce projet est pret a etre deploie sur Streamlit Community Cloud.

## Structure attendue

```text
Career Space/
├── app.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```

## Parametres de deploiement

- Plateforme: Streamlit Community Cloud
- Repository: depot GitHub contenant ce dossier
- Branch: `main`
- Main file path: `app.py`
- Python: selectionner une version supportee dans les parametres avances, idealement Python 3.12
- Secrets: aucun secret requis pour cette version

## Etapes

0. Verifier le projet avec `python scripts/verify_release.py`.
1. Creer un depot GitHub, par exemple `mfc-my-finance-career`.
2. Envoyer ce dossier dans le depot.
3. Ouvrir Streamlit Community Cloud.
4. Cliquer sur `Create app`.
5. Selectionner le depot, la branche et `app.py`.
6. Deployer.

## Notes importantes

- `mfc_data.sqlite3` est ignore volontairement: la base locale peut contenir des donnees personnelles.
- Au premier lancement cloud, l'application recree automatiquement une base SQLite avec des donnees de demonstration.
- La persistence SQLite sur Streamlit Cloud est adaptee a une demo ou un MVP personnel, pas a un produit multi-utilisateur.
- Pour une version publique avec comptes utilisateurs, remplacer SQLite local par une base geree et ajouter une authentification.
