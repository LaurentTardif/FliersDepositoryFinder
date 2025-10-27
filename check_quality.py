#!/usr/bin/env python3
"""
Script pour vérifier la qualité du code localement avant de pousser sur GitHub
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description, critical=True):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔍 {description}...")
    print("-" * 50)

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode != 0:
            print(f"❌ Échec: {description}")
            if critical:
                return False
            else:
                print("⚠️ Avertissement (non critique)")
        else:
            print(f"✅ Succès: {description}")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False


def main():
    """Fonction principale"""
    print("🚀 Vérification de la qualité du code - FliersDepositoryFinder")
    print("=" * 60)

    # Vérifier que nous sommes dans le bon dossier
    if not Path("tests/run_all_tests.py").exists():
        print("❌ Erreur: Veuillez exécuter ce script depuis la racine du projet")
        sys.exit(1)

    # Définir l'encodage
    os.environ["PYTHONIOENCODING"] = "utf-8"

    all_passed = True

    # 1. Tests unitaires
    if not run_command("python tests/run_all_tests.py", "Tests unitaires"):
        all_passed = False

    # 2. Linting avec flake8
    if not run_command(
        "python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
        "Vérification syntaxe (flake8 - critique)",
    ):
        all_passed = False

    # 3. Avertissements flake8 (non critique)
    run_command(
        "python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics",
        "Vérification style (flake8 - avertissements)",
        critical=False,
    )

    # 4. Formatage avec Black
    run_command("python -m black --check --diff .", "Vérification formatage (Black)", critical=False)

    # 5. Organisation des imports
    run_command("python -m isort --check-only --diff .", "Vérification imports (isort)", critical=False)

    # 6. Vérification des types (non critique)
    run_command("python -m mypy . --ignore-missing-imports", "Vérification types (mypy)", critical=False)  # Résumé final
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 Tous les tests critiques sont passés ! Prêt pour le commit.")
        sys.exit(0)
    else:
        print("❌ Certains tests critiques ont échoué. Veuillez corriger avant de committer.")
        sys.exit(1)


if __name__ == "__main__":
    main()
