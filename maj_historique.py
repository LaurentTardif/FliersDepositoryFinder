#!/usr/bin/env python3
"""
Script de mise à jour de l'historique des entreprises
Compare un fichier historique avec des candidats à insérer/mettre à jour
"""

import csv
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Set, Tuple
import os

def normalize_for_comparison(text: str) -> str:
    """Normalise le texte pour la comparaison"""
    return text.strip().lower().replace('  ', ' ')

def create_composite_key(nom: str, adresse: str, ville: str, metier: str) -> str:
    """Crée une clé composite pour identifier uniquement une entreprise"""
    return f"{normalize_for_comparison(nom)}|{normalize_for_comparison(adresse)}|{normalize_for_comparison(ville)}|{normalize_for_comparison(metier)}"

def create_location_key(adresse: str, ville: str, metier: str) -> str:
    """Crée une clé basée sur l'adresse/ville/métier (sans le nom)"""
    return f"{normalize_for_comparison(adresse)}|{normalize_for_comparison(ville)}|{normalize_for_comparison(metier)}"

def load_historique(file_path: str) -> Tuple[Dict[str, Dict], Dict[str, List[Dict]], List[str]]:
    """
    Charge le fichier historique

    Returns:
        Tuple (dict_by_composite_key, dict_by_location_key, fieldnames)
    """
    historique_by_composite = {}
    historique_by_location = {}
    fieldnames = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Détection automatique des colonnes
            fieldnames = reader.fieldnames or []
            if not fieldnames:
                raise ValueError("Impossible de lire les colonnes du fichier historique")

            print(f"Colonnes détectées dans l'historique: {fieldnames}")

            # Vérification des colonnes minimales requises
            required_cols = {'Nom', 'Adresse', 'Ville'}
            available_cols = set(fieldnames)

            missing_cols = required_cols - available_cols
            if missing_cols:
                raise ValueError(f"Colonnes minimales manquantes dans l'historique: {missing_cols}")

            # Vérifier qu'on a au moins une colonne métier
            has_metier = 'Metier' in fieldnames
            has_metier_normalise = 'Metier_normalise' in fieldnames
            if not (has_metier or has_metier_normalise):
                raise ValueError("Aucune colonne 'Metier' ou 'Metier_normalise' trouvée dans l'historique")

            for row in reader:
                nom = row['Nom']
                adresse = row['Adresse']
                ville = row['Ville']
                metier = row.get('Metier_normalise', row.get('Metier', ''))

                # Clé composite complète (nom + adresse + ville + métier)
                composite_key = create_composite_key(nom, adresse, ville, metier)
                historique_by_composite[composite_key] = row

                # Clé par localisation (adresse + ville + métier, sans nom)
                location_key = create_location_key(adresse, ville, metier)
                if location_key not in historique_by_location:
                    historique_by_location[location_key] = []
                historique_by_location[location_key].append(row)

        return historique_by_composite, historique_by_location, fieldnames

    except FileNotFoundError:
        print(f"Erreur: Fichier historique '{file_path}' non trouvé")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors du chargement de l'historique: {e}")
        sys.exit(1)

def load_candidats(file_path: str) -> Tuple[List[Dict], List[str]]:
    """Charge le fichier des candidats à insérer"""
    candidats = []
    fieldnames = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Détection automatique des colonnes
            fieldnames = reader.fieldnames or []
            if not fieldnames:
                raise ValueError("Impossible de lire les colonnes du fichier candidats")

            print(f"Colonnes détectées dans les candidats: {fieldnames}")

            # Vérification des colonnes minimales requises
            required_cols = {'Nom', 'Adresse', 'Ville'}
            available_cols = set(fieldnames)

            missing_cols = required_cols - available_cols
            if missing_cols:
                raise ValueError(f"Colonnes minimales manquantes dans les candidats: {missing_cols}")

            # Vérifier qu'on a au moins une colonne métier
            has_metier = 'Metier' in fieldnames
            has_metier_normalise = 'Metier_normalise' in fieldnames
            if not (has_metier or has_metier_normalise):
                raise ValueError("Aucune colonne 'Metier' ou 'Metier_normalise' trouvée dans les candidats")

            # Lecture des candidats
            for row in reader:
                candidats.append(row)

        return candidats, fieldnames

    except FileNotFoundError:
        print(f"Erreur: Fichier candidats '{file_path}' non trouvé")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors du chargement des candidats: {e}")
        sys.exit(1)

