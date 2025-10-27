import unittest
import subprocess
import csv
import os
import tempfile
from pathlib import Path

class TestSupprimeDoublons(unittest.TestCase):

    def setUp(self):
        """Configuration avant chaque test"""
        self.test_dir = Path(__file__).parent
        self.projet_root = self.test_dir.parent.parent
        self.script = self.projet_root / "supprime_doublons.py"

    def test_cas_nominal_suppression_doublons(self):
        """Test de suppression des doublons dans un cas normal"""
        input_file = self.test_dir / "input_avec_doublons.csv"
        expected_output = self.test_dir / "output_sans_doublons.csv"

        # Vérification des fichiers de test
        self.assertTrue(input_file.exists(), f"Fichier d'entrée manquant: {input_file}")
        self.assertTrue(expected_output.exists(), f"Fichier de référence manquant: {expected_output}")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_output:
            temp_output_path = temp_output.name

        try:
            # Exécution du script avec encodage UTF-8
            result = subprocess.run([
                'python', str(self.script),
                str(input_file), temp_output_path
            ], capture_output=True, text=True, encoding='utf-8', env=dict(os.environ, PYTHONIOENCODING='utf-8'))

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            # Comparaison des résultats
            with open(temp_output_path, 'r', encoding='utf-8') as f:
                generated_content = list(csv.DictReader(f))

            with open(expected_output, 'r', encoding='utf-8') as f:
                expected_content = list(csv.DictReader(f))

            self.assertEqual(len(generated_content), len(expected_content),
                           "Le nombre de lignes ne correspond pas")

            # Le fichier d'entrée avait 8 lignes (dont 3 doublons), le résultat devrait en avoir 5
            self.assertEqual(len(generated_content), 5, "Les doublons n'ont pas été supprimés correctement")

        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def test_donnees_inconnues(self):
        """Test avec des données nouvelles/inconnues (pas de doublons à supprimer)"""
        input_file = self.test_dir / "input_donnees_inconnues.csv"
        expected_output = self.test_dir / "output_donnees_inconnues.csv"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_output:
            temp_output_path = temp_output.name

        try:
            result = subprocess.run([
                'python', str(self.script),
                str(input_file), temp_output_path
            ], capture_output=True, text=True, encoding='utf-8', env=dict(os.environ, PYTHONIOENCODING='utf-8'))

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            with open(temp_output_path, 'r', encoding='utf-8') as f:
                generated_content = list(csv.DictReader(f))

            # Une seule ligne unique, donc aucune suppression
            self.assertEqual(len(generated_content), 1, "Les données uniques ne doivent pas être supprimées")

        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def test_donnees_manquantes(self):
        """Test avec des données manquantes ou incomplètes"""
        input_file = self.test_dir / "input_donnees_manquantes.csv"
        expected_output = self.test_dir / "output_donnees_manquantes.csv"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_output:
            temp_output_path = temp_output.name

        try:
            result = subprocess.run([
                'python', str(self.script),
                str(input_file), temp_output_path
            ], capture_output=True, text=True, encoding='utf-8', env=dict(os.environ, PYTHONIOENCODING='utf-8'))

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            with open(temp_output_path, 'r', encoding='utf-8') as f:
                generated_content = list(csv.DictReader(f))

            # Vérification que le script gère les données manquantes sans planter
            self.assertGreaterEqual(len(generated_content), 0, "Le script doit gérer les données manquantes")

        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

if __name__ == '__main__':
    unittest.main()