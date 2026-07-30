# My Finance Career

My Finance Career est une application Streamlit qui aide un etudiant en finance a piloter sa recherche de stages et premiers emplois depuis un espace unique, clair et actionnable.

## Fonctionnalites

- Accueil avec priorites du jour, traction, retards et pipeline actif.
- Pipeline de candidatures avec focus list, filtres, table exploitable et mise a jour rapide.
- Agenda pour deadlines, entretiens, tests, relances et networking, avec marquage termine.
- Reseau professionnel sous forme de bibliotheque de contacts, classee par metier, statut, priorite et prochaine relance.
- Import Excel/CSV d'une fiche de networking existante avec classement metier automatique de base.
- Ressources classees par categorie, domaine et tags.
- Objectifs avec progression et prochaine etape modifiable.
- Analyse du pipeline par statut, domaine, traction et offres.
- Export CSV des donnees.
- Logo et navigation horizontale integres pour une presentation plus proche d'une vraie app.

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

Cette version utilise SQLite local pour une demo ou un MVP individuel. Pour une version multi-utilisateur, il faudra ajouter une base geree, une authentification et une separation des donnees par utilisateur.
