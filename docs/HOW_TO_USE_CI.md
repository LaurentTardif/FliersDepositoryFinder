#!/bin/bash
# Exemple de commandes pour utiliser la CI/CD localement

echo "🚀 Guide d'utilisation de la CI/CD - FliersDepositoryFinder"
echo "============================================================="

echo ""
echo "📋 Étapes recommandées avant de committer :"
echo ""

echo "1️⃣ Formater le code automatiquement"
echo "   python format_code.py"
echo ""

echo "2️⃣ Vérifier la qualité du code"
echo "   python check_quality.py"
echo ""

echo "3️⃣ Lancer tous les tests"
echo "   python tests/run_all_tests.py"
echo ""

echo "4️⃣ Vérifier l'état de Git"
echo "   git status"
echo "   git diff"
echo ""

echo "5️⃣ Committer les changements"
echo "   git add ."
echo "   git commit -m 'feat: votre message de commit'"
echo "   git push"
echo ""

echo "🔍 Outils disponibles :"
echo ""

echo "▶ Formatage automatique :"
echo "  python format_code.py"
echo ""

echo "▶ Vérification complète :"
echo "  python check_quality.py"
echo ""

echo "▶ Tests par module :"
echo "  python -m unittest tests.tests_filters.test_filters -v"
echo "  python -m unittest tests.tests_maj_historique.test_maj_historique -v"
echo "  python -m unittest tests.tests_normalisation_metiers.test_normalise_metiers -v"
echo "  python -m unittest tests.tests_recherche_entreprises.test_recherche_entreprises -v"
echo "  python -m unittest tests.tests_supprime_doublons.test_supprime_doublons -v"
echo ""

echo "▶ Outils individuels :"
echo "  python -m flake8 . --statistics"
echo "  python -m black --check ."
echo "  python -m isort --check-only ."
echo "  python -m mypy . --ignore-missing-imports"
echo ""

echo "🎯 Résultats attendus :"
echo "✅ 31 tests passent (100%)"
echo "✅ Code formaté selon Black"
echo "✅ Imports organisés avec isort"
echo "✅ Pas d'erreurs critiques flake8"
echo "⚠️ Avertissements mypy (non critiques)"
echo ""

echo "📊 Structure de qualité :"
echo "  - Longueur de ligne : 127 caractères max"
echo "  - Style : Black formatter"
echo "  - Linting : flake8 (PEP 8)"
echo "  - Tests : unittest avec 31 tests"
echo "  - Couverture : mesurée automatiquement"
echo ""

echo "🚫 Fichiers ignorés par Git :"
echo "  - __pycache__/"
echo "  - .venv/, venv/, env/"
echo "  - temp_* (fichiers temporaires)"
echo "  - .coverage, coverage.xml"
echo ""

echo "🔗 GitHub Actions :"
echo "  - Se déclenche à chaque push sur main"
echo "  - Teste Python 3.9, 3.10, 3.11, 3.12"
echo "  - Ubuntu + Windows"
echo "  - Badge de statut dans README.md"
echo ""

echo "💡 Astuce : Configurez votre IDE pour :"
echo "  - Formater avec Black au save"
echo "  - Organiser les imports avec isort"
echo "  - Linter avec flake8"
echo "  - Type checking avec mypy"