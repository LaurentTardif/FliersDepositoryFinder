import csv
import os
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


class TestMajHistorique(unittest.TestCase):

    def setUp(self):
        """Configuration avant chaque test"""
        self.test_dir = Path(__file__).parent
        self.projet_root = self.test_dir.parent.parent
        self.script = self.projet_root / "maj_historique.py"

    def test_cas_nominal_maj_historique(self):
        """Test de mise à jour normale de l'historique"""
        historique_file = self.test_dir / "historique_existant.csv"
        candidats_file = self.test_dir / "candidats_nominal.csv"

        # Créer des copies temporaires pour ne pas modifier les originaux
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_historique:
            temp_historique_path = temp_historique.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_output:
            temp_output_path = temp_output.name

        try:
            # Copier le fichier historique
            shutil.copy2(historique_file, temp_historique_path)

            # Exécution du script
            result = subprocess.run(
                ["python", str(self.script), temp_historique_path, str(candidats_file), temp_output_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            # Vérification du résultat
            with open(temp_output_path, "r", encoding="utf-8") as f:
                updated_content = list(csv.DictReader(f))

            # L'historique devrait contenir plus d'entrées qu'avant (nouveaux ajouts)
            with open(temp_historique_path, "r", encoding="utf-8") as f:
                original_content = list(csv.DictReader(f))

            self.assertGreaterEqual(
                len(updated_content), len(original_content), "L'historique mis à jour devrait avoir au moins autant d'entrées"
            )

            # Vérification que les colonnes attendues existent
            if updated_content:
                fieldnames = set(updated_content[0].keys())
                expected_columns = {
                    "Nom",
                    "Adresse",
                    "Ville",
                    "Metier_normalise",
                    "Heures_ouverture",
                    "Nombre_avis",
                    "Note",
                    "Jours_fermeture",
                    "Date_introduction",
                    "Date_verification",
                    "Filtré",
                    "Actif",
                }

                # Vérification que toutes les colonnes attendues sont présentes
                missing_columns = expected_columns - fieldnames
                self.assertEqual(
                    len(missing_columns), 0, f"Colonnes manquantes dans l'historique mis à jour: {missing_columns}"
                )

                # Vérification spécifique des colonnes de date
                self.assertIn("Date_introduction", fieldnames, "Colonne Date_introduction manquante")
                self.assertIn("Date_verification", fieldnames, "Colonne Date_verification manquante")

        finally:
            for path in [temp_historique_path, temp_output_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_donnees_inconnues(self):
        """Test avec des entreprises complètement nouvelles"""
        historique_file = self.test_dir / "historique_existant.csv"
        candidats_file = self.test_dir / "candidats_inconnues.csv"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_historique:
            temp_historique_path = temp_historique.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_output:
            temp_output_path = temp_output.name

        try:
            shutil.copy2(historique_file, temp_historique_path)

            result = subprocess.run(
                ["python", str(self.script), temp_historique_path, str(candidats_file), temp_output_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            with open(temp_output_path, "r", encoding="utf-8") as f:
                updated_content = list(csv.DictReader(f))

            # Vérification que les nouvelles entreprises ont été ajoutées
            new_entries = [row for row in updated_content if "Entreprise Exotique" in row.get("Nom", "")]
            self.assertGreater(len(new_entries), 0, "Les nouvelles entreprises devraient être ajoutées")

        finally:
            for path in [temp_historique_path, temp_output_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_donnees_manquantes(self):
        """Test avec des données incomplètes ou manquantes et gestion du statut Actif"""
        historique_file = self.test_dir / "historique_existant.csv"
        candidats_file = self.test_dir / "candidats_manquantes.csv"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_historique:
            temp_historique_path = temp_historique.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_output:
            temp_output_path = temp_output.name

        try:
            shutil.copy2(historique_file, temp_historique_path)

            result = subprocess.run(
                ["python", str(self.script), temp_historique_path, str(candidats_file), temp_output_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=dict(os.environ, PYTHONIOENCODING="utf-8"),
            )

            # Le script devrait gérer les données manquantes sans planter
            self.assertEqual(result.returncode, 0, f"Le script devrait gérer les données manquantes: {result.stderr}")

            with open(temp_output_path, "r", encoding="utf-8") as f:
                updated_content = list(csv.DictReader(f))

            # Vérification que le fichier de sortie est valide
            self.assertGreaterEqual(len(updated_content), 0, "Le fichier de sortie devrait être valide")

            # Vérification de la gestion du statut Actif
            # Les 3 entreprises de l'historique sont présentes dans candidats_manquantes,
            # donc elles doivent être marquées comme Actif = 'Oui'
            entreprises_historique = {"Boulangerie Ancienne": False, "Restaurant Classique": False, "Coiffure Vintage": False}

            for row in updated_content:
                nom = row.get("Nom", "")
                if nom in entreprises_historique:
                    self.assertEqual(
                        row.get("Actif", ""),
                        "Oui",
                        f"L'entreprise {nom} devrait être marquée comme Actif=Oui car présente dans les candidats",
                    )
                    entreprises_historique[nom] = True

            # Vérifier que toutes les entreprises de l'historique ont été trouvées
            for nom, trouve in entreprises_historique.items():
                self.assertTrue(trouve, f"L'entreprise {nom} devrait être présente dans le résultat")

        finally:
            for path in [temp_historique_path, temp_output_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_compteur_mises_a_jour_donnees(self):
        """Test que le compteur 'Mises à jour de données' est incrémenté pour chaque ligne modifiée"""
        historique_file = self.test_dir / "historique_existant.csv"
        candidats_file = self.test_dir / "candidats_manquantes.csv"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_historique:
            temp_historique_path = temp_historique.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_output:
            temp_output_path = temp_output.name

        try:
            shutil.copy2(historique_file, temp_historique_path)

            result = subprocess.run(
                ["python", str(self.script), temp_historique_path, str(candidats_file), temp_output_path, "--verbose"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=dict(os.environ, PYTHONIOENCODING="utf-8"),
            )

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            # Analyser la sortie pour extraire le compteur "Mises à jour de données"
            output_lines = result.stdout.split("\n")
            compteur_line = None
            for line in output_lines:
                if "🔄 Mises à jour de données:" in line:
                    compteur_line = line
                    break

            self.assertIsNotNone(compteur_line, "Le compteur 'Mises à jour de données' devrait être affiché")

            # Extraire la valeur du compteur
            import re

            match = re.search(r"🔄 Mises à jour de données: (\d+)", compteur_line)
            self.assertIsNotNone(match, f"Impossible d'extraire le compteur de: {compteur_line}")

            compteur_value = int(match.group(1))

            # Vérifier que le compteur correspond au nombre total de lignes modifiées
            # candidats_manquantes.csv contient 6 entrées :
            # - 3 entreprises existantes (mises à jour -> Date_verification + Actif)
            # - 3 nouvelles entreprises avec données incomplètes (nouvelles entrées)
            # Donc le compteur devrait être 6 (une mise à jour pour chaque ligne modifiée)
            expected_count = 6
            self.assertEqual(
                compteur_value,
                expected_count,
                f"Le compteur devrait être {expected_count} (une mise à jour par ligne modifiée), mais trouvé {compteur_value}",
            )

            print(f"✅ Compteur validé: {compteur_value} mises à jour de données")

        finally:
            for path in [temp_historique_path, temp_output_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_statut_actif_entreprises_absentes(self):
        """Test que les entreprises absentes des candidats sont marquées comme Actif=Non"""
        historique_file = self.test_dir / "historique_existant.csv"
        candidats_file = self.test_dir / "candidats_inconnues.csv"  # Ne contient aucune entreprise de l'historique

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_historique:
            temp_historique_path = temp_historique.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_output:
            temp_output_path = temp_output.name

        try:
            shutil.copy2(historique_file, temp_historique_path)

            result = subprocess.run(
                ["python", str(self.script), temp_historique_path, str(candidats_file), temp_output_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=dict(os.environ, PYTHONIOENCODING="utf-8"),
            )

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            with open(temp_output_path, "r", encoding="utf-8") as f:
                updated_content = list(csv.DictReader(f))

            # Vérification que les entreprises de l'historique sont marquées comme inactives
            # car elles ne sont pas présentes dans candidats_inconnues
            entreprises_historique = ["Boulangerie Ancienne", "Restaurant Classique", "Coiffure Vintage"]

            for row in updated_content:
                nom = row.get("Nom", "")
                if nom in entreprises_historique:
                    self.assertEqual(
                        row.get("Actif", ""),
                        "Non",
                        f"L'entreprise {nom} devrait être marquée comme Actif=Non car absente des candidats",
                    )
                    # Vérifier aussi que la date de vérification n'a pas été mise à jour
                    date_verif = row.get("Date_verification", "")
                    self.assertNotEqual(
                        date_verif, "2025-10-27", f"La date de vérification de {nom} ne devrait pas être mise à jour"
                    )

        finally:
            for path in [temp_historique_path, temp_output_path]:
                if os.path.exists(path):
                    os.unlink(path)


if __name__ == "__main__":
    unittest.main()
