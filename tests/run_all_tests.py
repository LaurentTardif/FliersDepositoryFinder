#!/usr/bin/env python3
"""
Script pour exécuter tous les tests du projet FliersDepositoryFinder
"""

import unittest
import sys
from pathlib import Path

def run_all_tests():
    """Exécute tous les tests du projet"""

    # Chemin vers le dossier de tests
    tests_dir = Path(__file__).parent

    # Découverte automatique des tests
    loader = unittest.TestLoader()
    suite = loader.discover(str(tests_dir), pattern='test_*.py')

    # Exécution des tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Code de sortie basé sur le succès des tests
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)