import unittest
import subprocess
import csv
import os
import tempfile
from pathlib import Path

class TestNormaliseMetiers(unittest.TestCase):

    def setUp(self):
        """Configuration avant chaque test"""
        self.test_dir = Path(__file__).parent
        self.projet_root = self.test_dir.parent.parent
        self.input_file = self.test_dir / "input_MetiersNonNormalisés.csv"
        self.reference_file = self.projet_root / "data" / "referencesMetiers.csv"
        self.expected_output = self.test_dir / "output_Metiers_Normalisés.csv"
        self.normalise_script = self.projet_root / "NormaliseMetiers.py"

    def test_normalisation_complete(self):
        """Test que la normalisation produit le résultat attendu"""

        # Vérification que tous les fichiers nécessaires existent
        self.assertTrue(self.input_file.exists(), f"Fichier d'entrée manquant: {self.input_file}")
        self.assertTrue(self.reference_file.exists(), f"Fichier de référence manquant: {self.reference_file}")
        self.assertTrue(self.expected_output.exists(), f"Fichier de sortie attendu manquant: {self.expected_output}")
        self.assertTrue(self.normalise_script.exists(), f"Script manquant: {self.normalise_script}")

        # Création d'un fichier de sortie temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_output:
            temp_output_path = temp_output.name

        try:
            # Exécution du script de normalisation
            result = subprocess.run([
                'python',
                str(self.normalise_script),
                str(self.input_file),
                temp_output_path,
                str(self.reference_file)
            ], capture_output=True, text=True, encoding='utf-8')

            # Vérification que le script s'est exécuté sans erreur
            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            # Lecture du fichier de sortie généré
            with open(temp_output_path, 'r', encoding='utf-8') as f:
                generated_content = list(csv.DictReader(f))

            # Lecture du fichier de sortie attendu
            with open(self.expected_output, 'r', encoding='utf-8') as f:
                expected_content = list(csv.DictReader(f))

            # Comparaison du nombre de lignes
            self.assertEqual(len(generated_content), len(expected_content),
                           "Le nombre de lignes ne correspond pas")

            # Comparaison ligne par ligne
            for i, (generated_row, expected_row) in enumerate(zip(generated_content, expected_content)):
                with self.subTest(ligne=i+1):
                    self.assertEqual(generated_row['Nom'], expected_row['Nom'],
                                   f"Ligne {i+1}: Nom différent")
                    self.assertEqual(generated_row['Adresse'], expected_row['Adresse'],
                                   f"Ligne {i+1}: Adresse différente")
                    self.assertEqual(generated_row['Ville'], expected_row['Ville'],
                                   f"Ligne {i+1}: Ville différente")
                    self.assertEqual(generated_row['Metier_normalise'], expected_row['Metier_normalise'],
                                   f"Ligne {i+1}: Métier normalisé différent")

        finally:
            # Nettoyage du fichier temporaire
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def test_gestion_metiers_inconnus(self):
        """Test que les métiers non référencés sont marqués comme INCONNU"""

        # Création d'un fichier d'entrée temporaire avec un métier non référencé
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_input:
            writer = csv.writer(temp_input)
            writer.writerow(['Nom', 'Adresse', 'Ville', 'Metier'])
            writer.writerow(['Test User', '123 rue Test', 'TestVille', 'astronaute'])
            temp_input_path = temp_input.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_output:
            temp_output_path = temp_output.name

        try:
            # Exécution du script
            result = subprocess.run([
                'python',
                str(self.normalise_script),
                temp_input_path,
                temp_output_path,
                str(self.reference_file)
            ], capture_output=True, text=True, encoding='utf-8')

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            # Vérification du résultat
            with open(temp_output_path, 'r', encoding='utf-8') as f:
                content = list(csv.DictReader(f))

            self.assertEqual(len(content), 1)
            self.assertEqual(content[0]['Metier_normalise'], 'INCONNU(astronaute)')

        finally:
            # Nettoyage
            for path in [temp_input_path, temp_output_path]:
                if os.path.exists(path):
                    os.unlink(path)

if __name__ == '__main__':
    unittest.main()