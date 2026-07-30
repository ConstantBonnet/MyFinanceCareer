# MFC - My Finance Career

MFC est une application Streamlit pour aider un etudiant en finance a organiser sa recherche de stages ou premiers emplois depuis un espace unique.

## Fonctionnalites livrees

- Tableau de bord avec echeances, actions prioritaires et progression.
- Suivi des candidatures en Kanban et en liste filtrable.
- Bibliotheque de liens vers CV, lettres, guides, cours et ressources.
- Calendrier interne pour deadlines, entretiens, tests, relances et networking.
- Objectifs avec progression et prochaines etapes.
- Contacts professionnels sous forme de mini-CRM.
- Statistiques utiles sur le pipeline.
- Export CSV des donnees.

## Structure

- `app.py`: application Streamlit principale.
- `requirements.txt`: dependances Python pour Streamlit Cloud.
- `.streamlit/config.toml`: theme et configuration Streamlit.
- `docs/PRODUCT_REFERENCE.md`: decisions produit et limites du MVP.
- `DEPLOYMENT.md`: guide de mise en ligne sur Streamlit Community Cloud.
- `GITHUB_PUSH.md`: options pour pousser le depot vers GitHub.

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

L'application cree automatiquement `mfc_data.sqlite3` au premier lancement. Ce fichier est ignore par Git pour eviter de publier des donnees personnelles.

## Verifier avant publication

```bash
python scripts/verify_release.py
```

Ce controle verifie les fichiers attendus pour Streamlit Cloud, les dependances, la syntaxe et le chargement des donnees de demonstration.

## Deployer sur Streamlit Community Cloud

1. Publier ce dossier dans un depot GitHub.
2. Ouvrir Streamlit Community Cloud.
3. Creer une nouvelle app depuis le depot.
4. Choisir `app.py` comme fichier principal.
5. Deployer.

Voir `DEPLOYMENT.md` pour les parametres exacts.

## Limite importante

Cette version est adaptee a une demo ou un MVP individuel. Pour une version multi-utilisateur, il faudra remplacer SQLite local par une base geree et ajouter l'authentification.
