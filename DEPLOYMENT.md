# Deploiement Streamlit Community Cloud

## Parametres

- Repository: `ConstantBonnet/MyFinanceCareer`
- Branch: `main`
- Main file path: `app.py`
- Python: version supportee par Streamlit Cloud, idealement Python 3.12
- Secrets: aucun

## Checklist

1. Verifier le projet avec `python scripts/verify_release.py`.
2. Verifier que GitHub contient `app.py`, `requirements.txt`, `README.md` et `.streamlit/config.toml`.
3. Verifier que GitHub ne contient pas `.DS_Store` ni `mfc_data.sqlite3`.
4. Deployer depuis Streamlit Community Cloud.

## Limite

La persistence SQLite convient a une demo ou un usage personnel. Pour une application publique multi-utilisateur, remplacer SQLite local par une base geree et ajouter une authentification.