def process_updates(historique_composite: Dict, historique_location: Dict,
                   candidats: List[Dict], candidats_fieldnames: List[str],
                   historique_fieldnames: List[str], verbose: bool = False) -> Tuple[List[Dict], List[Dict], List[str]]:
    """
    Traite les mises à jour

    Returns:
        Tuple (updated_historique, conflicts, output_fieldnames)
    """
    today = datetime.now().strftime('%Y-%m-%d')
    updated_historique = []
    conflicts = []
    stats = {
        'exact_matches': 0,
        'new_entries': 0,
        'conflicts': 0,
        'data_updates': 0
    }

    # Fusionner les colonnes de l'historique et des candidats
    # Commencer par toutes les colonnes sauf les colonnes de suivi
    tracking_fields = ['Date_introduction', 'Date_verification', 'Actif', 'Filtré']

    # Collecter toutes les colonnes non-suivi
    data_fieldnames = []
    for field in historique_fieldnames:
        if field not in tracking_fields and field not in data_fieldnames:
            data_fieldnames.append(field)

    for field in candidats_fieldnames:
        if field not in tracking_fields and field not in data_fieldnames:
            data_fieldnames.append(field)

    # Construire la liste finale : colonnes de données + colonnes de suivi dans l'ordre voulu
    # Ordre : [données, Date_introduction, Date_verification, Filtré, Actif]
    all_fieldnames = data_fieldnames + ['Date_introduction', 'Date_verification', 'Filtré', 'Actif']

    print(f"Colonnes dans le fichier de sortie: {all_fieldnames}")    # Copier l'historique existant en étendant avec les nouvelles colonnes
    for record in historique_composite.values():
        updated_record = {}
        for field in all_fieldnames:
            if field == 'Filtré' and field not in record:
                # Valeur par défaut pour la colonne Filtré si elle n'existe pas
                updated_record[field] = 'Non'
            else:
                updated_record[field] = record.get(field, '')
        updated_historique.append(updated_record)

    # Traiter chaque candidat
    for candidat in candidats:
        nom = candidat['Nom']
        adresse = candidat['Adresse']
        ville = candidat['Ville']
        metier = candidat.get('Metier_normalise', candidat.get('Metier', ''))

        # Clé composite complète
        composite_key = create_composite_key(nom, adresse, ville, metier)
        location_key = create_location_key(adresse, ville, metier)

        if composite_key in historique_composite:
            # Correspondance exacte : mettre à jour les données et date_verification
            for record in updated_historique:
                existing_key = create_composite_key(
                    record['Nom'],
                    record['Adresse'],
                    record['Ville'],
                    record.get('Metier_normalise', record.get('Metier', ''))
                )
                if existing_key == composite_key:
                    # Mettre à jour la date de vérification
                    record['Date_verification'] = today
                    stats['exact_matches'] += 1

                    # Vérifier et mettre à jour les nouvelles données
                    data_updated = False
                    for field in candidats_fieldnames:
                        candidat_value = candidat.get(field, '')
                        existing_value = record.get(field, '')

                        # Si le candidat a une valeur et l'historique n'en a pas ou a une valeur différente
                        if candidat_value and (not existing_value or existing_value != candidat_value):
                            if field not in ['Date_introduction', 'Date_verification', 'Actif']:  # Ne pas écraser les champs de suivi
                                record[field] = candidat_value
                                data_updated = True
                                if verbose:
                                    print(f"   📝 Mise à jour {field}: '{existing_value}' → '{candidat_value}'")

                    if data_updated:
                        stats['data_updates'] += 1

                    if verbose:
                        print(f"✅ Mis à jour: {nom} - {adresse}")
                    break

        elif location_key in historique_location:
            # Même adresse/ville/métier mais nom différent : conflit potentiel
            existing_entries = historique_location[location_key]
            for existing in existing_entries:
                if normalize_for_comparison(existing['Nom']) != normalize_for_comparison(nom):
                    conflict = {
                        'candidat': candidat,
                        'existant': existing
                    }
                    conflicts.append(conflict)
                    stats['conflicts'] += 1

                    print(f"⚠️  CONFLIT DÉTECTÉ:")
                    print(f"   Candidat: {nom} | {adresse} | {ville} | {metier}")
                    print(f"   Existant: {existing['Nom']} | {existing['Adresse']} | {existing['Ville']} | {existing.get('Metier_normalise', existing.get('Metier', ''))}")
                    print()
        else:
            # Nouvelle entrée
            new_entry = {}
            for field in all_fieldnames:
                new_entry[field] = candidat.get(field, '')

            # Ajouter les champs de suivi
            new_entry['Date_introduction'] = today
            new_entry['Date_verification'] = today
            new_entry['Actif'] = 'Oui'
            new_entry['Filtré'] = 'Non'  # Valeur par défaut pour les nouvelles entrées

            updated_historique.append(new_entry)
            stats['new_entries'] += 1
            if verbose:
                print(f"➕ Nouvelle entrée: {nom} - {adresse}")

    print(f"\n📊 Statistiques de traitement:")
    print(f"   Mises à jour (correspondances exactes): {stats['exact_matches']}")
    print(f"   Nouvelles entrées: {stats['new_entries']}")
    print(f"   Conflits détectés: {stats['conflicts']}")
    print(f"   🔄 Mises à jour de données: {stats['data_updates']}")

    return updated_historique, conflicts, all_fieldnames

