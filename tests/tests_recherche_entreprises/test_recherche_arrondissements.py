import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ajouter le répertoire parent au path pour importer le module à tester
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from recherche_entreprises import GooglePlacesSearcher


class TestRechercheEntreprisesArrondissements(unittest.TestCase):
    """Tests spécifiques pour les villes avec arrondissements"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.fake_api_key = "fake_api_key_for_testing"
        self.searcher = GooglePlacesSearcher(self.fake_api_key)

    @patch("recherche_entreprises.requests.Session.post")
    def test_recherche_marseille_arrondissement(self, mock_post):
        """Test de recherche avec ville + arrondissement (Marseille, 10e arrondissement)"""
        # Mock d'une réponse avec des résultats pour un arrondissement
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {
                    "displayName": {"text": "Boulangerie du 10e"},
                    "formattedAddress": "123 avenue de la République, 13010 Marseille, France",
                    "addressComponents": [
                        {"types": ["street_number"], "longText": "123"},
                        {"types": ["route"], "longText": "avenue de la République"},
                        {"types": ["locality"], "longText": "Marseille"},
                        {"types": ["postal_code"], "longText": "13010"},
                        {"types": ["country"], "longText": "France"},
                    ],
                    "rating": 4.3,
                    "userRatingCount": 87,
                    "currentOpeningHours": {"weekdayDescriptions": ["lundi: 07:00–19:30", "mardi: 07:00–19:30"]},
                },
                {
                    "displayName": {"text": "Pâtisserie Belle Vue"},
                    "formattedAddress": "45 rue Saint-Pierre, 13010 Marseille, France",
                    "addressComponents": [
                        {"types": ["street_number"], "longText": "45"},
                        {"types": ["route"], "longText": "rue Saint-Pierre"},
                        {"types": ["locality"], "longText": "Marseille"},
                        {"types": ["postal_code"], "longText": "13010"},
                        {"types": ["country"], "longText": "France"},
                    ],
                    "rating": 4.6,
                    "userRatingCount": 124,
                },
            ]
        }
        mock_post.return_value = mock_response

        # Test de la recherche avec arrondissement
        ville_avec_arrondissement = "Marseille, 10e arrondissement"
        businesses, pagination_count = self.searcher.search_businesses("boulanger", ville_avec_arrondissement, 20)

        # Vérifications
        self.assertEqual(len(businesses), 2, "Devrait trouver 2 entreprises")
        self.assertEqual(pagination_count, 1, "Une seule requête effectuée")

        # Vérification que l'API a été appelée avec la bonne requête
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        payload = call_args[1]["json"]  # Le payload JSON envoyé

        # Vérifier que la requête contient bien l'arrondissement
        expected_query = "boulanger in Marseille, 10e arrondissement, France"
        self.assertEqual(payload["textQuery"], expected_query, f"La requête devrait être: {expected_query}")

        # Vérification du contenu des résultats
        first_business = businesses[0]
        self.assertEqual(first_business["Nom"], "Boulangerie du 10e")
        self.assertEqual(first_business["Ville"], "Marseille")
        self.assertEqual(first_business["Metier"], "boulanger")
        self.assertEqual(first_business["Note"], 4.3)
        self.assertEqual(first_business["Nombre_avis"], 87)

        second_business = businesses[1]
        self.assertEqual(second_business["Nom"], "Pâtisserie Belle Vue")
        self.assertEqual(second_business["Ville"], "Marseille")
        self.assertEqual(second_business["Note"], 4.6)
        self.assertEqual(second_business["Nombre_avis"], 124)

    @patch("recherche_entreprises.requests.Session.post")
    def test_requetes_multiples_arrondissements(self, mock_post):
        """Test avec plusieurs arrondissements différents"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {
                    "displayName": {"text": "Test Restaurant"},
                    "formattedAddress": "Test Address, Marseille, France",
                    "addressComponents": [{"types": ["locality"], "longText": "Marseille"}],
                    "rating": 4.0,
                    "userRatingCount": 50,
                }
            ]
        }
        mock_post.return_value = mock_response

        # Test avec différents arrondissements
        arrondissements = [
            "Marseille, 1er arrondissement",
            "Marseille, 5e arrondissement",
            "Marseille, 16e arrondissement",
        ]

        for arrondissement in arrondissements:
            with self.subTest(arrondissement=arrondissement):
                businesses, _ = self.searcher.search_businesses("restaurant", arrondissement, 5)

                # Vérifier que chaque requête est bien formée
                expected_query = f"restaurant in {arrondissement}, France"
                call_args = mock_post.call_args
                payload = call_args[1]["json"]
                self.assertEqual(payload["textQuery"], expected_query, f"Requête incorrecte pour {arrondissement}")

                # Vérifier qu'on obtient des résultats
                self.assertGreater(len(businesses), 0, f"Devrait trouver des entreprises pour {arrondissement}")

    @patch("recherche_entreprises.requests.Session.post")
    def test_gestion_erreur_arrondissement_inexistant(self, mock_post):
        """Test avec un arrondissement qui n'existe pas"""
        # Mock d'une réponse vide (arrondissement inexistant)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"places": []}
        mock_post.return_value = mock_response

        # Test avec un arrondissement inexistant
        businesses, pagination_count = self.searcher.search_businesses("pharmacie", "Marseille, 25e arrondissement", 10)

        # Vérifications
        self.assertEqual(len(businesses), 0, "Ne devrait trouver aucune entreprise pour un arrondissement inexistant")
        self.assertEqual(pagination_count, 1, "Une seule requête effectuée")

        # Vérifier que l'API a quand même été appelée correctement
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        expected_query = "pharmacie in Marseille, 25e arrondissement, France"
        self.assertEqual(payload["textQuery"], expected_query)

    def test_construction_requete_avec_caracteres_speciaux(self):
        """Test que les caractères spéciaux dans les arrondissements sont gérés"""
        # Test unitaire de la construction de requête (sans appel API)
        metier = "coiffeur"
        villes_test = [
            "Marseille, 1er arrondissement",  # ordinal avec 'er'
            "Marseille, 2e arrondissement",  # ordinal avec 'e'
            "Paris, 11e arrondissement",  # autre ville
            "Lyon, 3e arrondissement",  # autre ville
        ]

        for ville in villes_test:
            with self.subTest(ville=ville):
                # Construction manuelle de la requête (comme le fait le script)
                query = f"{metier} in {ville}, France"

                # Vérifications
                self.assertIn(metier, query, "Le métier doit être dans la requête")
                self.assertIn(ville, query, "La ville avec arrondissement doit être dans la requête")
                self.assertIn("France", query, "Le pays doit être dans la requête")
                self.assertIn("arrondissement", query, "Le mot arrondissement doit être préservé")

    @patch("recherche_entreprises.requests.Session.post")
    def test_extraction_ville_depuis_adresse_arrondissement(self, mock_post):
        """Test que l'extraction de ville fonctionne avec les adresses d'arrondissements"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {
                    "displayName": {"text": "Commerce Test"},
                    "formattedAddress": "12 rue Example, 13010 Marseille, France",
                    "addressComponents": [
                        {"types": ["street_number"], "longText": "12"},
                        {"types": ["route"], "longText": "rue Example"},
                        {"types": ["locality"], "longText": "Marseille"},
                        {"types": ["postal_code"], "longText": "13010"},
                        {"types": ["administrative_area_level_1"], "longText": "Provence-Alpes-Côte d'Azur"},
                        {"types": ["country"], "longText": "France"},
                    ],
                    "rating": 4.2,
                    "userRatingCount": 75,
                }
            ]
        }
        mock_post.return_value = mock_response

        # Test avec un arrondissement
        businesses, _ = self.searcher.search_businesses("épicerie", "Marseille, 10e arrondissement", 1)

        # Vérifier que la ville est correctement extraite (doit être "Marseille", pas "Marseille, 10e arrondissement")
        self.assertEqual(len(businesses), 1)
        business = businesses[0]
        self.assertEqual(business["Ville"], "Marseille", "La ville extraite doit être 'Marseille' sans l'arrondissement")


if __name__ == "__main__":
    unittest.main()
