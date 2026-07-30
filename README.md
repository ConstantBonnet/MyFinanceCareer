# My Finance Career

My Finance Career est une application Streamlit qui aide un etudiant en finance a piloter sa recherche de stages et premiers emplois depuis un espace unique, clair et actionnable.

## Fonctionnalites

- Objectifs sous forme de to-do avec priorite, echeance, statut, progression et prochaine etape.
- Calendrier mensuel avec ajout d'evenements, echeances d'objectifs et rappels reseau.
- Bibliotheque de ressources sous forme de liens externes vers CV, lettres de motivation, preparations techniques, cours et documents Google Drive.
- Reseau professionnel sous forme de bibliotheque de contacts, classee par metier, statut, priorite et prochaine relance.
- Import Excel/CSV d'une fiche de networking existante avec classement metier automatique de base.
- Logo fondu dans le fond et navigation compacte limitee aux fonctions principales.

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
