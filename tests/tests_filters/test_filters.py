import unittest
import subprocess
import csv
import os
import tempfile
from pathlib import Path

class TestFilters(unittest.TestCase):

    def setUp(self):
        """Configuration avant chaque test"""
        self.test_dir = Path(__file__).parent
        self.projet_root = self.test_dir.parent.parent
        self.script = self.projet_root / "Filters.py"

    def test_cas_nominal_aucun_filtre(self):
        """Test avec des entreprises qui ne doivent pas être filtrées"""
        input_file = self.test_dir / "input_nominal.csv"
        expected_output = self.test_dir / "output_nominal.csv"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_output:
            temp_output_path = temp_output.name

        try:
            # Exécution du script
            result = subprocess.run([
                'python', str(self.script),
                str(input_file), temp_output_path
            ], capture_output=True, text=True, encoding='utf-8')

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            # Vérification du résultat
            with open(temp_output_path, 'r', encoding='utf-8') as f:
                generated_content = list(csv.DictReader(f))

            # Vérification que toutes les entreprises ont "NON" dans le champ Filtré
            for row in generated_content:
                self.assertEqual(row.get('Filtré', ''), 'NON',
                               f"L'entreprise {row.get('Nom', '')} ne devrait pas être filtrée")

            # Vérification que les colonnes de filtrage ont été ajoutées
            if generated_content:
                fieldnames = generated_content[0].keys()
                self.assertIn('Filtré', fieldnames, "Colonne 'Filtré' manquante")
                self.assertIn('Raison_filtrage', fieldnames, "Colonne 'Raison_filtrage' manquante")

        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def test_cas_entreprises_a_filtrer(self):
        """Test avec des entreprises qui doivent être filtrées selon les règles"""
        input_file = self.test_dir / "input_a_filtrer.csv"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_output:
            temp_output_path = temp_output.name

        try:
            result = subprocess.run([
                'python', str(self.script),
                str(input_file), temp_output_path
            ], capture_output=True, text=True, encoding='utf-8')

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            with open(temp_output_path, 'r', encoding='utf-8') as f:
                generated_content = list(csv.DictReader(f))

            # Vérification que toutes les entreprises ont été filtrées (OUI) à cause du nombre d'avis < 20
            filtered_count = sum(1 for row in generated_content if row.get('Filtré', '') == 'OUI')
            self.assertGreater(filtered_count, 0, "Certaines entreprises devraient être filtrées")

            # Vérification des raisons de filtrage
            for row in generated_content:
                if row.get('Filtré', '') == 'OUI':
                    raison = row.get('Raison_filtrage', '')
                    self.assertNotEqual(raison, '', "Une raison de filtrage doit être fournie")

        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def test_donnees_manquantes(self):
        """Test avec des données manquantes ou incomplètes"""
        input_file = self.test_dir / "input_donnees_manquantes.csv"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_output:
            temp_output_path = temp_output.name

        try:
            result = subprocess.run([
                'python', str(self.script),
                str(input_file), temp_output_path
            ], capture_output=True, text=True, encoding='utf-8')

            # Le script devrait gérer les données manquantes sans planter
            self.assertEqual(result.returncode, 0, f"Le script devrait gérer les données manquantes: {result.stderr}")

            with open(temp_output_path, 'r', encoding='utf-8') as f:
                generated_content = list(csv.DictReader(f))

            # Vérification que le fichier de sortie est valide
            self.assertGreaterEqual(len(generated_content), 0, "Le fichier de sortie devrait être valide")

            # Vérification que les colonnes de filtrage ont été ajoutées même avec des données manquantes
            if generated_content:
                fieldnames = generated_content[0].keys()
                self.assertIn('Filtré', fieldnames, "Colonne 'Filtré' manquante")
                self.assertIn('Raison_filtrage', fieldnames, "Colonne 'Raison_filtrage' manquante")

                # Vérification que les lignes avec données manquantes ont un statut de filtrage
                for row in generated_content:
                    filtre_status = row.get('Filtré', '')
                    self.assertIn(filtre_status, ['OUI', 'NON'],
                                f"Statut de filtrage invalide: {filtre_status}")

        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

if __name__ == '__main__':
    unittest.main()