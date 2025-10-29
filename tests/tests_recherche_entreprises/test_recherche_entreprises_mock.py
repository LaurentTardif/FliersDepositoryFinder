import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ajouter le répertoire parent au path pour importer le module à tester
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from recherche_entreprises import GooglePlacesSearcher


class TestRechercheEntreprisesMock(unittest.TestCase):
    """Tests avec mock complet de l'API Google pour tester la logique métier"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.fake_api_key = "fake_api_key_for_testing"
        self.searcher = GooglePlacesSearcher(self.fake_api_key)

    @patch("recherche_entreprises.requests.Session.post")
    def test_api_key_valide_mock(self, mock_post):
        """Test de validation de clé API avec réponse mockée"""
        # Mock d'une réponse API valide
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {"displayName": {"text": "Restaurant Test"}, "formattedAddress": "123 rue Test, 38000 Grenoble, France"}
            ]
        }
        mock_post.return_value = mock_response

        # Test de la validation
        result = self.searcher.test_api_key()
        self.assertTrue(result, "La validation de clé API devrait réussir avec un mock valide")

        # Vérification que l'API a été appelée
        mock_post.assert_called_once()

    @patch("recherche_entreprises.requests.Session.post")
    def test_api_key_invalide_mock(self, mock_post):
        """Test avec clé API invalide (403 Forbidden)"""
        # Mock d'une réponse 403
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error": {"message": "API key not valid"}}
        mock_post.return_value = mock_response

        # Test de la validation
        result = self.searcher.test_api_key()
        self.assertFalse(result, "La validation devrait échouer avec une clé invalide")

    @patch("recherche_entreprises.requests.Session.post")
    def test_recherche_avec_resultats_mock(self, mock_post):
        """Test de recherche avec résultats mockés"""
        # Mock d'une réponse avec des résultats
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {
                    "displayName": {"text": "Boulangerie Dupont"},
                    "formattedAddress": "12 rue de la Paix, 38000 Grenoble, France",
                    "addressComponents": [{"types": ["locality"], "longText": "Grenoble"}],
                    "rating": 4.5,
                    "userRatingCount": 142,
                    "currentOpeningHours": {"weekdayDescriptions": ["lundi: 07:00–19:00", "mardi: 07:00–19:00"]},
                },
                {
                    "displayName": {"text": "Boulangerie Martin"},
                    "formattedAddress": "45 avenue Test, 38000 Grenoble, France",
                    "addressComponents": [{"types": ["locality"], "longText": "Grenoble"}],
                    "rating": 4.2,
                    "userRatingCount": 89,
                },
            ]
        }
        mock_post.return_value = mock_response

        # Test de la recherche
        businesses, pagination_count = self.searcher.search_businesses("boulanger", "Grenoble", 20)

        # Vérifications
        self.assertEqual(len(businesses), 2, "Devrait trouver 2 entreprises")
        self.assertEqual(pagination_count, 1, "Une seule requête effectuée")

        # Vérification du contenu
        first_business = businesses[0]
        self.assertEqual(first_business["Nom"], "Boulangerie Dupont")
        self.assertEqual(first_business["Ville"], "Grenoble")
        self.assertEqual(first_business["Metier"], "boulanger")
        self.assertEqual(first_business["Note"], 4.5)
        self.assertEqual(first_business["Nombre_avis"], 142)

    @patch("recherche_entreprises.requests.Session.post")
    def test_recherche_sans_resultats_mock(self, mock_post):
        """Test de recherche sans résultats"""
        # Mock d'une réponse vide
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"places": []}
        mock_post.return_value = mock_response

        # Test de la recherche
        businesses, pagination_count = self.searcher.search_businesses("metier_inexistant", "ville_inexistante", 20)

        # Vérifications
        self.assertEqual(len(businesses), 0, "Devrait ne trouver aucune entreprise")
        self.assertEqual(pagination_count, 1, "Une seule requête effectuée")

    @patch("recherche_entreprises.requests.Session.post")
    def test_pagination_mock(self, mock_post):
        """Test de la pagination avec mock"""
        # Réponse unique (API Text Search ne supporte plus la pagination)
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "places": [
                {
                    "displayName": {"text": "Restaurant 1"},
                    "formattedAddress": "1 rue Test, 38000 Grenoble, France",
                    "addressComponents": [{"types": ["locality"], "longText": "Grenoble"}],
                    "rating": 4.0,
                    "userRatingCount": 50,
                    "location": {"latitude": 45.1885, "longitude": 5.7245},
                    "types": ["restaurant"]
                }
            ]
            # Pas de nextPageToken car API Text Search ne supporte pas la pagination
        }

        # Configuration du mock pour retourner une seule réponse
        mock_post.return_value = response

        # Test de la recherche (sans pagination car API Text Search ne la supporte plus)
        businesses, pagination_count = self.searcher.search_businesses("restaurant", "Grenoble", 40)

        # Vérifications - API Text Search limitée à 20 résultats maximum
        self.assertEqual(len(businesses), 1, "Devrait trouver 1 entreprise (API Text Search limitée)")
        self.assertEqual(pagination_count, 1, "Une seule requête effectuée")
        self.assertEqual(mock_post.call_count, 1, "Devrait avoir fait 1 appel API")

    def test_extraction_ville_nouvelle_api(self):
        """Test d'extraction de ville depuis les données de la nouvelle API"""
        place_data = {
            "addressComponents": [
                {"types": ["street_number"], "longText": "123"},
                {"types": ["route"], "longText": "rue de la Paix"},
                {"types": ["locality"], "longText": "Grenoble"},
                {"types": ["country"], "longText": "France"},
            ],
            "formattedAddress": "123 rue de la Paix, 38000 Grenoble, France",
        }

        ville = self.searcher._extract_city_new_api(place_data)
        self.assertEqual(ville, "Grenoble", "Devrait extraire correctement la ville")

    def test_extraction_heures_ouverture(self):
        """Test d'extraction des heures d'ouverture"""
        place_data = {
            "currentOpeningHours": {"weekdayDescriptions": ["lundi: 07:00–19:00", "mardi: 07:00–19:00", "mercredi: Fermé"]}
        }

        heures = self.searcher._extract_opening_hours(place_data)
        expected = "lundi: 07:00–19:00; mardi: 07:00–19:00; mercredi: Fermé"
        self.assertEqual(heures, expected, "Devrait extraire correctement les heures")

    def test_calcul_jours_fermeture(self):
        """Test du calcul des jours de fermeture"""
        place_data = {
            "currentOpeningHours": {
                "periods": [
                    {"open": {"day": 1}},  # Lundi
                    {"open": {"day": 2}},  # Mardi
                    {"open": {"day": 4}},  # Jeudi
                    {"open": {"day": 5}},  # Vendredi
                    {"open": {"day": 6}},  # Samedi
                    # Dimanche (0) et Mercredi (3) manquants = 2 jours fermés
                ]
            }
        }

        jours_fermeture = self.searcher._extract_closure_days(place_data)
        self.assertEqual(jours_fermeture, 2, "Devrait calculer 2 jours de fermeture")


if __name__ == "__main__":
    unittest.main()
