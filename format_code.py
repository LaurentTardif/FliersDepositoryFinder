#!/usr/bin/env python3
"""
Script pour formater automatiquement le code Python du projet
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔧 {description}...")
    print("-" * 50)

    try:
        result = subprocess.run(command, shell=True, text=True)

        if result.returncode == 0:
            print(f"✅ Succès: {description}")
        else:
            print(f"⚠️ Avertissement: {description}")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False


def main():
    """Fonction principale"""
    print("🎨 Formatage automatique du code - FliersDepositoryFinder")
    print("=" * 60)

    # Vérifier que nous sommes dans le bon dossier
    if not Path("tests/run_all_tests.py").exists():
        print("❌ Erreur: Veuillez exécuter ce script depuis la racine du projet")
        sys.exit(1)

    print("🚀 Formatage en cours...")

    # 1. Formatage avec Black
    run_command("python -m black .", "Formatage du code avec Black")

    # 2. Organisation des imports avec isort
    run_command("python -m isort .", "Organisation des imports avec isort")

    print("\n" + "=" * 60)
    print("🎉 Formatage terminé ! Votre code est maintenant bien formaté.")
    print("\n💡 Conseils :")
    print("1. Vérifiez les changements avec: git diff")
    print("2. Lancez les tests avec: python check_quality.py")
    print("3. Committez vos changements si tout est OK")


if __name__ == "__main__":
    main()
