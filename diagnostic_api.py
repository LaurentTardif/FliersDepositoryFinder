#!/usr/bin/env python3
"""
Script de diagnostic pour l'API Google Places
Aide à identifier les problèmes de configuration de l'API
"""

import requests
import sys
import argparse

def test_google_places_api(api_key):
    """Test complet de la nouvelle API Google Places"""

    print("🔍 Diagnostic de la nouvelle API Google Places")
    print("=" * 50)

    base_url = "https://places.googleapis.com/v1/places:searchText"

    # Headers pour la nouvelle API
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.addressComponents'
    }

    # Test 1: Recherche textuelle simple avec la nouvelle API
    print("\n1️⃣ Test de recherche textuelle (nouvelle API)...")
    payload = {
        "textQuery": "restaurant Paris",
        "languageCode": "fr",
        "maxResultCount": 5
    }

    try:
        response = requests.post(base_url, json=payload, headers=headers)

        print(f"   Status HTTP: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            places = data.get('places', [])
            print(f"   ✅ Succès - {len(places)} résultats trouvés")
            if places:
                print(f"   Premier résultat: {places[0].get('displayName', {}).get('text', 'Nom non disponible')}")
        else:
            print(f"   ❌ Échec - Status HTTP: {response.status_code}")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"   Message d'erreur: {error_data['error'].get('message', 'Pas de détails')}")
            except:
                print(f"   Réponse brute: {response.text[:200]}")

    except Exception as e:
        print(f"   ❌ Erreur réseau: {e}")

    # Test 2: Vérification des quotas avec la nouvelle API
    print("\n2️⃣ Test de quota...")
    try:
        # Faire plusieurs requêtes pour tester les limites
        for i in range(3):
            response = requests.post(base_url, json=payload, headers=headers)

            if response.status_code == 429:
                print(f"   ⚠️  Quota dépassé à la requête {i+1}")
                break
            elif response.status_code == 200:
                print(f"   ✅ Requête {i+1} OK")
            else:
                print(f"   ❌ Requête {i+1} échouée: HTTP {response.status_code}")

    except Exception as e:
        print(f"   ❌ Erreur lors du test de quota: {e}")

    # Test 3: Informations sur la clé API
    print("\n3️⃣ Informations sur la clé API...")
    print(f"   Clé fournie: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else api_key}")
    print(f"   Longueur: {len(api_key)} caractères")

    # Test 4: URLs de vérification
    print("\n4️⃣ URLs utiles pour la configuration:")
    print("   • Console Google Cloud: https://console.cloud.google.com/")
    print("   • APIs activées: https://console.cloud.google.com/apis/dashboard")
    print("   • Clés API: https://console.cloud.google.com/apis/credentials")
    print("   • Quotas: https://console.cloud.google.com/apis/quotas")
    print("   • Facturation: https://console.cloud.google.com/billing")

    print("\n" + "=" * 50)
    print("Diagnostic terminé.")

def main():
    parser = argparse.ArgumentParser(description="Diagnostic de l'API Google Places")
    parser.add_argument('--api-key', required=True, help='Clé API Google Places à tester')

    args = parser.parse_args()

    if not args.api_key or args.api_key == 'YOUR_API_KEY_HERE':
        print("❌ Veuillez fournir une vraie clé API")
        print("Exemple: python diagnostic_api.py --api-key AIza...")
        sys.exit(1)

    test_google_places_api(args.api_key)

if __name__ == "__main__":
    main()