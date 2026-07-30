# Publication GitHub

Le depot cible est:

```text
https://github.com/ConstantBonnet/MyFinanceCareer.git
```

Le projet local est deja initialise avec Git et le remote `origin`.

## Option recommandee: GitHub Desktop

1. Ouvrir GitHub Desktop.
2. Ajouter le dossier local `Career Space`.
3. Verifier que le remote est `ConstantBonnet/MyFinanceCareer`.
4. Publier ou pousser la branche `main`.

## Option terminal avec token GitHub

1. Creer un Personal Access Token GitHub avec acces au depot `ConstantBonnet/MyFinanceCareer`.
2. Repasser le remote en HTTPS:

```bash
git remote set-url origin https://github.com/ConstantBonnet/MyFinanceCareer.git
```

3. Pousser:

```bash
git push -u origin main
```

Quand Git demande le mot de passe, utiliser le token GitHub comme mot de passe.

## Option terminal avec SSH

1. Ajouter une cle SSH a ton compte GitHub.
2. Utiliser le remote SSH:

```bash
git remote set-url origin git@github.com:ConstantBonnet/MyFinanceCareer.git
git push -u origin main
```

## Apres le push

Dans Streamlit Community Cloud:

- Repository: `ConstantBonnet/MyFinanceCareer`
- Branch: `main`
- Main file path: `app.py`
- Secrets: aucun
