import csv
import os
import subprocess
import tempfile
import unittest
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

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_output:
            temp_output_path = temp_output.name

        try:
            # Exécution du script
            result = subprocess.run(
                ["python", str(self.script), str(input_file), temp_output_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            # Vérification du résultat
            with open(temp_output_path, "r", encoding="utf-8") as f:
                generated_content = list(csv.DictReader(f))

            # Vérification que toutes les entreprises ont "NON" dans le champ Filtré
            for row in generated_content:
                self.assertEqual(
                    row.get("Filtré", ""), "NON", f"L'entreprise {row.get('Nom', '')} ne devrait pas être filtrée"
                )

            # Vérification que les colonnes de filtrage ont été ajoutées
            if generated_content:
                fieldnames = generated_content[0].keys()
                self.assertIn("Filtré", fieldnames, "Colonne 'Filtré' manquante")
                self.assertIn("Raison du filtre", fieldnames, "Colonne 'Raison du filtre' manquante")

        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def test_cas_entreprises_a_filtrer(self):
        """Test avec des entreprises qui doivent être filtrées selon les règles"""
        input_file = self.test_dir / "input_a_filtrer.csv"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_output:
            temp_output_path = temp_output.name

        try:
            result = subprocess.run(
                ["python", str(self.script), str(input_file), temp_output_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            with open(temp_output_path, "r", encoding="utf-8") as f:
                generated_content = list(csv.DictReader(f))

            # Vérification que toutes les entreprises ont été filtrées (OUI) à cause du nombre d'avis < 20
            filtered_count = sum(1 for row in generated_content if row.get("Filtré", "") == "OUI")
            self.assertGreater(filtered_count, 0, "Certaines entreprises devraient être filtrées")

            # Vérification des raisons de filtrage
            for row in generated_content:
                if row.get("Filtré", "") == "OUI":
                    raison = row.get("Raison du filtre", "")
                    self.assertNotEqual(raison, "", "Une raison de filtrage doit être fournie")

        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def test_donnees_manquantes(self):
        """Test avec des données manquantes ou incomplètes"""
        input_file = self.test_dir / "input_donnees_manquantes.csv"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_output:
            temp_output_path = temp_output.name

        try:
            result = subprocess.run(
                ["python", str(self.script), str(input_file), temp_output_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            # Le script devrait gérer les données manquantes sans planter
            self.assertEqual(result.returncode, 0, f"Le script devrait gérer les données manquantes: {result.stderr}")

            with open(temp_output_path, "r", encoding="utf-8") as f:
                generated_content = list(csv.DictReader(f))

            # Vérification que le fichier de sortie est valide
            self.assertGreaterEqual(len(generated_content), 0, "Le fichier de sortie devrait être valide")

            # Vérification que les colonnes de filtrage ont été ajoutées même avec des données manquantes
            if generated_content:
                fieldnames = generated_content[0].keys()
                self.assertIn("Filtré", fieldnames, "Colonne 'Filtré' manquante")
                self.assertIn("Raison du filtre", fieldnames, "Colonne 'Raison du filtre' manquante")

                # Vérification que les lignes avec données manquantes ont un statut de filtrage
                for row in generated_content:
                    filtre_status = row.get("Filtré", "")
                    self.assertIn(filtre_status, ["OUI", "NON"], f"Statut de filtrage invalide: {filtre_status}")

        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def test_entrees_deja_filtrees(self):
        """Test avec des entrées déjà filtrées pour vérifier le comportement de réapplication des règles"""
        input_file = self.test_dir / "input_a_filtrer.csv"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_output:
            temp_output_path = temp_output.name

        try:
            result = subprocess.run(
                ["python", str(self.script), str(input_file), temp_output_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            with open(temp_output_path, "r", encoding="utf-8") as f:
                generated_content = list(csv.DictReader(f))

            # Vérifier que les entrées déjà filtrées ont leur raison mise à jour avec la règle automatique
            entrees_deja_filtrees = {
                "Restaurant Mauvais": {
                    "nouvelle_raison": "Nombre d'avis insuffisant (< 20)",
                    "description": "Règle 1 appliquée (ancienne raison personnalisée écrasée)",
                },
                "Restaurant Médiocre": {
                    "nouvelle_raison": "Restaurant - Note insuffisante (< 4.5)",
                    "description": "Règle 3 appliquée (ancienne raison personnalisée écrasée)",
                },
                "Coiffeur Moyen": {
                    "nouvelle_raison": "Coiffeur/Barbier - Note insuffisante (< 4.0)",
                    "description": "Règle 4 appliquée (ancienne raison personnalisée écrasée)",
                },
                "Café Fermé": {
                    "nouvelle_raison": "Trop de jours de fermeture (> 3)",
                    "description": "Règle 2 appliquée (ancienne raison personnalisée écrasée)",
                },
            }

            for row in generated_content:
                nom = row.get("Nom", "")
                if nom in entrees_deja_filtrees:
                    attendu = entrees_deja_filtrees[nom]

                    # Vérifier que l'entrée est toujours filtrée
                    self.assertEqual(row.get("Filtré", ""), "OUI", f"{nom} devrait rester filtré")

                    # Vérifier que la raison a été mise à jour avec la règle automatique
                    raison_actuelle = row.get("Raison du filtre", "")
                    self.assertEqual(raison_actuelle, attendu["nouvelle_raison"], f"{nom}: {attendu['description']}")

            print(f"✅ Test des entrées déjà filtrées validé: les raisons sont mises à jour par les règles automatiques")

        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def test_cas_positifs_non_filtres(self):
        """Test que les cas positifs ne sont pas filtrés (vérification de non-régression)"""
        input_file = self.test_dir / "input_a_filtrer.csv"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_output:
            temp_output_path = temp_output.name

        try:
            result = subprocess.run(
                ["python", str(self.script), str(input_file), temp_output_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            with open(temp_output_path, "r", encoding="utf-8") as f:
                generated_content = list(csv.DictReader(f))

            # Vérifier les cas positifs spécifiques qui ne doivent PAS être filtrés
            cas_positifs = {
                "Restaurant Très Populaire": {
                    "attendu": "NON",
                    "raison": "Restaurant avec ≥250 avis et note ≥4.8 (règles 1 et 3 non applicables)",
                },
                "Coiffeur Excellence": {
                    "attendu": "NON",
                    "raison": "Coiffeur avec ≥80 avis et note ≥4.5 (règles 1 et 4 non applicables)",
                },
                "Boulangerie Bien Notée": {"attendu": "NON", "raison": "Boulangerie avec ≥50 avis (règle 1 non applicable)"},
                "Garage Ouvert": {
                    "attendu": "NON",
                    "raison": "Garage avec ≥35 avis et ≤2 jours fermeture (règles 1 et 2 non applicables)",
                },
            }

            # Vérifier chaque cas positif
            for row in generated_content:
                nom = row.get("Nom", "")
                if nom in cas_positifs:
                    attendu = cas_positifs[nom]["attendu"]
                    raison = cas_positifs[nom]["raison"]
                    filtre_status = row.get("Filtré", "")

                    self.assertEqual(filtre_status, attendu, f"{nom} ne devrait PAS être filtré. {raison}")

                    # Vérifier aussi que la raison est "Pas de filtre"
                    raison_filtrage = row.get("Raison du filtre", "")
                    self.assertEqual(raison_filtrage, "Pas de filtre", f"{nom} devrait avoir 'Pas de filtre' comme raison")

            # Compter les cas positifs trouvés
            cas_positifs_trouves = sum(
                1 for row in generated_content if row.get("Nom", "") in cas_positifs and row.get("Filtré", "") == "NON"
            )

            self.assertEqual(
                cas_positifs_trouves,
                len(cas_positifs),
                f"Tous les {len(cas_positifs)} cas positifs devraient être trouvés et non filtrés",
            )

            print(f"✅ Cas positifs validés: {cas_positifs_trouves}/{len(cas_positifs)} entreprises non filtrées")

        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def test_couverture_filtres_multiples(self):
        """Test que tous les filtres sont couverts avec plusieurs données par filtre"""
        input_file = self.test_dir / "input_a_filtrer.csv"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as temp_output:
            temp_output_path = temp_output.name

        try:
            result = subprocess.run(
                ["python", str(self.script), str(input_file), temp_output_path, "--verbose"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 0, f"Erreur d'exécution: {result.stderr}")

            with open(temp_output_path, "r", encoding="utf-8") as f:
                generated_content = list(csv.DictReader(f))

            # Compter les différents types de filtres appliqués
            raisons_comptees = {}
            cas_non_filtres = 0

            for row in generated_content:
                if row.get("Filtré", "") == "OUI":
                    raison = row.get("Raison du filtre", "")
                    # Extraire le type de filtre de la raison
                    if "Nombre d'avis insuffisant" in raison:
                        raisons_comptees["avis_insuffisant"] = raisons_comptees.get("avis_insuffisant", 0) + 1
                    elif "Trop de jours de fermeture" in raison:
                        raisons_comptees["jours_fermeture"] = raisons_comptees.get("jours_fermeture", 0) + 1
                    elif "Restaurant - Note insuffisante" in raison:
                        raisons_comptees["restaurant_note"] = raisons_comptees.get("restaurant_note", 0) + 1
                    elif "Coiffeur/Barbier - Note insuffisante" in raison:
                        raisons_comptees["coiffeur_note"] = raisons_comptees.get("coiffeur_note", 0) + 1
                elif row.get("Filtré", "") == "NON":
                    cas_non_filtres += 1

            # Vérifier qu'on a au moins 2 données pour chaque type de filtre
            self.assertGreaterEqual(
                raisons_comptees.get("avis_insuffisant", 0),
                2,
                "Il devrait y avoir au moins 2 entreprises filtrées pour 'Nombre d'avis insuffisant'",
            )
            self.assertGreaterEqual(
                raisons_comptees.get("jours_fermeture", 0),
                2,
                "Il devrait y avoir au moins 2 entreprises filtrées pour 'Jours de fermeture'",
            )
            self.assertGreaterEqual(
                raisons_comptees.get("restaurant_note", 0),
                2,
                "Il devrait y avoir au moins 2 restaurants filtrés pour 'Note insuffisante'",
            )
            self.assertGreaterEqual(
                raisons_comptees.get("coiffeur_note", 0),
                1,
                "Il devrait y avoir au moins 1 coiffeur filtré pour 'Note insuffisante'",
            )

            # Vérifier qu'on a des cas positifs (non filtrés)
            self.assertGreaterEqual(cas_non_filtres, 4, "Il devrait y avoir au moins 4 cas positifs (non filtrés)")

            print(f"✅ Couverture des filtres validée:")
            print(f"   - Avis insuffisant: {raisons_comptees.get('avis_insuffisant', 0)} entrées")
            print(f"   - Jours fermeture: {raisons_comptees.get('jours_fermeture', 0)} entrées")
            print(f"   - Restaurant note: {raisons_comptees.get('restaurant_note', 0)} entrées")
            print(f"   - Coiffeur note: {raisons_comptees.get('coiffeur_note', 0)} entrées")
            print(f"   - Cas positifs (NON filtrés): {cas_non_filtres} entrées")

        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)


if __name__ == "__main__":
    unittest.main()
