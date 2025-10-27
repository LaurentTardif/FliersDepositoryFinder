# 🚀 Configuration GitHub Actions - CI/CD

Ce projet utilise **GitHub Actions** pour automatiser les tests et la vérification de la qualité du code à chaque commit.

## 📋 Workflow automatique

À chaque `push` ou `pull request` sur la branche `main`, GitHub Actions exécute automatiquement :

### ✅ Tests et validations
- **Tests unitaires** : Exécution complète des 31 tests
- **Vérification syntaxe** : Détection des erreurs critiques (flake8)
- **Style de code** : Vérification du formatage (Black)
- **Organisation imports** : Validation de l'ordre des imports (isort)
- **Types statiques** : Analyse des annotations de types (mypy)
- **Couverture de tests** : Mesure du pourcentage de code testé

### 🌍 Environnements testés
- **Python** : 3.9, 3.10, 3.11, 3.12
- **OS** : Ubuntu (CI) + Windows (validation)

## 🛠️ Scripts locaux disponibles

### Avant de committer :
```bash
# Vérifier la qualité du code
python check_quality.py

# Formater automatiquement le code
python format_code.py

# Lancer tous les tests
python tests/run_all_tests.py
```

## 📊 Status Badge

Une fois configuré, vous pouvez ajouter ce badge dans votre README :

```markdown
![CI Status](https://github.com/LaurentTardif/FliersDepositoryFinder/workflows/CI%20-%20Tests%20et%20Qualité%20du%20Code/badge.svg)
```

## 🔧 Configuration des outils

### Fichiers de configuration :
- `.flake8` : Règles de linting
- `pyproject.toml` : Configuration Black, isort, mypy
- `requirements.txt` : Dépendances du projet

### Règles appliquées :
- **Longueur ligne** : 127 caractères max
- **Complexité** : Max 10 (McCabe)
- **Style** : Black formatter
- **Imports** : Triés avec isort
- **Encodage** : UTF-8 partout

## 🚫 Fichiers ignorés

Le workflow ignore automatiquement :
- `__pycache__/`
- `.venv/`, `venv/`, `env/`
- `temp_*` (fichiers temporaires)
- `.git/`

## 💡 Bonnes pratiques

1. **Formatez toujours avant de committer** : `python format_code.py`
2. **Vérifiez localement** : `python check_quality.py`
3. **Gardez les tests à jour** : 31 tests actuellement
4. **Suivez les conventions** : PEP 8, annotations de types recommandées

## 🛡️ Protection des branches

Recommandation : Configurez la protection de branche `main` pour :
- Exiger que les CI checks passent avant merge
- Exiger une revue de code
- Interdire les push directs sur main

## 📈 Métriques de qualité

Objectifs du projet :
- ✅ **Tests** : 100% de passage (31/31)
- ✅ **Couverture** : Mesurée automatiquement
- ✅ **Style** : Conforme Black + flake8
- ✅ **Imports** : Organisés avec isort
- ⚠️ **Types** : En amélioration continue (mypy)