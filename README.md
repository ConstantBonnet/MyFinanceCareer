# MFC - My Finance Career

MFC est une application Streamlit qui aide un etudiant en finance a organiser sa recherche de stages et premiers emplois depuis un espace unique.

## Fonctionnalites

- Tableau de bord avec actions prioritaires, echeances et progression.
- Pipeline de candidatures avec Kanban, liste, filtres et mise a jour.
- Bibliotheque de liens vers CV, lettres, guides, cours et ressources.
- Calendrier interne pour deadlines, entretiens, tests, relances et networking.
- Objectifs avec progression, statut et prochaine etape.
- Contacts professionnels sous forme de mini-CRM.
- Statistiques utiles sur le pipeline.
- Export CSV des donnees.

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Verifier avant publication

```bash
python scripts/verify_release.py
```

## Deployer sur Streamlit Community Cloud

- Repository: `ConstantBonnet/MyFinanceCareer`
- Branch: `main`
- Main file path: `app.py`
- Secrets: aucun

Cette version utilise SQLite local pour une demo ou un MVP individuel. Pour une version multi-utilisateur, il faudra ajouter une base geree et une authentification.