def save_updated_historique(data: List[Dict], output_file: str, fieldnames: List[str]):
    """Sauvegarde l'historique mis à jour"""
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"✅ Historique mis à jour sauvegardé: {output_file} ({len(data)} entrées)")

    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Mise à jour de l'historique des entreprises",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Fonctionnement:
1. Détection automatique des colonnes dans les fichiers historique et candidats
2. Pour chaque candidat, vérifie s'il existe une correspondance exacte (nom/adresse/ville/métier)
   -> Si oui: met à jour la date_verification à aujourd'hui
   -> Ajoute/met à jour toutes les nouvelles informations disponibles (heures, notes, etc.)

3. Si pas de correspondance exacte, vérifie s'il existe une entrée avec même adresse/ville/métier
   -> Si oui avec nom différent: affiche un conflit à l'écran

4. Si aucune correspondance: ajoute comme nouvelle entrée avec toutes les colonnes

Nouvelles fonctionnalités:
- Support automatique de toutes les colonnes (Heures_ouverture, Nombre_avis, Note, etc.)
- Mise à jour des données existantes avec de nouvelles informations
- Compteur de mises à jour de données
- Suppression de la rétrocompatibilité avec l'ancien format

Exemples d'utilisation:
  python maj_historique.py historique.csv candidats.csv output.csv
  python maj_historique.py historique.csv candidats.csv output.csv --verbose
        """
    )

    parser.add_argument('historique_file', help='Fichier CSV historique (détection automatique des colonnes)')
    parser.add_argument('candidats_file', help='Fichier CSV des candidats (détection automatique des colonnes)')
    parser.add_argument('output_file', help='Fichier CSV de sortie mis à jour (toutes colonnes fusionnées)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Affichage détaillé des opérations')

    args = parser.parse_args()

    print(f"🔄 Mise à jour de l'historique...")
    print(f"   Historique: {args.historique_file}")
    print(f"   Candidats: {args.candidats_file}")
    print(f"   Sortie: {args.output_file}")

    # Chargement des données
    print(f"\n📖 Chargement des fichiers...")
    historique_composite, historique_location, historique_fieldnames = load_historique(args.historique_file)
    candidats, candidats_fieldnames = load_candidats(args.candidats_file)

    print(f"   Historique: {len(historique_composite)} entrées")
    print(f"   Candidats: {len(candidats)} entrées")

    # Traitement des mises à jour
    print(f"\n🔄 Traitement des mises à jour...")
    updated_historique, conflicts, output_fieldnames = process_updates(
        historique_composite, historique_location, candidats,
        candidats_fieldnames, historique_fieldnames, args.verbose
    )

    # Sauvegarde
    save_updated_historique(updated_historique, args.output_file, output_fieldnames)

    if conflicts:
        print(f"\n⚠️  {len(conflicts)} conflit(s) détecté(s) - vérification manuelle recommandée")

if __name__ == "__main__":
    main()

# Exemple de fichiers:
#
# historique.csv:
# Nom,Adresse,Ville,Metier_normalise,Date_introduction,Date_verification,Actif
# Jean Dupont,12 rue A,Paris,Boulanger_Patissdr ier,2024-01-01,2024-06-01,Oui
# Marie Martin,34 rue B,Lyon,Plombier,2024-02-01,2024-07-01,Oui
#
# candidats.csv:
# Nom,Adresse,Ville,Metier_normalise
# Jean Dupont,12 rue A,Paris,Boulanger_Patissier
# Pierre Durand,34 rue B,Lyon,Plombier
# Sophie Bernard,78 rue D,Toulouse,Enseignant