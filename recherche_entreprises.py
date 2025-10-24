import csv
import sys
import time
import requests
from typing import List, Dict, Tuple
import argparse

class GooglePlacesSearcher:
    """Classe pour rechercher des entreprises via Google Places API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://places.googleapis.com/v1/places:searchText"
        self.session = requests.Session()
        # Configuration des headers pour la nouvelle API
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.addressComponents,places.location,places.currentOpeningHours,places.rating,places.userRatingCount,places.regularOpeningHours'
        })

    def test_api_key(self) -> bool:
        """
        Test la validité de la clé API avec une requête simple

        Returns:
            True si la clé API fonctionne, False sinon
        """
        print("🔍 Test de la clé API...")

        # Test simple avec une recherche basique pour la nouvelle API
        payload = {
            "textQuery": "restaurant Grenoble",
            "languageCode": "fr",
            "maxResultCount": 1
        }

        try:
            response = self.session.post(self.base_url, json=payload)

            if response.status_code == 200:
                data = response.json()
                places = data.get('places', [])
                if places:
                    print("✅ Clé API valide et fonctionnelle")
                    return True
                else:
                    print("⚠️  API fonctionne mais aucun résultat trouvé")
                    return True
            elif response.status_code == 403:
                print("❌ Clé API refusée (403 Forbidden)")
                print("\n🔧 Solutions possibles :")
                print("1. Vérifiez que votre clé API est correcte")
                print("2. Activez la nouvelle API Places dans Google Cloud Console:")
                print("   https://console.cloud.google.com/apis/library/places-backend.googleapis.com")
                print("3. Vérifiez les restrictions de votre clé API")
                print("4. Assurez-vous d'avoir des crédits/quota disponibles")
                return False
            else:
                print(f"❌ Erreur HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        print(f"Message: {error_data['error'].get('message', 'Pas de détails')}")
                except:
                    print(f"Réponse: {response.text[:200]}")
                return False

        except requests.RequestException as e:
            print(f"❌ Erreur réseau lors du test: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur inattendue lors du test: {e}")
            return False

    def search_businesses(self, metier: str, ville: str, max_results: int = 20) -> Tuple[List[Dict], int]:
        """
        Recherche des entreprises pour un métier dans une ville donnée avec pagination

        Args:
            metier: Le type d'entreprise à rechercher
            ville: La ville où chercher
            max_results: Nombre maximum de résultats par recherche (max 60 avec pagination)

        Returns:
            Tuple contenant (liste des entreprises trouvées, nombre de pages suivantes utilisées)
        """
        businesses = []
        next_page_token = None
        pagination_count = 0

        # Limite maximale de l'API : 60 résultats au total
        max_results = min(max_results, 60)
        total_collected = 0

        # Construction de la requête de recherche pour la nouvelle API
        query = f"{metier} in {ville}, France"

        while total_collected < max_results:
            # Calculer combien de résultats demander pour cette page
            remaining = max_results - total_collected
            page_size = min(remaining, 20)  # Max 20 par page

            # Payload pour la nouvelle API Places
            payload = {
                "textQuery": query,
                "languageCode": "fr",
                "pageSize": page_size
            }

            # Ajouter le token de pagination si disponible
            if next_page_token:
                payload["pageToken"] = next_page_token
                pagination_count += 1
                print(f"    🔄 Page suivante {pagination_count + 1} (pagination)")

            try:
                # Recherche avec la nouvelle API
                response = self.session.post(self.base_url, json=payload)

                if response.status_code != 200:
                    print(f"Erreur HTTP {response.status_code} pour {metier} à {ville}")

                    if response.status_code == 403:
                        print("\n🚨 ERREUR 403 FORBIDDEN - Vérifiez :")
                        print("1. Votre clé API est-elle valide ?")
                        print("2. La nouvelle API Places est-elle activée dans Google Cloud Console ?")
                        print("3. Y a-t-il des restrictions d'IP ou de domaine ?")
                        print("4. Avez-vous des crédits disponibles ?")
                        print("5. URL: https://console.cloud.google.com/apis/library/places-backend.googleapis.com")

                    try:
                        error_data = response.json()
                        if 'error' in error_data:
                            print(f"Message d'erreur: {error_data['error'].get('message', 'Pas de détails')}")
                    except:
                        print(f"Réponse brute: {response.text[:200]}")

                    break

                data = response.json()
                places = data.get('places', [])

                # Traitement des résultats de cette page
                for place in places:
                    business = self._extract_business_info_new_api(place, metier)
                    if business:
                        businesses.append(business)
                        total_collected += 1

                # Vérifier s'il y a une page suivante
                next_page_token = data.get('nextPageToken')
                print("le next page token vaut :", next_page_token)

                # Si pas de token ou pas de nouveaux résultats, arrêter
                if not next_page_token or len(places) == 0:
                    break

                # Délai entre les pages pour respecter les limites de l'API
                if next_page_token:
                    time.sleep(0.2)

            except requests.RequestException as e:
                print(f"Erreur réseau pour {metier} à {ville}: {e}")
                break
            except Exception as e:
                print(f"Erreur inattendue pour {metier} à {ville}: {e}")
                break

        return businesses, pagination_count

    def _extract_business_info_new_api(self, place: Dict, metier_recherche: str) -> Dict:
        """
        Extrait les informations pertinentes d'un lieu depuis la nouvelle API Google Places

        Args:
            place: Données du lieu depuis la nouvelle API Google Places
            metier_recherche: Le métier recherché

        Returns:
            Dictionnaire avec les informations de l'entreprise
        """
        # Extraction du nom depuis la nouvelle API
        name = place.get('displayName', {}).get('text', '')

        # Extraction de l'adresse formatée
        address = place.get('formattedAddress', '')

        # Extraction de la ville depuis les composants d'adresse
        ville = self._extract_city_new_api(place)

        # Extraction des nouveaux champs
        heures_ouverture = self._extract_opening_hours(place)
        nombre_avis = place.get('userRatingCount', 0)
        note = place.get('rating', 0.0)
        jours_fermeture = self._extract_closure_days(place)

        return {
            'Nom': name,
            'Adresse': address,
            'Ville': ville,
            'Metier': metier_recherche,
            'Heures_ouverture': heures_ouverture,
            'Nombre_avis': nombre_avis,
            'Note': note,
            'Jours_fermeture': jours_fermeture
        }

    def _extract_business_info(self, place: Dict, metier_recherche: str) -> Dict:
        """
        Extrait les informations pertinentes d'un lieu Google Places (ancienne API)

        Args:
            place: Données du lieu depuis l'API Google Places
            metier_recherche: Le métier recherché

        Returns:
            Dictionnaire avec les informations de l'entreprise
        """
        # Extraction de l'adresse formatée
        address = place.get('formatted_address', '')

        # Extraction de la ville depuis l'adresse ou les composants d'adresse
        ville = self._extract_city(place)

        return {
            'Nom': place.get('name', ''),
            'Adresse': address,
            'Ville': ville,
            'Metier': metier_recherche,
            'Heures_ouverture': 'Non disponible (ancienne API)',
            'Nombre_avis': 0,
            'Note': 0.0,
            'Jours_fermeture': 0
        }

    def _extract_city_new_api(self, place: Dict) -> str:
        """
        Extrait la ville depuis les données de la nouvelle API Google Places

        Args:
            place: Données du lieu depuis la nouvelle API Google Places

        Returns:
            Nom de la ville
        """
        # Recherche dans les composants d'adresse de la nouvelle API
        address_components = place.get('addressComponents', [])
        for component in address_components:
            types = component.get('types', [])
            if 'locality' in types:
                return component.get('longText', '')
            elif 'administrative_area_level_2' in types and not any('locality' in comp.get('types', []) for comp in address_components):
                return component.get('longText', '')

        # Fallback: extraction depuis l'adresse formatée
        formatted_address = place.get('formattedAddress', '')
        if formatted_address:
            parts = formatted_address.split(', ')
            for part in parts:
                if part and not part.isdigit() and 'France' not in part:
                    # Exclure les codes postaux et le nom du pays
                    if not any(char.isdigit() for char in part) or len(part) > 5:
                        return part

        return ''

    def _extract_city(self, place: Dict) -> str:
        """
        Extrait la ville depuis les données Google Places (ancienne API)

        Args:
            place: Données du lieu depuis l'API Google Places

        Returns:
            Nom de la ville
        """
        # Recherche dans les composants d'adresse
        address_components = place.get('address_components', [])
        for component in address_components:
            types = component.get('types', [])
            if 'locality' in types:
                return component.get('long_name', '')
            elif 'administrative_area_level_2' in types and not any('locality' in comp.get('types', []) for comp in address_components):
                return component.get('long_name', '')

        # Fallback: extraction depuis l'adresse formatée
        formatted_address = place.get('formatted_address', '')
        if formatted_address:
            parts = formatted_address.split(', ')
            for part in parts:
                if part and not part.isdigit() and 'France' not in part:
                    # Exclure les codes postaux et le nom du pays
                    if not any(char.isdigit() for char in part) or len(part) > 5:
                        return part

        return ''

    def _extract_opening_hours(self, place: Dict) -> str:
        """
        Extrait les heures d'ouverture depuis les données Google Places

        Args:
            place: Données du lieu depuis l'API Google Places

        Returns:
            String formatée des heures d'ouverture
        """
        # Essayer d'abord les heures actuelles
        current_hours = place.get('currentOpeningHours', {})
        if current_hours:
            weekday_descriptions = current_hours.get('weekdayDescriptions', [])
            if weekday_descriptions:
                return '; '.join(weekday_descriptions)

        # Fallback sur les heures régulières
        regular_hours = place.get('regularOpeningHours', {})
        if regular_hours:
            weekday_descriptions = regular_hours.get('weekdayDescriptions', [])
            if weekday_descriptions:
                return '; '.join(weekday_descriptions)

        return 'Non disponible'

    def _extract_closure_days(self, place: Dict) -> int:
        """
        Calcule le nombre de jours de fermeture par semaine

        Args:
            place: Données du lieu depuis l'API Google Places

        Returns:
            Nombre de jours de fermeture (0-7)
        """
        # Essayer d'abord les heures actuelles
        current_hours = place.get('currentOpeningHours', {})
        if not current_hours:
            # Fallback sur les heures régulières
            current_hours = place.get('regularOpeningHours', {})

        if current_hours:
            periods = current_hours.get('periods', [])
            if periods:
                # Compter les jours où il n'y a pas de période d'ouverture
                open_days = set()
                for period in periods:
                    if 'open' in period:
                        day = period['open'].get('day', 0)
                        open_days.add(day)

                # Il y a 7 jours dans la semaine (0=Dimanche, 1=Lundi, ..., 6=Samedi)
                total_days = 7
                return total_days - len(open_days)

        return 0  # Par défaut, supposer ouvert tous les jours si pas d'info

def load_csv_column(filepath: str, column_name: str) -> List[str]:
    """
    Charge une colonne spécifique depuis un fichier CSV

    Args:
        filepath: Chemin vers le fichier CSV
        column_name: Nom de la colonne à extraire

    Returns:
        Liste des valeurs de la colonne
    """
    values = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                value = row.get(column_name, '').strip()
                if value:
                    values.append(value)
    except FileNotFoundError:
        print(f"Erreur: Fichier {filepath} non trouvé")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors de la lecture de {filepath}: {e}")
        sys.exit(1)

    return values

def save_results_to_csv(businesses: List[Dict], output_file: str):
    """
    Sauvegarde les résultats dans un fichier CSV

    Args:
        businesses: Liste des entreprises trouvées
        output_file: Chemin du fichier de sortie
    """
    fieldnames = ['Nom', 'Adresse', 'Ville', 'Metier', 'Heures_ouverture', 'Nombre_avis', 'Note', 'Jours_fermeture']

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(businesses)

        print(f"Résultats sauvegardés dans {output_file} ({len(businesses)} entreprises)")

    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Recherche d'entreprises via Google Places API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python recherche_entreprises.py metiers.csv villes.csv output.csv --api-key YOUR_API_KEY
  python recherche_entreprises.py metiers.csv villes.csv output.csv --api-key YOUR_API_KEY --max-per-search 10

Format des fichiers CSV d'entrée:
  metiers.csv: doit contenir une colonne 'Metier'
  villes.csv: doit contenir une colonne 'Ville'
        """
    )

    parser.add_argument('metiers_file', help='Fichier CSV contenant la liste des métiers (colonne: Metier)')
    parser.add_argument('villes_file', help='Fichier CSV contenant la liste des villes (colonne: Ville)')
    parser.add_argument('output_file', help='Fichier CSV de sortie')
    parser.add_argument('--api-key', required=True, help='Clé API Google Places')
    parser.add_argument('--max-per-search', type=int, default=20,
                       help='Nombre maximum de résultats par recherche (défaut: 20, maximum: 60 avec pagination)')
    parser.add_argument('--delay', type=float, default=0.1,
                       help='Délai entre les requêtes en secondes (défaut: 0.1)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Affichage détaillé des informations récupérées')

    args = parser.parse_args()

    # Validation du paramètre max-per-search
    if args.max_per_search > 60:
        print("⚠️  Avertissement: L'API Google Places limite à 60 résultats maximum avec pagination.")
        print(f"   Votre demande de {args.max_per_search} sera limitée à 60.")
        args.max_per_search = 60
    elif args.max_per_search > 20:
        print(f"ℹ️  Information: Utilisation de la pagination pour obtenir {args.max_per_search} résultats.")
        print("   (20 résultats par page, plusieurs requêtes seront effectuées)")

    # Chargement des données d'entrée
    print("Chargement des fichiers d'entrée...")
    metiers = load_csv_column(args.metiers_file, 'Metier')
    villes = load_csv_column(args.villes_file, 'Ville')

    print(f"Métiers chargés: {len(metiers)}")
    print(f"Villes chargées: {len(villes)}")

    if not metiers:
        print("Erreur: Aucun métier trouvé dans le fichier")
        sys.exit(1)

    if not villes:
        print("Erreur: Aucune ville trouvée dans le fichier")
        sys.exit(1)

    # Initialisation du chercheur Google Places
    searcher = GooglePlacesSearcher(args.api_key)

    # Test de la clé API avant de commencer
    if not searcher.test_api_key():
        print("\n❌ Impossible de continuer avec une clé API invalide")
        sys.exit(1)

    # Recherche des entreprises
    all_businesses = []
    total_searches = len(metiers) * len(villes)
    current_search = 0
    total_pagination_calls = 0

    print(f"\nDébut de la recherche ({total_searches} combinaisons métier/ville)...")

    for metier in metiers:
        for ville in villes:
            current_search += 1
            print(f"[{current_search}/{total_searches}] Recherche: {metier} à {ville}")

            businesses, pagination_count = searcher.search_businesses(metier, ville, args.max_per_search)
            all_businesses.extend(businesses)
            total_pagination_calls += pagination_count

            print(f"  Trouvé: {len(businesses)} entreprises")
            if pagination_count > 0:
                print(f"  📄 {pagination_count} page(s) suivante(s) utilisée(s)")

            # Affichage détaillé si mode verbose activé
            if args.verbose and businesses:
                for business in businesses:
                    print(f"    • {business.get('Nom', 'N/A')} - Note: {business.get('Note', 'N/A')}/5 ({business.get('Nombre_avis', 'N/A')} avis)")

            # Délai entre les requêtes pour respecter les limites de l'API
            if current_search < total_searches:
                time.sleep(args.delay)

    # Sauvegarde des résultats
    print(f"\nRecherche terminée. Total: {len(all_businesses)} entreprises trouvées")
    print(f"📊 Statistiques de pagination :")
    print(f"   • Total de pages suivantes utilisées : {total_pagination_calls}")
    print(f"   • Requêtes de pagination effectuées : {total_pagination_calls}")
    if total_pagination_calls > 0:
        print(f"   • Économie sans pagination : {len(all_businesses) - (total_searches * 20)} entreprises supplémentaires récupérées")

    save_results_to_csv(all_businesses, args.output_file)

if __name__ == "__main__":
    main()

# Exemples de fichiers CSV d'entrée:

# metiers.csv:
# Metier
# boulanger
# plombier
# restaurant
# pharmacie

# villes.csv:
# Ville
# Paris
# Lyon
# Marseille

# Utilisation:
# python recherche_entreprises.py metiers.csv villes.csv entreprises_trouvees.csv --api-key YOUR_GOOGLE_API_KEY

# Utilisation avec pagination (jusqu'à 60 résultats par recherche):
# python recherche_entreprises.py metiers.csv villes.csv entreprises_trouvees.csv --api-key YOUR_GOOGLE_API_KEY --max-per-search 40

# Structure du fichier de sortie:
# Nom,Adresse,Ville,Metier,Heures_ouverture,Nombre_avis,Note,Jours_fermeture
# Boulangerie Dupont,"12 rue de la Paix, 75001 Paris",Paris,boulanger,"lundi: 07:00-19:00; mardi: 07:00-19:00; ...",142,4.3,1