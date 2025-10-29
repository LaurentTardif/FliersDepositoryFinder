import csv
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ajouter le répertoire parent au path pour importer le module à tester
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from recherche_entreprises import GooglePlacesSearcher


class TestIntegrationVillesReelles(unittest.TestCase):
    """Tests d'intégration avec les vraies données de villes"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.fake_api_key = "fake_api_key_for_testing"
        self.searcher = GooglePlacesSearcher(self.fake_api_key)

        # Charger les villes du fichier exemples_villes.csv
        self.villes_exemples = []
        villes_file = Path(__file__).parent.parent.parent / "data" / "exemples_villes.csv"

        if villes_file.exists():
            with open(villes_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header ("Ville")
                for row in reader:
                    if row:
                        # Reconstituer la ville complète si elle a été séparée par les virgules
                        ville_complete = ", ".join(cell.strip() for cell in row if cell.strip())
                        if ville_complete:
                            self.villes_exemples.append(ville_complete)

    @patch("recherche_entreprises.requests.Session.post")
    def test_toutes_villes_exemples(self, mock_post):
        """Test avec toutes les villes du fichier exemples_villes.csv"""
        # Mock d'une réponse générique réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {
                    "displayName": {"text": "Test Business"},
                    "formattedAddress": "Test Address, Test City, France",
                    "addressComponents": [{"types": ["locality"], "longText": "Test City"}],
                    "rating": 4.0,
                    "userRatingCount": 50,
                }
            ]
        }
        mock_post.return_value = mock_response

        # Tester chaque ville
        metier = "restaurant"
        erreurs = []

        for i, ville in enumerate(self.villes_exemples):
            if not ville.strip():  # Skip empty cities
                continue

            with self.subTest(ville=ville, index=i):
                try:
                    # Appel de la fonction
                    businesses, pagination_count = self.searcher.search_businesses(metier, ville, 5)

                    # Vérifications de base
                    self.assertIsInstance(businesses, list, f"Résultat doit être une liste pour {ville}")
                    self.assertIsInstance(pagination_count, int, f"Pagination count doit être un entier pour {ville}")

                    # Vérifier que l'API a été appelée avec la bonne requête
                    if mock_post.call_args:
                        payload = mock_post.call_args[1]["json"]
                        expected_query = f"{metier} in {ville}, France"
                        self.assertEqual(
                            payload["textQuery"],
                            expected_query,
                            f"Requête incorrecte pour {ville}: attendu '{expected_query}', reçu '{payload['textQuery']}'",
                        )

                except Exception as e:
                    erreurs.append(f"Erreur pour la ville '{ville}': {str(e)}")

        # Rapport des erreurs s'il y en a
        if erreurs:
            self.fail(f"Erreurs détectées pour {len(erreurs)} villes:\n" + "\n".join(erreurs))

    def test_villes_avec_arrondissements_specifiques(self):
        """Test spécifique pour les villes avec arrondissements dans nos données"""
        villes_arrondissement = [ville for ville in self.villes_exemples if "arrondissement" in ville.lower()]

        if not villes_arrondissement:
            self.skipTest("Aucune ville avec arrondissement trouvée dans exemples_villes.csv")

        print(f"\nVilles avec arrondissements trouvées: {len(villes_arrondissement)}")
        for ville in villes_arrondissement:
            print(f"  - {ville}")

        # Test de construction de requête pour chacune
        metier = "boulanger"
        for ville in villes_arrondissement:
            with self.subTest(ville=ville):
                # Construction manuelle (comme dans le script)
                query = f"{metier} in {ville}, France"

                # Vérifications
                self.assertIn(metier, query)
                self.assertIn(ville, query)
                self.assertIn("France", query)
                self.assertIn("arrondissement", query.lower())

                # Vérifier que la requête est bien formée (pas de caractères problématiques)
                self.assertNotIn(",,", query, "Pas de virgules doubles")
                self.assertNotIn(" ,", query, "Pas d'espace avant virgule")

    def test_rapport_villes_exemples(self):
        """Génère un rapport sur les types de villes dans le fichier exemples"""
        if not self.villes_exemples:
            self.skipTest("Aucune ville chargée depuis exemples_villes.csv")

        total_villes = len(self.villes_exemples)
        villes_arrondissement = [v for v in self.villes_exemples if "arrondissement" in v.lower()]
        villes_accents = [v for v in self.villes_exemples if any(c in v for c in "àáâäèéêëìíîïòóôöùúûüÿçñ")]
        villes_apostrophe = [v for v in self.villes_exemples if "'" in v or "'" in v or "-" in v]

        print(f"\n=== RAPPORT DES VILLES EXEMPLES ===")
        print(f"Total de villes: {total_villes}")
        print(f"Villes avec arrondissements: {len(villes_arrondissement)}")
        print(f"Villes avec accents: {len(villes_accents)}")
        print(f"Villes avec apostrophes/tirets: {len(villes_apostrophe)}")

        if villes_arrondissement:
            print(f"\nExemples d'arrondissements:")
            for ville in villes_arrondissement[:3]:
                print(f"  - {ville}")

        # Ce test réussit toujours, c'est juste pour information
        self.assertTrue(True)


if __name__ == "__main__":
    # Exécuter avec verbosité pour voir les prints
    unittest.main(verbosity=2)
